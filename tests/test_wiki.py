"""Tests for superinstance_wiki."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from superinstance_wiki import Wiki, WikiPage, WikiSearch, LinkTracker, WikiExporter


# ── WikiPage Tests ──────────────────────────────────────────────────


class TestWikiPage:
    def test_basic_creation(self):
        page = WikiPage(title="Hello World", content="Some content")
        assert page.title == "Hello World"
        assert page.content == "Some content"
        assert page.tags == []
        assert page.slug == "hello-world"

    def test_slug_generation(self):
        assert WikiPage(title="Hello World").slug == "hello-world"
        assert WikiPage(title="Foo/Bar Baz").slug == "foobar-baz"
        assert WikiPage(title="  spaces  ").slug == "spaces"
        assert WikiPage(title="API & Design").slug == "api-design"

    def test_outgoing_links(self):
        page = WikiPage(
            title="Test",
            content="See [[Other Page]] and [[Third Page|alias]] for details.",
        )
        links = page.outgoing_links()
        assert links == ["Other Page", "Third Page"]

    def test_outgoing_links_with_aliases(self):
        page = WikiPage(
            title="Test",
            content="See [[Target|Display]] and [[Simple]].",
        )
        pairs = page.outgoing_links_with_aliases()
        assert pairs == [("Target", "Display"), ("Simple", None)]

    def test_headings(self):
        page = WikiPage(
            title="Test",
            content="# Title\n## Sub\n### Deep\nSome text\n#### Deeper",
        )
        headings = page.headings()
        assert headings == [
            (1, "Title"),
            (2, "Sub"),
            (3, "Deep"),
            (4, "Deeper"),
        ]

    def test_excerpt(self):
        page = WikiPage(title="Test", content="A" * 300)
        assert page.excerpt(100).endswith("...")
        assert len(page.excerpt(100)) == 100

    def test_word_count(self):
        page = WikiPage(title="Test", content="one two three four")
        assert page.word_count() == 4

    def test_touch(self):
        page = WikiPage(title="Test")
        assert page.updated_at is None
        page.touch()
        assert page.updated_at is not None

    def test_to_dict_roundtrip(self):
        page = WikiPage(title="Test", content="Content", tags=["a", "b"])
        d = page.to_dict()
        assert d["title"] == "Test"
        assert d["tags"] == ["a", "b"]

        restored = WikiPage.from_dict(d)
        assert restored.title == page.title
        assert restored.content == page.content
        assert restored.tags == page.tags
        assert restored.page_id == page.page_id

    def test_render_links(self):
        page = WikiPage(
            title="Test",
            content="Go to [[Home]] and [[About|About Us]].",
        )
        resolver = lambda t: f"/{t.lower().replace(' ', '-')}"
        result = page.render_links(resolver)
        assert "[Home](/home)" in result
        assert "[About Us](/about)" in result

    def test_no_links(self):
        page = WikiPage(title="Test", content="No links here.")
        assert page.outgoing_links() == []


# ── LinkTracker Tests ──────────────────────────────────────────────


class TestLinkTracker:
    def test_add_page(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B", "C"])
        assert tracker.get_forward_links("A") == {"B", "C"}
        assert tracker.get_backlinks("B") == {"A"}
        assert tracker.get_backlinks("C") == {"A"}

    def test_remove_page(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B"])
        tracker.add_page("B", ["A"])
        tracker.remove_page("A")
        assert tracker.get_forward_links("A") == set()
        assert tracker.get_backlinks("B") == set()

    def test_orphans(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B"])
        tracker.add_page("B", ["A"])
        orphans = tracker.get_orphans({"A", "B", "C"})
        assert orphans == {"C"}

    def test_dead_ends(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B"])
        dead = tracker.get_dead_ends({"A", "B"})
        assert dead == {"B"}

    def test_broken_links(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B", "Missing"])
        broken = tracker.get_broken_links({"A", "B"})
        assert broken == {"A": {"Missing"}}

    def test_shortest_path(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B"])
        tracker.add_page("B", ["C"])
        tracker.add_page("C", ["D"])
        path = tracker.shortest_path("A", "D")
        assert path == ["A", "B", "C", "D"]

    def test_shortest_path_unreachable(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B"])
        assert tracker.shortest_path("A", "Z") is None

    def test_shortest_path_self(self):
        tracker = LinkTracker()
        assert tracker.shortest_path("A", "A") == ["A"]

    def test_update_links(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B", "C"])
        tracker.add_page("A", ["D"])
        assert tracker.get_forward_links("A") == {"D"}
        assert tracker.get_backlinks("B") == set()
        assert tracker.get_backlinks("D") == {"A"}

    def test_stats(self):
        tracker = LinkTracker()
        tracker.add_page("A", ["B", "C"])
        tracker.add_page("B", ["C"])
        stats = tracker.stats()
        assert stats["pages_with_links"] == 2
        assert stats["total_links"] == 3
        assert stats["pages_linked_to"] == 2


# ── WikiSearch Tests ───────────────────────────────────────────────


class TestWikiSearch:
    @pytest.fixture
    def search_engine(self):
        engine = WikiSearch()
        engine.index({
            "Python": WikiPage(title="Python", content="Python is a programming language", tags=["code"]),
            "JavaScript": WikiPage(title="JavaScript", content="JavaScript runs in the browser"),
            "Go Lang": WikiPage(title="Go Lang", content="Go is fast and concurrent", tags=["code"]),
            "Recipes": WikiPage(title="Recipes", content="How to cook python snake soup", tags=["food"]),
        })
        return engine

    def test_exact_title_match(self, search_engine):
        results = search_engine.search("Python")
        assert results[0].page.title == "Python"
        assert results[0].match_type == "title_exact"

    def test_partial_title_match(self, search_engine):
        results = search_engine.search("Java")
        assert any(r.page.title == "JavaScript" for r in results)

    def test_content_match(self, search_engine):
        results = search_engine.search("browser")
        assert any(r.page.title == "JavaScript" for r in results)

    def test_tag_match(self, search_engine):
        results = search_engine.search("code")
        assert len(results) == 2

    def test_tag_filter(self, search_engine):
        results = search_engine.search("python", tag_filter=["code"])
        titles = [r.page.title for r in results]
        assert "Recipes" not in titles

    def test_limit(self, search_engine):
        results = search_engine.search("a", limit=2)
        assert len(results) <= 2

    def test_min_score(self, search_engine):
        results = search_engine.search("python", min_score=5.0)
        assert all(r.score >= 5.0 for r in results)

    def test_search_titles_only(self, search_engine):
        results = search_engine.search_titles("Go")
        assert all(r.match_type.startswith("title") for r in results)

    def test_search_by_tag(self, search_engine):
        pages = search_engine.search_by_tag("code")
        assert len(pages) == 2

    def test_recent(self, search_engine):
        pages = search_engine.recent(limit=2)
        assert len(pages) <= 2

    def test_empty_query(self, search_engine):
        assert search_engine.search("") == []


# ── WikiExporter Tests ─────────────────────────────────────────────


class TestWikiExporter:
    @pytest.fixture
    def wiki_pages(self):
        return {
            "Home": WikiPage(title="Home", content="# Welcome\nThis is the **home** page. See [[About]]."),
            "About": WikiPage(title="About", content="## About Us\nWe build things. See [[Home]]."),
        }

    def test_export_all(self, wiki_pages):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = WikiExporter(output_dir=tmpdir)
            backlinks = {"Home": {"About"}, "About": {"Home"}}
            files = exporter.export_all(wiki_pages, backlinks)
            assert len(files) >= 4  # 2 pages + index + recent

            # Check files exist
            for f in files:
                assert os.path.exists(f)

            # Check index exists
            assert os.path.exists(os.path.join(tmpdir, "index.html"))
            assert os.path.exists(os.path.join(tmpdir, "recent.html"))

    def test_exported_html_content(self, wiki_pages):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = WikiExporter(output_dir=tmpdir)
            backlinks = {"Home": {"About"}, "About": {"Home"}}
            exporter.export_all(wiki_pages, backlinks)

            home_html = Path(os.path.join(tmpdir, "home.html")).read_text()
            assert "Welcome" in home_html
            assert "backlinks" in home_html.lower()

    def test_markdown_to_html(self):
        exporter = WikiExporter()
        slug_map = {"about": "About"}
        html = exporter._markdown_to_html("See [[About]] for **info**.", slug_map)
        assert "<strong>info</strong>" in html
        assert 'href="about.html"' in html

    def test_broken_link_rendering(self):
        exporter = WikiExporter()
        slug_map = {}
        html = exporter._markdown_to_html("See [[Missing]].", slug_map)
        assert "broken-link" in html


# ── Wiki Integration Tests ─────────────────────────────────────────


class TestWiki:
    def test_add_and_get(self):
        wiki = Wiki()
        page = WikiPage(title="Test", content="Hello")
        wiki.add_page(page)
        assert wiki.get_page("Test") is page
        assert len(wiki) == 1

    def test_remove(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Test", content="Hello"))
        removed = wiki.remove_page("Test")
        assert removed is not None
        assert "Test" not in wiki
        assert len(wiki) == 0

    def test_rename(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Old", content="Content"))
        wiki.rename_page("Old", "New")
        assert wiki.get_page("Old") is None
        assert wiki.get_page("New") is not None
        assert wiki.get_page("New").content == "Content"

    def test_get_by_slug(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Hello World", content="Hi"))
        assert wiki.get_by_slug("hello-world") is not None
        assert wiki.get_by_slug("nonexistent") is None

    def test_list_pages(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="B", content=""))
        wiki.add_page(WikiPage(title="A", content=""))
        wiki.add_page(WikiPage(title="C", content=""))
        titles = [p.title for p in wiki.list_pages(sort_by="title")]
        assert titles == ["A", "B", "C"]

    def test_search_integration(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Python Guide", content="Learn python programming"))
        wiki.add_page(WikiPage(title="Java Guide", content="Learn java programming"))
        results = wiki.search("Python")
        assert len(results) == 1
        assert results[0].page.title == "Python Guide"

    def test_backlinks(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="A", content="See [[B]] and [[C]]."))
        wiki.add_page(WikiPage(title="B", content="See [[A]]."))
        wiki.add_page(WikiPage(title="C", content="Standalone."))
        assert wiki.backlinks("B") == {"A"}
        assert wiki.backlinks("A") == {"B"}
        assert wiki.backlinks("C") == {"A"}

    def test_orphans(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="A", content="See [[B]]."))
        wiki.add_page(WikiPage(title="B", content="See [[A]]."))
        wiki.add_page(WikiPage(title="Orphan", content="Alone."))
        assert wiki.orphans() == {"Orphan"}

    def test_broken_links(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="A", content="See [[Missing Page]]."))
        broken = wiki.broken_links()
        assert broken == {"A": {"Missing Page"}}

    def test_export(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Home", content="# Welcome\nHello world."))
        with tempfile.TemporaryDirectory() as tmpdir:
            files = wiki.export(output_dir=tmpdir)
            assert len(files) >= 2
            assert any("index.html" in f for f in files)

    def test_save_and_load(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Test", content="Content", tags=["a"]))
        wiki.add_page(WikiPage(title="Other", content="See [[Test]]."))

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            wiki.save(path)
            loaded = Wiki.load(path)
            assert len(loaded) == 2
            assert loaded.get_page("Test").content == "Content"
            assert loaded.get_page("Test").tags == ["a"]
            # Search should work on loaded wiki
            results = loaded.search("Test")
            assert len(results) > 0
        finally:
            os.unlink(path)

    def test_contains(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="Test", content=""))
        assert "Test" in wiki
        assert "Missing" not in wiki

    def test_repr(self):
        wiki = Wiki()
        wiki.add_page(WikiPage(title="A", content=""))
        assert "pages=1" in repr(wiki)
