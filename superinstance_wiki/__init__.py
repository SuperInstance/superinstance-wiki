"""SuperInstance Wiki — a Python wiki engine for the SuperInstance knowledge base."""

from .wiki import Wiki
from .page import WikiPage
from .search import WikiSearch
from .link import LinkTracker
from .export import WikiExporter

__version__ = "1.0.0"
__all__ = ["Wiki", "WikiPage", "WikiSearch", "LinkTracker", "WikiExporter"]
