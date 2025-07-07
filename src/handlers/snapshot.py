# /backend/handlers/snapshot.py
# Handles generating webpage snapshots using Playwright (Python's Puppeteer equivalent).

from playwright.async_api import async_playwright

async def generate_snapshot(url: str) -> bytes:
    """
    Generates a snapshot of a given URL.
    Returns the image as bytes.
    """
    async with async_playwright() as p:
        # TODO: Add error handling for browser launch and page navigation
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        screenshot_bytes = await page.screenshot()
        await browser.close()
        return screenshot_bytes