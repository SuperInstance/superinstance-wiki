"""WikiExporter — static site generation from wiki pages."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .page import WikiPage, WIKI_LINK_RE


@dataclass
class WikiExporter:
    """Exports wiki pages to static HTML files."""

    output_dir: str = "wiki-export"
    template: str = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — SuperInstance Wiki</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; color: #222; }}
a {{ color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
h1 {{ border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
.backlinks {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #eee; font-size: 0.9em; color: #666; }}
.tags {{ display: inline-block; background: #f1f8ff; color: #0366d6; padding: 2px 8px; border-radius: 3px; margin-right: 4px; font-size: 0.85em; }}
.meta {{ font-size: 0.85em; color: #888; }}
nav {{ margin-bottom: 2em; padding: 0.5em; background: #f6f8fa; border-radius: 4px; }}
nav a {{ margin-right: 1em; }}
pre {{ background: #f6f8fa; padding: 1em; border-radius: 4px; overflow-x: auto; }}
code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
</style>
</head>
<body>
<nav><a href="index.html">🏠 Index</a> <a href="recent.html">🕐 Recent</a></nav>
<h1>{title}</h1>
<div class="meta">Tags: {tags} · Word count: {word_count}</div>
<article>{body}</article>
{backlinks_section}
</body>
</html>"""
    backlinks_template: str = """<div class="backlinks"><strong>Backlinks:</strong> {links}</div>"""

    def _slug_to_filename(self, slug: str) -> str:
        """Convert a slug to an HTML filename."""
        return f"{slug}.html"

    def _resolve_link(
        self, slug_map: dict[str, str], target: str
    ) -> Optional[str]:
        """Resolve a wiki link target to a relative HTML path."""
        target_lower = target.lower().strip()
        for slug, title in slug_map.items():
            if title.lower() == target_lower or slug == target_lower:
                return self._slug_to_filename(slug)
        return None

    def _markdown_to_html(self, text: str, slug_map: dict[str, str]) -> str:
        """Convert basic markdown to HTML (intentionally simple)."""
        # Escape HTML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Wiki links → HTML links
        def _wiki_link(match: re.Match) -> str:
            target = match.group(1).strip()
            alias = match.group(2)
            display = alias.strip() if alias else target
            url = self._resolve_link(slug_map, target)
            if url:
                return f'<a href="{url}">{display}</a>'
            return f'<span class="broken-link">{display}</span>'

        text = WIKI_LINK_RE.sub(_wiki_link, text)

        # Code blocks (```...```)
        text = re.sub(
            r"```(\w*)\n(.*?)```",
            r'<pre><code>\2</code></pre>',
            text,
            flags=re.DOTALL,
        )
        # Inline code
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        # Headings
        for level in range(6, 0, -1):
            prefix = "#" * level
            text = re.sub(
                rf"^{prefix}\s+(.+)$",
                rf"<h{level}>\1</h{level}>",
                text,
                flags=re.MULTILINE,
            )
        # Links [text](url)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        # Paragraphs (double newline)
        blocks = re.split(r"\n{2,}", text)
        html_blocks = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            if block.startswith("<h") or block.startswith("<pre") or block.startswith("<ul") or block.startswith("<ol"):
                html_blocks.append(block)
            else:
                # Convert remaining newlines to <br>
                block = block.replace("\n", "<br>\n")
                html_blocks.append(f"<p>{block}</p>")
        return "\n".join(html_blocks)

    def export_page(
        self,
        page: WikiPage,
        slug_map: dict[str, str],
        backlinks: set[str],
    ) -> str:
        """Render a single page to HTML string."""
        body = self._markdown_to_html(page.content, slug_map)
        tags_html = " ".join(f'<span class="tags">{t}</span>' for t in page.tags) or "none"

        if backlinks:
            links_html = ", ".join(
                f'<a href="{self._slug_to_filename(page.slug)}">{title}</a>'
                for title in sorted(backlinks)
            )
            bl_section = self.backlinks_template.format(links=links_html)
        else:
            bl_section = ""

        return self.template.format(
            title=page.title,
            tags=tags_html,
            word_count=page.word_count(),
            body=body,
            backlinks_section=bl_section,
        )

    def export_all(
        self,
        pages: dict[str, WikiPage],
        backlinks_map: dict[str, set[str]],
    ) -> list[str]:
        """Export all pages. Returns list of written file paths."""
        os.makedirs(self.output_dir, exist_ok=True)
        slug_map = {page.slug: title for title, page in pages.items()}
        written = []

        # Export individual pages
        for title, page in pages.items():
            bl = backlinks_map.get(title, set())
            html = self.export_page(page, slug_map, bl)
            filepath = os.path.join(self.output_dir, self._slug_to_filename(page.slug))
            Path(filepath).write_text(html, encoding="utf-8")
            written.append(filepath)

        # Index page
        index_html = self._generate_index(pages, slug_map)
        index_path = os.path.join(self.output_dir, "index.html")
        Path(index_path).write_text(index_html, encoding="utf-8")
        written.append(index_path)

        # Recent page
        recent_html = self._generate_recent(pages, slug_map)
        recent_path = os.path.join(self.output_dir, "recent.html")
        Path(recent_path).write_text(recent_html, encoding="utf-8")
        written.append(recent_path)

        return written

    def _generate_index(self, pages: dict[str, WikiPage], slug_map: dict[str, str]) -> str:
        """Generate the index page listing all pages."""
        items = []
        for title in sorted(pages.keys()):
            page = pages[title]
            items.append(
                f'<li><a href="{self._slug_to_filename(page.slug)}">{title}</a>'
                f' — {page.excerpt(100)}</li>'
            )
        body = f"<h1>All Pages ({len(pages)})</h1><ul>{''.join(items)}</ul>"
        return self.template.format(
            title="Index",
            tags="",
            word_count="",
            body=body,
            backlinks_section="",
        )

    def _generate_recent(self, pages: dict[str, WikiPage], slug_map: dict[str, str]) -> str:
        """Generate a page listing recently updated pages."""
        sorted_pages = sorted(
            pages.values(),
            key=lambda p: p.updated_at or p.created_at,
            reverse=True,
        )
        items = []
        for page in sorted_pages[:20]:
            ts = (page.updated_at or page.created_at).strftime("%Y-%m-%d %H:%M")
            items.append(
                f'<li><a href="{self._slug_to_filename(page.slug)}">{page.title}</a>'
                f" — {ts}</li>"
            )
        body = f"<h1>Recent Changes</h1><ul>{''.join(items)}</ul>"
        return self.template.format(
            title="Recent",
            tags="",
            word_count="",
            body=body,
            backlinks_section="",
        )

    def __repr__(self) -> str:
        return f"WikiExporter(output_dir={self.output_dir!r})"
