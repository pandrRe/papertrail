import asyncio
import json
import hashlib
import torch
import textwrap
import os
import time
import anthropic
from typing import AsyncGenerator, Optional
from scholarly import scholarly, Author, Publication
from scholarly.data_types import BibEntry
from itertools import islice
from pydantic import TypeAdapter
from sentence_transformers import SentenceTransformer
from ..internal.logger import logger
from ..internal.base_model import PtBaseModel
from ..internal.db import CacheScope, start_session, Cache
from ..internal.streamable import (
    ExtendedAuthor, 
    Streamable, 
    StreamSetAuthorList, 
    StreamSetPublicationList, 
    StreamUpdateAuthor, 
    StreamUpdatePublication
)

# Runtime patch of BibEntry to allow for list[str] for authors
BibEntry.__annotations__["author"] = str | list[str]


class GlobalSearchResult(PtBaseModel):
    authors: list[ExtendedAuthor]
    publications: list[Publication]


author_adapter = TypeAdapter(ExtendedAuthor)
publication_adapter = TypeAdapter(Publication)


def search_keywords_slice(keywords: list[str], slice_size: int = 10) -> list[Author]:
    logger.debug("Executing Google Scholar keyword search", 
                keywords=keywords, 
                slice_size=slice_size)
    result = scholarly.search_keywords(keywords)
    sliced = islice(result, slice_size)
    sliced = list(sliced)
    logger.debug("Google Scholar keyword search completed", 
                keywords=keywords,
                actual_results=len(sliced))
    return sliced


def search_publications_slice(query: str, slice_size: int = 10) -> list[Publication]:
    logger.debug("Executing Google Scholar publication search", 
                query=query, 
                slice_size=slice_size)
    result = scholarly.search_pubs(query)
    sliced = islice(result, slice_size)
    sliced = list(sliced)
    logger.debug("Google Scholar publication search completed", 
                query=query,
                actual_results=len(sliced))
    return sliced


async def wrapped_search_keywords(keywords: list[str], slice_size: int = 10):
    logger.debug("Starting keyword search", 
                keywords=keywords, 
                keyword_count=len(keywords),
                slice_size=slice_size)
    
    async with start_session() as session:
        cache_key = json.dumps(keywords)
        logger.debug("Checking cache for keywords", cache_key=cache_key)
        
        cached = await Cache.get(
            session, CacheScope.SCHOLARLY_SEARCH_KEYWORDS, cache_key
        )
        if cached:
            logger.info("Cache hit for keyword search", 
                       keywords=keywords,
                       cached_at=cached.inserted_at.isoformat() if cached.inserted_at else None)
            deser = json.loads(cached.content)
            validated = [
                author_adapter.validate_python({"summary": None} | author)
                for author in deser
            ]
            return StreamSetAuthorList(
                payload=validated,
            )
        
        logger.info("Cache miss for keyword search - fetching from Google Scholar",
                   keywords=keywords)
        
        start_time = time.time()
        result = await asyncio.to_thread(search_keywords_slice, keywords, slice_size)
        search_duration = time.time() - start_time
        
        logger.info("Keyword search completed", 
                   keywords=keywords,
                   result_count=len(result),
                   duration_seconds=round(search_duration, 2))
        
        await Cache.set(
            session,
            CacheScope.SCHOLARLY_SEARCH_KEYWORDS,
            cache_key,
            json.dumps(result),
        )
        await session.commit()
        
        logger.debug("Cached keyword search results", cache_key=cache_key)
        
        return StreamSetAuthorList(
            payload=result,
        )


async def wrapped_search_publications(query: str, slice_size: int = 10):
    async with start_session() as session:
        cached = await Cache.get(
            session, CacheScope.SCHOLARLY_SEARCH_PUBLICATIONS, query
        )
        if cached:
            deser = json.loads(cached.content)
            validated = [publication_adapter.validate_python(pub) for pub in deser]
            return StreamSetPublicationList(
                payload=validated,
            )
        result = await asyncio.to_thread(search_publications_slice, query, slice_size)
        await Cache.set(
            session,
            CacheScope.SCHOLARLY_SEARCH_PUBLICATIONS,
            query,
            json.dumps(result),
        )
        await session.commit()
        return StreamSetPublicationList(
            payload=result,
        )


MAX_PUBLICATIONS = 50
TOP_K_PUBLICATIONS = 10


def rank_publications_by_query(
    sentence_transformer: SentenceTransformer,
    query: str,
    publications: list[Publication],
):
    model = sentence_transformer
    query_embedding = model.encode(query, convert_to_tensor=True)

    publications_slice = publications[:MAX_PUBLICATIONS]
    corpus = [
        f"title: {publication.get('bib', {}).get('title', '')}. citation: {publication.get('bib', {}).get('citation', '')}"
        for publication in publications_slice
    ]
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    similarity_scores = model.similarity(query_embedding, corpus_embeddings)[0]
    scores, indices = torch.topk(similarity_scores, k=TOP_K_PUBLICATIONS)
    top_publications = []
    for score, index in zip(scores, indices):
        publication = publications[index]
        top_publications.append(publication)

    return top_publications


api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.AsyncAnthropic(api_key=api_key)


async def summarize_author_publications(author: Author, query: str) -> str:
    # Let's cache the summaries to not waste money.
    hash_content = f"{author['scholar_id']}:{query}"
    hashed = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()
    async with start_session() as session:
        cached = await Cache.get(
            session, CacheScope.ANTHROPIC_PUBLICATION_SUMMARY, hashed
        )
    if cached and cached.content:
        logger.debug(f"Cache hit for '{author['name']}':'{query}' - {hashed}")
        return cached.content

    logger.debug(f"Cache miss for '{author['name']}':'{query}' - {hashed}")
    if len(author["publications"]) > TOP_K_PUBLICATIONS:
        raise Exception(
            "Too many publications to summarize. First rank them using `rank_publications_by_query`."
        )

    publications = author["publications"]
    formatted_publications = []
    for pub in publications:
        bib = pub.get("bib", {})
        title = bib.get("title", "Untitled")
        venue = bib.get("citation", "Unknown venue")
        citations = pub.get("num_citations", 0)
        formatted_publications.append(
            f"- **{title}** ({venue}, cited {citations} times)"
        )
    input_text = "\n".join(formatted_publications)
    prompt = textwrap.dedent(
        f"""
        Write a small blurb about the author {author['name']}'s research based on two factors:

        1. The query: {query}
        2. The author's publications:
        {input_text}

        The blurb should be a short paragraph, no more than 70 words. Oh, write in Brazilian Portuguese.
        Do not make assertions on their influence on the subject such as "the author is a prominent figure in the field of..." or "the author is a renowned expert in..." or "the author is a prolific researcher in...".
        Similar avoidances in Portuguese are "o autor é uma figura prominente no campo de...", "o autor é um especialista em..." e "o autor é um pesquisador prolifico em...".
        Just go straight to a summary of the work, no opinions on the researcher themselves.

        An example of a good summary is:
        'Jeff Dean trabalha com inteligência artificial em larga escala, com foco em modelos de linguagem, redes neurais profundas e sistemas distribuídos para aprendizado de máquina.
        Seus trabalhos incluem a introdução do TensorFlow, o uso de distilação de conhecimento em redes neurais, e investigações sobre as habilidades emergentes de modelos de linguagem de grande porte.
        Também contribuiu com pesquisas sobre embeddings visuais e semânticos, aplicações de aprendizado de máquina na medicina e representação distribuída de palavras e frases.
        Sua produção aborda tanto aspectos teóricos quanto práticos de IA escalável.'

        Another one:
        'Yoesoep Edhie Rachmad desenvolve pesquisas sobre a integração da inteligência artificial com realidade virtual e aumentada em contextos de marketing digital,
        design inovador e estruturas sociais futuras. Seus trabalhos abordam estratégias para a excelência em marketing impulsionada por tecnologias emergentes,
        além de discutir aspectos éticos e colaborativos na era do Management 5.0. As publicações exploram o impacto dessas tecnologias na transformação das interações humanas,
        nas políticas públicas e na construção de sociedades digitais, com ênfase na coexistência entre avanços tecnológicos e valores humanos.'

        Also, do not speak anything else other than the summary.

        Summary:
        """
    )

    message = await client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=400,
        temperature=1,
        system="You are an expert assistant for summarizing research papers.",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    logger.debug(f"Got summary for '{author['name']}':'{query}' - {hashed}")
    summary = message.content[0].text.strip()
    async with start_session() as session:
        await Cache.set(
            session,
            CacheScope.ANTHROPIC_PUBLICATION_SUMMARY,
            hashed,
            summary,
        )
        await session.commit()

    return summary


async def fill_author(
    author: Author, query: str, sentence_transformer: SentenceTransformer
):
    async with start_session() as session:
        cached = await Cache.get(
            session, CacheScope.SCHOLARLY_AUTHOR_FILLED, author["scholar_id"]
        )
    if cached:
        validated = author_adapter.validate_json(cached.content)
        validated["publications"] = rank_publications_by_query(
            sentence_transformer, query, validated["publications"]
        )
        validated["summary"] = await summarize_author_publications(validated, query)
        return StreamUpdateAuthor(
            payload=validated,
        )

    result = await asyncio.to_thread(scholarly.fill, author)
    validated = author_adapter.validate_python({"summary": None} | result)
    validated["publications"] = rank_publications_by_query(
        sentence_transformer, query, validated["publications"]
    )
    validated["summary"] = await summarize_author_publications(validated, query)
    async with start_session() as session:
        await Cache.set(
            session,
            CacheScope.SCHOLARLY_AUTHOR_FILLED,
            author["scholar_id"],
            json.dumps(validated),
        )
        streamable = StreamUpdateAuthor(
            payload=validated,
        )
        await session.commit()
    return streamable


async def fill_publication(publication: Publication):
    async with start_session() as session:
        cached = await Cache.get(
            session,
            CacheScope.SCHOLARLY_PUBLICATION_FILLED,
            publication["url_scholarbib"],
        )
    if cached:
        validated = publication_adapter.validate_json(cached.content)
        return StreamUpdatePublication(
            payload=validated,
        )

    result = await asyncio.to_thread(scholarly.fill, publication)
    validated = publication_adapter.validate_python(result)
    async with start_session() as session:
        await Cache.set(
            session,
            CacheScope.SCHOLARLY_PUBLICATION_FILLED,
            publication["url_scholarbib"],
            json.dumps(validated),
        )
        streamable = StreamUpdatePublication(
            payload=validated,
        )
        await session.commit()
    return streamable


def global_search(query: str) -> GlobalSearchResult:
    """
    Search for a query in Google Scholar and return the results.
    Includes authors by keywords and publications.
    """
    logger.debug(f"Searching for query: {query}")
    keywords = query.split(" ")
    keyword_results = scholarly.search_keywords(keywords)
    publication_results = scholarly.search_pubs(query)

    keyword_result_slice = islice(keyword_results, 10)
    publication_result_slice = islice(publication_results, 10)

    return GlobalSearchResult(
        authors=list(keyword_result_slice),
        publications=list(publication_result_slice),
    )


async def global_search_stream(
    query: str, sentence_transformer: SentenceTransformer
) -> AsyncGenerator[Streamable, None]:
    """
    Search for a query in Google Scholar and streams the results.
    Includes authors by keywords and publications.
    """
    logger.info("Starting global search stream", 
               query=query, 
               query_length=len(query))
    
    keywords = query.split(",")
    logger.debug("Parsed search keywords", 
                original_query=query,
                keywords=keywords,
                keyword_count=len(keywords))

    # Phase 1: Initial search with individual error handling
    loading_authors = asyncio.create_task(wrapped_search_keywords(keywords))
    loading_publications = asyncio.create_task(wrapped_search_publications(query))
    initial_tasks = [loading_authors, loading_publications]

    authors = None
    publications = None

    logger.debug("Initial search tasks created", 
                task_count=len(initial_tasks),
                task_types=["authors", "publications"])
    try:
        # Stream initial results as they complete, handling individual failures
        for result in asyncio.as_completed(initial_tasks, timeout=30.0):
            try:
                resolved_result = await result
                yield resolved_result

                # Track which result we got for later use
                if isinstance(resolved_result, StreamSetAuthorList):
                    authors = resolved_result
                elif isinstance(resolved_result, StreamSetPublicationList):
                    publications = resolved_result

            except Exception as e:
                print(e)
                logger.error(f"Initial search task failed: {e}")
                # Continue with other tasks - don't break the stream

        # Phase 2: Fill details with individual error handling
        fill_tasks: list[asyncio.Task[Streamable]] = []

        try:
            # Only create fill tasks for successful initial searches
            if authors:
                for author in authors.payload:
                    fill_tasks.append(
                        asyncio.create_task(
                            fill_author(author, query, sentence_transformer)
                        )
                    )
            if publications:
                for publication in publications.payload:
                    fill_tasks.append(
                        asyncio.create_task(fill_publication(publication))
                    )

            # Stream fill results as they complete, handling individual failures
            for filled in asyncio.as_completed(fill_tasks, timeout=60.0):
                try:
                    resolved = await filled
                    yield resolved
                except Exception as e:
                    logger.error(f"Fill task failed: {e}")
                    # Continue with other tasks - don't break the stream

        finally:
            # Always cancel any remaining fill tasks on generator cleanup
            for task in fill_tasks:
                if not task.done():
                    task.cancel()

            # Wait for cancellation to complete, ignoring exceptions
            if fill_tasks:
                await asyncio.gather(*fill_tasks, return_exceptions=True)

    except asyncio.TimeoutError:
        logger.error(f"Search timed out for query: {query}")
        # Don't re-raise - let partial results through
    except Exception as e:
        logger.error(f"Unexpected error in search for query '{query}': {e}")
        # Don't re-raise - let partial results through
    finally:
        # Always cancel any remaining initial tasks on generator cleanup
        for task in initial_tasks:
            if not task.done():
                task.cancel()

        # Wait for cancellation to complete, ignoring exceptions
        await asyncio.gather(*initial_tasks, return_exceptions=True)
