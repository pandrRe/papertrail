from .base_model import PtBaseModel
from datetime import date
from typing import List

# ENTITIES


class AuthorIds(PtBaseModel):
    orcid: str | None
    openalex: str | None
    scopus: str | None
    twitter: str | None
    wikipedia: str | None
    scholar: str | None


class Author(PtBaseModel):
    ids: AuthorIds
    institution: str | None


# OpenAlex Work API Result Models


class OpenAlexIds(PtBaseModel):
    openalex: str | None
    doi: str | None
    mag: int | None
    pmid: str | None
    pmcid: str | None


class OpenAlexAuthor(PtBaseModel):
    id: str | None
    display_name: str | None
    orcid: str | None


class OpenAlexInstitution(PtBaseModel):
    id: str | None
    display_name: str | None
    ror: str | None
    country_code: str | None
    type: str | None
    lineage: List[str] | None


class OpenAlexAuthorship(PtBaseModel):
    author_position: str | None
    is_corresponding: bool | None
    raw_author_name: str | None
    raw_affiliation_strings: List[str] | None
    author: OpenAlexAuthor | None
    institutions: List[OpenAlexInstitution] | None
    countries: List[str] | None


class OpenAlexSource(PtBaseModel):
    id: str | None
    display_name: str | None
    issn_l: str | None
    issn: List[str] | None
    is_oa: bool | None
    is_in_doaj: bool | None
    is_indexed_in_scopus: bool | None
    is_core: bool | None
    host_organization: str | None
    host_organization_name: str | None
    host_organization_lineage: List[str] | None
    host_organization_lineage_names: List[str] | None
    type: str | None


class OpenAlexOpenAccess(PtBaseModel):
    is_oa: bool | None
    oa_status: str | None  # gold, green, hybrid, bronze, closed, diamond
    oa_url: str | None
    any_repository_has_fulltext: bool | None


class OpenAlexPrimaryLocation(PtBaseModel):
    is_oa: bool | None
    landing_page_url: str | None
    pdf_url: str | None
    license: str | None
    license_id: str | None
    version: str | None
    is_accepted: bool | None
    is_published: bool | None
    source: OpenAlexSource | None


class OpenAlexWorkApiResult(PtBaseModel):
    id: str | None
    doi: str | None
    title: str | None
    display_name: str | None
    relevance_score: float | None
    publication_year: int | None
    publication_date: date | None
    ids: OpenAlexIds | None
    language: str | None
    primary_location: OpenAlexPrimaryLocation | None
    type: str | None
    type_crossref: str | None
    indexed_in: List[str] | None
    open_access: OpenAlexOpenAccess | None
    authorships: List[OpenAlexAuthorship] | None


class WorkSummary(PtBaseModel):
    display_name: str | None
    publication_date: date | None
    doi: str | None
    type: str | None
    authorships: List[OpenAlexAuthor] | None
    url: str | None


class AuthorAffiliation(PtBaseModel):
    institution_id: str | None
    institution_name: str | None
    years: List[int] | None


class AuthorWorksResult(PtBaseModel):
    id: str
    work_count: int
    works: List[WorkSummary]
    author_score: float
    affiliations: List[AuthorAffiliation]
