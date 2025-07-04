from datetime import date, datetime
from typing import Literal, Optional
import xml.etree.ElementTree as ET

from pydantic import AnyUrl, Field, field_serializer
from app.internal.base_model import PtBaseModel
import httpx

BASE_ARXIV_OAI_URL = "https://oaipmh.arxiv.org/oai"


class ArxivHarvesterParams(PtBaseModel):
    verb: Optional[
        Literal[
            "Identify",
            "ListMetadataFormats",
            "ListSets",
            "GetRecord",
            "ListIdentifiers",
            "ListRecords",
        ]
    ] = None
    identifier: Optional[str] = None
    metadataPrefix: Optional[str] = None
    from_: Optional[datetime] = Field(default=None, alias="from")
    until: Optional[datetime] = None
    set: Optional[str] = None
    resumptionToken: Optional[str] = None

    @field_serializer("from_", "until")
    def serialize_datetime(v: datetime) -> str:
        return v.strftime("%Y-%m-%d")


class ArxivHeaderType(PtBaseModel):
    identifier: AnyUrl
    datestamp: datetime
    setSpec: Optional[list[str]] = None
    status: Optional[Literal["deleted"]] = None


class ArxivAuthor(PtBaseModel):
    keyname: str  # The keyname (often the surname)
    forenames: Optional[str] = None  # Forenames (given names)
    suffix: Optional[str] = None  # Suffix (e.g., Jr, II, etc.)
    affiliation: Optional[list[str]] = None  # Affiliations (can be multiple)


class ArxivAuthors(PtBaseModel):
    author: list[ArxivAuthor]


class ArxivMetadataType(PtBaseModel):
    id: str  # Unique identifier (required field)
    created: Optional[date] = None  # Date of creation (e.g., submission date)
    updated: Optional[date] = None  # Date of the latest update
    authors: Optional[ArxivAuthors] = None  # List of authors (can be empty)
    title: Optional[str] = None  # Title of the work
    msc_class: Optional[str] = Field(None, alias="msc-class")
    acm_class: Optional[str] = Field(None, alias="acm-class")
    report_no: Optional[str] = Field(None, alias="report-no")
    journal_ref: Optional[str] = Field(None, alias="journal-ref")
    comments: Optional[str] = None  # Comments or notes
    abstract: Optional[str] = None  # Abstract or summary of the work
    categories: Optional[str] = None  # Categories under which the work is classified
    doi: Optional[str] = None  # DOI (Digital Object Identifier)
    proxy: Optional[str] = None  # Proxy information (optional)
    license: Optional[str] = None  # License under which the work is published


class ArxivAboutType(PtBaseModel):
    pass


class ArxivRecordType(PtBaseModel):
    header: ArxivHeaderType
    metadata: Optional[ArxivMetadataType] = None
    # about: Optional[list[ArxivAboutType]] = None


def request_to_arxiv(params: ArxivHarvesterParams) -> ET.Element:
    with httpx.Client() as client:
        response = client.get(
            BASE_ARXIV_OAI_URL,
            params=params.model_dump(exclude_none=True, by_alias=True),
        )
    print(response.url)
    root = ET.fromstring(response.content)
    return root


ns = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


if __name__ == "__main__":
    root = request_to_arxiv(
        ArxivHarvesterParams(
            verb="ListRecords",
            metadataPrefix="oai_dc",
            from_=datetime(2025, 5, 6),
            until=datetime(2025, 5, 7),
        )
    )
    records = root.findall(".//oai:record", ns)
    for record in records[:2]:
        print(record)
    # TODO: transform the records into Pydantic models
