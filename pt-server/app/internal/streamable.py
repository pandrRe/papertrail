"""
Streamable types for the papertrail streaming system.

This module contains the core streamable types used throughout the application
for server-sent events and real-time data streaming.
"""

from typing import Literal, NotRequired
from scholarly import Author, Publication
from .base_model import PtBaseModel


class ExtendedAuthor(Author):
    """Extended Author class with optional summary field."""

    summary: NotRequired[str | None]


class StreamSetAuthorList(PtBaseModel):
    type: Literal["set:author:list"] = "set:author:list"
    payload: list[ExtendedAuthor]


class StreamSetPublicationList(PtBaseModel):
    type: Literal["set:publication:list"] = "set:publication:list"
    payload: list[Publication]


class StreamUpdateAuthor(PtBaseModel):
    type: Literal["update:author"] = "update:author"
    payload: ExtendedAuthor


class StreamUpdatePublication(PtBaseModel):
    type: Literal["update:publication"] = "update:publication"
    payload: Publication


Streamable = (
    StreamSetAuthorList
    | StreamSetPublicationList
    | StreamUpdateAuthor
    | StreamUpdatePublication
)


class StreamPacket(PtBaseModel):
    stream_id: str
    content: Streamable
