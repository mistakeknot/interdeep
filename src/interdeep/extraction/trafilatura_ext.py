"""trafilatura-based content extraction — fast path for ~80% of web pages."""

import logging
from .models import ExtractionResult

logger = logging.getLogger("interdeep.extraction")


def extract_with_trafilatura(url: str, timeout: int = 10) -> ExtractionResult:
    """Fetch and extract main content from a URL using trafilatura."""
    if not url:
        return ExtractionResult(url="", content="", method="failed")
    try:
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return ExtractionResult(url=url, content="", method="failed",
                                    metadata={"error": "fetch returned None"})
        return extract_from_html(downloaded, url=url)
    except Exception as e:
        logger.warning("trafilatura extraction failed for %s: %s", url, e)
        return ExtractionResult(url=url, content="", method="failed",
                                metadata={"error": str(e)})


def extract_from_html(html: str, url: str = "") -> ExtractionResult:
    """Extract main content from raw HTML string."""
    try:
        import trafilatura

        text = trafilatura.extract(
            html,
            url=url,
            include_links=True,
            include_formatting=True,
            include_tables=True,
            favor_precision=False,
            favor_recall=True,
            output_format="txt",
        )
        if text is None:
            return ExtractionResult(url=url, content="", method="failed",
                                    metadata={"error": "extraction returned None"})
        title = trafilatura.extract_metadata(html, url)
        title_str = title.title if title and title.title else ""
        return ExtractionResult(url=url, content=text, title=title_str,
                                method="trafilatura")
    except Exception as e:
        logger.warning("HTML extraction failed: %s", e)
        return ExtractionResult(url=url, content="", method="failed",
                                metadata={"error": str(e)})
