import asyncio
import datetime
import enum
from typing import Optional
from sqlalchemy import DateTime, UniqueConstraint, select, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.dialects.sqlite import insert as upsert
from dotenv import load_dotenv
import os


if __name__ == "__main__":
    load_dotenv()

DB_PATH = os.environ.get("DB_PATH")

dbUrl = f"sqlite+aiosqlite:///{DB_PATH}"
engine = create_async_engine(
    dbUrl,
    # echo=True
)
start_session = async_sessionmaker(engine, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(conn, connection_record):
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()


class Base(DeclarativeBase):
    pass


class CacheScope(enum.Enum):
    SCHOLARLY_AUTHOR_FILLED = "scholarly-author-filled"
    SCHOLARLY_PUBLICATION_FILLED = "scholarly-publication-filled"
    SCHOLARLY_SEARCH_KEYWORDS = "scholarly-search-keywords"
    SCHOLARLY_SEARCH_PUBLICATIONS = "scholarly-search-publications"
    ANTHROPIC_PUBLICATION_SUMMARY = "anthropic-publication-summary"


class Cache(Base):
    __tablename__ = "cache"
    __table_args__ = (UniqueConstraint("key", "scope", name="uix_cache_key_scope"),)

    key: Mapped[str] = mapped_column()
    scope: Mapped[str] = mapped_column()
    content: Mapped[Optional[str]]
    ttl: Mapped[Optional[int]]  # Time to live in seconds
    inserted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda _: datetime.datetime.now(datetime.timezone.utc)
    )

    __mapper_args__ = {"primary_key": [key, scope]}  # Composite PK

    @classmethod
    async def set(
        cls,
        session: AsyncSession,
        scope: CacheScope,
        key: str,
        content: str,
        ttl: Optional[int | datetime.timedelta] = None,
    ):
        resolved_ttl = (
            (ttl if isinstance(ttl, int) else int(ttl.total_seconds())) if ttl else None
        )
        stmt = (
            upsert(cls)
            .values(
                scope=scope.value,
                key=key,
                content=content,
                ttl=resolved_ttl,
                inserted_at=datetime.datetime.now(datetime.timezone.utc),
            )
            .on_conflict_do_update(
                index_elements=[cls.scope, cls.key],
                set_=dict(
                    content=content,
                    ttl=resolved_ttl,
                ),
            )
            .returning(cls)
        )
        result = await session.execute(stmt)
        row = result.scalar_one()
        return row

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        scope: CacheScope,
        key: str,
    ):
        stmt = select(cls).where(cls.scope == scope.value, cls.key == key)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


# class AuthorDescription(Base):
#     __tablename__ = "author_description"
#     id: Mapped[str] = mapped_column(primary_key=True)
#     external_id: Mapped[str]
#     external_id_scope: Mapped[str]
#     generated_description: Mapped[str]
#     inserted_at: Mapped[datetime.datetime] = mapped_column(
#         DateTime, default=lambda _: datetime.datetime.now(datetime.timezone.utc)
#     )


async def migrator():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(migrator())
