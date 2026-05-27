"""LinkTracker — builds and queries the link graph between wiki pages."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LinkTracker:
    """Tracks forward links, backlinks, and the full link graph."""

    # forward_links[A] = {B, C} means A links to B and C
    forward_links: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    # backlinks[B] = {A, C} means A and C link to B
    backlinks: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def add_page(self, title: str, outgoing: list[str]) -> None:
        """Register a page's outgoing links. Removes stale links first."""
        # Clean up old forward links for this page
        old_targets = self.forward_links.get(title, set())
        for target in old_targets:
            self.backlinks[target].discard(title)
            if not self.backlinks[target]:
                del self.backlinks[target]

        # Set new forward links
        new_targets = set(outgoing)
        self.forward_links[title] = new_targets
        for target in new_targets:
            self.backlinks[target].add(title)

    def remove_page(self, title: str) -> None:
        """Remove all link references for a page."""
        for target in self.forward_links.pop(title, set()):
            self.backlinks[target].discard(title)
            if not self.backlinks.get(target):
                self.backlinks.pop(target, None)
        # Also remove from other pages' backlinks
        for source in self.backlinks.pop(title, set()):
            self.forward_links[source].discard(title)

    def get_backlinks(self, title: str) -> set[str]:
        """Return titles of pages that link to the given page."""
        return set(self.backlinks.get(title, set()))

    def get_forward_links(self, title: str) -> set[str]:
        """Return titles that the given page links to."""
        return set(self.forward_links.get(title, set()))

    def get_orphans(self, all_titles: set[str]) -> set[str]:
        """Return pages with no backlinks (nobody links to them)."""
        return all_titles - set(self.backlinks.keys())

    def get_dead_ends(self, all_titles: set[str]) -> set[str]:
        """Return pages with no forward links."""
        return all_titles - set(self.forward_links.keys())

    def get_broken_links(self, all_titles: set[str]) -> dict[str, set[str]]:
        """Return {source: {missing_targets}} for links pointing to non-existent pages."""
        broken: dict[str, set[str]] = {}
        for source, targets in self.forward_links.items():
            missing = targets - all_titles
            if missing:
                broken[source] = missing
        return broken

    def shortest_path(self, source: str, target: str) -> Optional[list[str]]:
        """BFS shortest path from source to target via forward links. None if unreachable."""
        if source == target:
            return [source]
        visited = {source}
        queue: list[list[str]] = [[source]]
        while queue:
            path = queue.pop(0)
            current = path[-1]
            for neighbor in self.forward_links.get(current, set()):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def get_strongly_connected_titles(self, all_titles: set[str]) -> set[str]:
        """Return titles that both link out and are linked to (bidirectionally connected)."""
        return set(self.forward_links.keys()) & set(self.backlinks.keys()) & all_titles

    def link_count(self) -> int:
        """Total number of individual links."""
        return sum(len(targets) for targets in self.forward_links.values())

    def page_count(self) -> int:
        """Number of pages that have at least one outgoing link."""
        return len(self.forward_links)

    def stats(self) -> dict:
        """Return summary statistics."""
        return {
            "pages_with_links": self.page_count(),
            "total_links": self.link_count(),
            "pages_linked_to": len(self.backlinks),
            "avg_links_per_page": (
                self.link_count() / self.page_count() if self.page_count() else 0
            ),
        }

    def __repr__(self) -> str:
        return f"LinkTracker(pages={self.page_count()}, links={self.link_count()})"
