from playwright.async_api import async_playwright

async def generate_snapshot(url: str, output_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
