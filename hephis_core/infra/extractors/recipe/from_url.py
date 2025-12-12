import os
from playwright.async_api import async_playwright
from hephis_core.utils.logger_decorator import log_action
from hephis_core.infra.extractors.registry import extractor


@log_action(action="extract_recipe_from_url")
@extractor(domain="recipe", input_type="url")
async def extract_recipe_from_url(url: str) -> dict | None:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            await page.wait_for_timeout(6000)
            html = await page.content()
            await browser.close()

            return {
                "raw_html": html,
                "source": "url",
                "url": url
            }

        except Exception as e:
            await browser.close()
            return None