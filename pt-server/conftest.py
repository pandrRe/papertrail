"""
Pytest configuration and shared fixtures for pt-server tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from scholarly import Author, Publication
from app.internal.streamable import ExtendedAuthor, StreamSetAuthorList, StreamSetPublicationList


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_author() -> Author:
    """Create a mock Author object for testing."""
    return Author({
        'name': 'John Doe',
        'scholar_id': 'ABC123',
        'affiliation': 'Test University',
        'email_domain': 'test.edu',
        'url_picture': 'https://example.com/picture.jpg',
        'citedby': 1500,
        'publications': []
    })


@pytest.fixture
def mock_extended_author() -> ExtendedAuthor:
    """Create a mock ExtendedAuthor object for testing."""
    return ExtendedAuthor({
        'name': 'Jane Smith',
        'scholar_id': 'XYZ789',
        'affiliation': 'Research Institute',
        'email_domain': 'research.org',
        'url_picture': 'https://example.com/jane.jpg',
        'citedby': 2500,
        'publications': [],
        'summary': 'A researcher working on machine learning applications.'
    })


@pytest.fixture
def mock_publication() -> Publication:
    """Create a mock Publication object for testing."""
    return Publication({
        'container_type': 'journal',
        'source': 'scholar',
        'bib': {
            'title': 'Test Publication',
            'author': ['John Doe', 'Jane Smith'],
            'pub_year': '2023',
            'venue': 'Journal of Test Research',
            'citation': 'Doe, J., & Smith, J. (2023). Test Publication. Journal of Test Research.'
        },
        'filled': False,
        'gsrank': 1,
        'pub_url': 'https://example.com/paper',
        'author_id': ['ABC123', 'XYZ789'],
        'url_scholarbib': 'https://scholar.google.com/citations?hl=en&user=ABC123',
        'num_citations': 42
    })


@pytest.fixture
def mock_author_list() -> list[Author]:
    """Create a list of mock authors for testing."""
    return [
        Author({
            'name': f'Author {i}',
            'scholar_id': f'ID{i:03d}',
            'affiliation': f'University {i}',
            'citedby': 100 * i,
            'publications': []
        })
        for i in range(1, 6)
    ]


@pytest.fixture
def mock_publication_list() -> list[Publication]:
    """Create a list of mock publications for testing."""
    return [
        Publication({
            'container_type': 'journal',
            'source': 'scholar',
            'bib': {
                'title': f'Publication {i}',
                'author': [f'Author {i}'],
                'pub_year': str(2020 + i),
                'venue': f'Journal {i}',
            },
            'filled': False,
            'gsrank': i,
            'num_citations': 10 * i
        })
        for i in range(1, 6)
    ]


@pytest.fixture
def mock_sentence_transformer():
    """Create a mock SentenceTransformer for testing."""
    mock = MagicMock()
    mock.encode.return_value = MagicMock()
    mock.similarity.return_value = [[0.9, 0.8, 0.7, 0.6, 0.5]]
    return mock


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    mock = AsyncMock()
    mock_response = AsyncMock()
    mock_response.content = [MagicMock(text="Test summary in Portuguese")]
    mock.messages.create = AsyncMock(return_value=mock_response)
    return mock


@pytest.fixture
def sample_stream_set_author_list(mock_author_list) -> StreamSetAuthorList:
    """Create a sample StreamSetAuthorList for testing."""
    return StreamSetAuthorList(payload=mock_author_list)


@pytest.fixture
def sample_stream_set_publication_list(mock_publication_list) -> StreamSetPublicationList:
    """Create a sample StreamSetPublicationList for testing."""
    return StreamSetPublicationList(payload=mock_publication_list)