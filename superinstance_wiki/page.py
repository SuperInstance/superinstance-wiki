"""WikiPage — a single wiki page with markdown content, metadata, and links."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# Regex for [[wiki links]]
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
# Regex for markdown headings
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass
class WikiPage:
    """Represents a single wiki page."""

    title: str
    content: str = ""
    tags: list[str] = field(default_factory=list)
    page_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    @property
    def slug(self) -> str:
        """URL-friendly slug derived from the title."""
        slug = self.title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        return slug.strip("-")

    def outgoing_links(self) -> list[str]:
        """Return a list of page titles this page links to via [[wiki links]]."""
        return [match.group(1).strip() for match in WIKI_LINK_RE.finditer(self.content)]

    def outgoing_links_with_aliases(self) -> list[tuple[str, Optional[str]]]:
        """Return (target, alias) pairs for all wiki links."""
        results = []
        for match in WIKI_LINK_RE.finditer(self.content):
            target = match.group(1).strip()
            alias = match.group(2)
            if alias:
                alias = alias.strip()
            results.append((target, alias))
        return results

    def headings(self) -> list[tuple[int, str]]:
        """Return (level, text) pairs for all markdown headings."""
        return [
            (len(match.group(1)), match.group(2).strip())
            for match in HEADING_RE.finditer(self.content)
        ]

    def excerpt(self, max_length: int = 200) -> str:
        """Return a plain-text excerpt of the content."""
        text = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", r"\2\1", self.content)
        text = re.sub(r"^[#]+\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"[*_`~]", "", text)
        text = re.sub(r"\n{2,}", "\n", text).strip()
        if len(text) > max_length:
            return text[: max_length - 3] + "..."
        return text

    def word_count(self) -> int:
        """Return the approximate word count."""
        return len(self.content.split())

    def touch(self) -> None:
        """Mark the page as updated now."""
        self.updated_at = datetime.now(timezone.utc)

    def render_links(self, resolver: "callable") -> str:
        """Render wiki links using a resolver function (title -> URL or None)."""
        def _replace(match: re.Match) -> str:
            target = match.group(1).strip()
            alias = match.group(2)
            display = alias.strip() if alias else target
            url = resolver(target)
            if url:
                return f"[{display}]({url})"
            return display
        return WIKI_LINK_RE.sub(_replace, self.content)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "page_id": self.page_id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": dict(self.metadata),
            "word_count": self.word_count(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WikiPage":
        """Deserialize from a dictionary."""
        data = dict(data)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def __repr__(self) -> str:
        return f"WikiPage(title={self.title!r}, slug={self.slug!r})"
