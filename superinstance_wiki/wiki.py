"""Wiki — central class managing pages, search, links, and export."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .export import WikiExporter
from .link import LinkTracker
from .page import WikiPage
from .search import WikiSearch


@dataclass
class Wiki:
    """Central wiki engine managing pages, search, and link tracking."""

    pages: dict[str, WikiPage] = field(default_factory=dict)
    search_engine: WikiSearch = field(default_factory=WikiSearch)
    link_tracker: LinkTracker = field(default_factory=LinkTracker)
    exporter: WikiExporter = field(default_factory=WikiExporter)

    def add_page(self, page: WikiPage) -> WikiPage:
        """Add or update a page. Returns the page."""
        page.touch()
        self.pages[page.title] = page
        self._reindex()
        return page

    def get_page(self, title: str) -> Optional[WikiPage]:
        """Get a page by exact title."""
        return self.pages.get(title)

    def get_by_slug(self, slug: str) -> Optional[WikiPage]:
        """Get a page by its slug."""
        slug_lower = slug.lower()
        for page in self.pages.values():
            if page.slug == slug_lower:
                return page
        return None

    def remove_page(self, title: str) -> Optional[WikiPage]:
        """Remove a page by title. Returns the removed page or None."""
        page = self.pages.pop(title, None)
        if page:
            self._reindex()
        return page

    def rename_page(self, old_title: str, new_title: str) -> Optional[WikiPage]:
        """Rename a page, preserving its content and metadata."""
        page = self.pages.pop(old_title, None)
        if page is None:
            return None
        page.title = new_title
        page.touch()
        self.pages[new_title] = page
        self._reindex()
        return page

    def list_pages(self, sort_by: str = "title") -> list[WikiPage]:
        """List all pages. sort_by: 'title', 'updated', or 'created'."""
        pages = list(self.pages.values())
        if sort_by == "updated":
            pages.sort(key=lambda p: p.updated_at or p.created_at, reverse=True)
        elif sort_by == "created":
            pages.sort(key=lambda p: p.created_at, reverse=True)
        else:
            pages.sort(key=lambda p: p.title.lower())
        return pages

    def _reindex(self) -> None:
        """Rebuild search index and link graph from current pages."""
        self.search_engine.index(self.pages)
        # Rebuild link tracker
        self.link_tracker = LinkTracker()
        for title, page in self.pages.items():
            self.link_tracker.add_page(title, page.outgoing_links())

    def search(self, query: str, **kwargs) -> list:
        """Search pages. See WikiSearch.search for options."""
        return self.search_engine.search(query, **kwargs)

    def backlinks(self, title: str) -> set[str]:
        """Return titles of pages that link to the given page."""
        return self.link_tracker.get_backlinks(title)

    def orphans(self) -> set[str]:
        """Pages with no incoming links."""
        return self.link_tracker.get_orphans(set(self.pages.keys()))

    def broken_links(self) -> dict[str, set[str]]:
        """Links pointing to non-existent pages."""
        return self.link_tracker.get_broken_links(set(self.pages.keys()))

    def export(self, output_dir: Optional[str] = None) -> list[str]:
        """Export all pages to static HTML. Returns list of file paths."""
        if output_dir:
            self.exporter.output_dir = output_dir
        backlinks_map = {
            title: self.link_tracker.get_backlinks(title)
            for title in self.pages
        }
        return self.exporter.export_all(self.pages, backlinks_map)

    def save(self, path: str) -> None:
        """Save wiki to a JSON file."""
        data = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "pages": [p.to_dict() for p in self.pages.values()],
        }
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> "Wiki":
        """Load wiki from a JSON file."""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        wiki = cls()
        for page_data in raw.get("pages", []):
            page = WikiPage.from_dict(page_data)
            wiki.pages[page.title] = page
        wiki._reindex()
        return wiki

    def __len__(self) -> int:
        return len(self.pages)

    def __contains__(self, title: str) -> bool:
        return title in self.pages

    def __repr__(self) -> str:
        return f"Wiki(pages={len(self.pages)})"
