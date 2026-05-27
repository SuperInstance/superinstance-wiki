"""WikiSearch — full-text and title search over wiki pages."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from .page import WikiPage


@dataclass
class SearchResult:
    """A single search result with relevance score."""

    page: WikiPage
    score: float
    match_type: str  # "title_exact", "title_partial", "tag", "content"
    snippet: str = ""


@dataclass
class WikiSearch:
    """Search engine for wiki pages."""

    pages: dict[str, WikiPage] = field(default_factory=dict)

    def index(self, pages: dict[str, WikiPage]) -> None:
        """Set or replace the page index."""
        self.pages = dict(pages)

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        include_content: bool = True,
        min_score: float = 0.0,
        tag_filter: Optional[list[str]] = None,
    ) -> list[SearchResult]:
        """Search pages by query string. Returns results sorted by score descending."""
        results: list[SearchResult] = []
        query_lower = query.lower().strip()
        query_words = re.findall(r"\w+", query_lower)

        if not query_lower:
            return results

        for title, page in self.pages.items():
            if tag_filter and not any(t in page.tags for t in tag_filter):
                continue

            score = 0.0
            match_type = "content"
            snippet = ""

            title_lower = page.title.lower()

            # Exact title match
            if query_lower == title_lower:
                score = 10.0
                match_type = "title_exact"
            # Title starts with query
            elif title_lower.startswith(query_lower):
                score = 7.0
                match_type = "title_partial"
            # Title contains query
            elif query_lower in title_lower:
                score = 5.0
                match_type = "title_partial"
            # Tag match
            elif any(query_lower == t.lower() for t in page.tags):
                score = 4.0
                match_type = "tag"

            # Content match (only if no title/tag match or supplementing)
            if include_content:
                content_lower = page.content.lower()
                # Count word occurrences
                word_hits = sum(
                    content_lower.count(w) for w in query_words if w in content_lower
                )
                if word_hits > 0:
                    content_score = min(word_hits * 0.5, 3.0)
                    if score == 0.0:
                        match_type = "content"
                    score += content_score
                    # Extract snippet around first match
                    snippet = self._extract_snippet(page.content, query_words)

            if score >= min_score and score > 0:
                results.append(
                    SearchResult(
                        page=page,
                        score=round(score, 2),
                        match_type=match_type,
                        snippet=snippet,
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def search_titles(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        """Search only page titles."""
        return self.search(query, limit=limit, include_content=False)

    def search_by_tag(self, tag: str) -> list[WikiPage]:
        """Return all pages matching a tag."""
        tag_lower = tag.lower()
        return [
            p for p in self.pages.values()
            if any(t.lower() == tag_lower for t in p.tags)
        ]

    def recent(self, limit: int = 10) -> list[WikiPage]:
        """Return most recently updated pages."""
        pages = list(self.pages.values())
        pages.sort(
            key=lambda p: p.updated_at or p.created_at,
            reverse=True,
        )
        return pages[:limit]

    def _extract_snippet(self, content: str, query_words: list[str]) -> str:
        """Extract a short snippet around the first query word match."""
        content_lower = content.lower()
        best_pos = len(content)
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < best_pos:
                best_pos = pos

        if best_pos == len(content):
            return ""

        start = max(0, best_pos - 40)
        end = min(len(content), best_pos + 80)
        snippet = content[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet

    def __repr__(self) -> str:
        return f"WikiSearch(indexed_pages={len(self.pages)})"
