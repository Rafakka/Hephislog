from hephis_core.infra.extractors.recipe.from_html import extract_recipe_from_html
import asyncio
import os
import json
from playwright.async_api import async_playwright
from hephis_core.utils.logger_decorator import log_action
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.cleaners.data_cleaner import slugify
from hephis_core.utils.file_setter import save_text

@log_action(action="extract_recipe_from_url")
@extractor(domain="recipe", input_type="url")
async def extract_recipe_from_url(url, outdir="recipes_tg", retries=3):
    os.makedirs(outdir, exist_ok=True)
    slug = slugify(url)
    html_path = os.path.join(outdir, f"{slug}.html")
    json_path = os.path.join(outdir, f"{slug}.json")

    async with async_playwright() as p:
        for attempt in range(1, retries + 1):
            print(f"🌐 Tentativa {attempt}/{retries}: {url}")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"),
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_timeout(8000)  # espera JS e Cloudflare
                html = await page.content()

                # verifica se ainda está no desafio do Cloudflare
                if "Verifying you are human" in html or "Just a moment" in html:
                    print("⚠️  Ainda na tela de verificação. Repetindo tentativa...")
                    await browser.close()
                    continue

                save_text(html_path, html)
                print(f"✅ HTML salvo em: {html_path}")

                # Extrai os dados direto do HTML
                recipe = extract_recipe_from_html(html)
                save_text(json_path, json.dumps(recipe, ensure_ascii=False, indent=2))
                print(f"🥣 Receita salva em: {json_path}")

                await browser.close()
                return recipe

            except Exception as e:
                print(f"❌ Erro: {e}")
                await browser.close()

        print("🚫 Todas as tentativas falharam — Cloudflare ainda bloqueando.")
        return None
