from .base_model import PtBaseModel

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
