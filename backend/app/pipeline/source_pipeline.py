import hashlib
import logging
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.source import DatasetEntity, ModelEntity, Paper, Repository, Source
from app.tools.base import RawSourceResult
from app.tools.sanitizer import sanitize_text
from app.tools.ssrf import validate_url_safe

logger = logging.getLogger(__name__)


def compute_canonical_url(url: str) -> str:
    """Normalize URL by stripping fragments, sorting query params, and lowercasing host."""
    parsed = urlparse(url)
    # Filter common tracking params
    filtered_query = [
        (k, v)
        for k, v in parse_qsl(parsed.query)
        if not k.startswith("utm_") and k not in ("fbclid", "gclid", "ref")
    ]
    filtered_query.sort()
    canonical_query = urlencode(filtered_query)

    canonical_parts = (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/") or "/",
        parsed.params,
        canonical_query,
        "",  # No fragment
    )
    return urlunparse(canonical_parts)


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SourcePipeline:
    def __init__(self, db: AsyncSession, project_id: str, run_id: Optional[str] = None):
        self.db = db
        self.project_id = project_id
        self.run_id = run_id

    async def process_and_store(
        self, raw_results: List[RawSourceResult], max_sources: int = 60
    ) -> List[Source]:
        saved_sources: List[Source] = []
        seen_canonical: set = set()
        seen_hashes: set = set()

        # Fetch existing canonical URLs for this project
        stmt = select(Source.canonical_url, Source.content_hash).where(
            Source.project_id == self.project_id
        )
        existing = await self.db.execute(stmt)
        for c_url, c_hash in existing.all():
            seen_canonical.add(c_url)
            seen_hashes.add(c_hash)

        for raw in raw_results:
            if len(saved_sources) >= max_sources:
                break

            # 1. SSRF and URL Safety
            is_safe, clean_url = validate_url_safe(raw.url)
            if not is_safe:
                logger.warning("Dropped unsafe source URL: %s (%s)", raw.url, clean_url)
                continue

            canonical_url = compute_canonical_url(clean_url)
            if canonical_url in seen_canonical:
                continue

            # 2. Sanitize and check injection
            sanitized_content, is_injected, _ = sanitize_text(raw.content or raw.snippet or raw.title)
            content_hash = compute_content_hash(sanitized_content)
            if content_hash in seen_hashes and len(sanitized_content) > 50:
                continue

            # 3. Create Source Entity
            source = Source(
                project_id=self.project_id,
                run_id=self.run_id,
                title=raw.title[:500],
                url=clean_url,
                canonical_url=canonical_url,
                source_type=raw.source_type,
                author=raw.author,
                published_date=raw.published_date,
                publisher=raw.publisher,
                content=sanitized_content,
                snippet=(raw.snippet or sanitized_content[:300])[:1000],
                license=raw.license,
                relevance_note=raw.relevance_note,
                content_hash=content_hash,
            )
            self.db.add(source)
            await self.db.flush()

            # 4. Create Typed Detail Tables
            meta = raw.extra_metadata or {}
            if raw.source_type == "paper":
                paper = Paper(
                    source_id=source.id,
                    external_id=meta.get("external_id"),
                    venue=meta.get("venue"),
                    year=meta.get("year"),
                    citation_count=meta.get("citation_count", 0),
                    abstract=meta.get("abstract", sanitized_content),
                    authors=meta.get("authors", []),
                    open_access_url=meta.get("open_access_url"),
                )
                self.db.add(paper)
            elif raw.source_type == "repository":
                repo = Repository(
                    source_id=source.id,
                    full_name=meta.get("full_name", raw.title),
                    description=meta.get("description"),
                    language=meta.get("language"),
                    stars=meta.get("stars", 0),
                    forks=meta.get("forks", 0),
                    license=meta.get("license", raw.license),
                    topics=meta.get("topics", []),
                    readme_summary=meta.get("readme_summary"),
                    archived=meta.get("archived", False),
                )
                self.db.add(repo)
            elif raw.source_type == "model":
                model_item = ModelEntity(
                    source_id=source.id,
                    hub_id=meta.get("hub_id", raw.title),
                    task=meta.get("task"),
                    license=meta.get("license", raw.license),
                    params=meta.get("params"),
                    downloads=meta.get("downloads", 0),
                    notes=meta.get("notes"),
                )
                self.db.add(model_item)
            elif raw.source_type == "dataset":
                ds_item = DatasetEntity(
                    source_id=source.id,
                    hub_id=meta.get("hub_id", raw.title),
                    license=meta.get("license", raw.license),
                    size_note=meta.get("size_note"),
                    modality=meta.get("modality", "Multimodal"),
                    access_note=meta.get("access_note"),
                )
                self.db.add(ds_item)

            seen_canonical.add(canonical_url)
            seen_hashes.add(content_hash)
            saved_sources.append(source)

        await self.db.commit()
        return saved_sources
