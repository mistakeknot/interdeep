"""Playwright-based content extraction — fallback for JS-rendered pages."""

import logging
from .models import ExtractionResult

logger = logging.getLogger("interdeep.extraction")

_PLAYWRIGHT_AVAILABLE = False
try:
    import playwright  # noqa: F401
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


async def extract_with_playwright(url: str, timeout: int = 30000) -> ExtractionResult:
    """Render page with headless browser and extract content."""
    if not _PLAYWRIGHT_AVAILABLE:
        return ExtractionResult(url=url, content="", method="failed",
                                metadata={"error": "playwright not installed"})
    if not url:
        return ExtractionResult(url="", content="", method="failed")
    try:
        from playwright.async_api import async_playwright
        from .trafilatura_ext import extract_from_html

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            html = await page.content()
            await browser.close()

        result = extract_from_html(html, url=url)
        result.method = "playwright"
        result.metadata["rendered"] = True
        return result
    except Exception as e:
        logger.warning("Playwright extraction failed for %s: %s", url, e)
        return ExtractionResult(url=url, content="", method="failed",
                                metadata={"error": str(e)})


def is_available() -> bool:
    return _PLAYWRIGHT_AVAILABLE
