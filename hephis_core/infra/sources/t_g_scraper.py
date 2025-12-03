#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
t_g_scraper.py
Playwright + BeautifulSoup
Baixa e extrai automaticamente receitas do TG.
"""

import asyncio
import os
import re
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --------------------------------------------------
# 🔧 Helpers
# --------------------------------------------------

def slugify(url):
    path = urlparse(url).path.strip("/")
    return re.sub(r"[^a-zA-Z0-9_-]", "_", path) or "index"

def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# --------------------------------------------------
# 🧠 Extrator específico do TG
# --------------------------------------------------

def extract_tg_recipe(html):
    soup = BeautifulSoup(html, "html.parser")

    # 🏷️ Título
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Sem título"

    # 🧂 Ingredientes
    ingredients_section = soup.select_one("section.recipe-section.recipe-ingredients")
    ingredients = []
    if ingredients_section:
        for span in ingredients_section.select("span.recipe-ingredients-item-label"):
            txt = span.get_text(strip=True)
            if txt:
                ingredients.append(txt)

    # 🔥 Modo de preparo
    steps_section = soup.select_one("section.recipe-section.recipe-steps")
    steps = []
    if steps_section:
        for li in steps_section.find_all("li"):
            txt = li.get_text(" ", strip=True)
            if len(txt) > 1:
                steps.append(txt)
        if not steps:  # fallback se não tiver <li>
            for p in steps_section.find_all("p"):
                txt = p.get_text(" ", strip=True)
                if len(txt) > 1:
                    steps.append(txt)

    # ⏱️ Tempo e rendimento
    info = {}
    if steps_section:
        text_block = steps_section.get_text(" ", strip=True)
        m_time = re.search(r"(?i)(\d+\s*(?:minutos?|horas?))", text_block)
        m_servings = re.search(r"(?i)(\d+\s*(?:porç(?:ões|ao|aoes)|pessoas?))", text_block)
        if m_time:
            info["time"] = m_time.group(1)
        if m_servings:
            info["servings"] = m_servings.group(1)

    return {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "info": info
    }

# --------------------------------------------------
# 🕹️ Scraper com Playwright
# --------------------------------------------------

async def fetch_and_extract(url, outdir="recipes_tg", retries=3):
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
                recipe = extract_tg_recipe(html)
                save_text(json_path, json.dumps(recipe, ensure_ascii=False, indent=2))
                print(f"🥣 Receita salva em: {json_path}")

                await browser.close()
                return recipe

            except Exception as e:
                print(f"❌ Erro: {e}")
                await browser.close()

        print("🚫 Todas as tentativas falharam — Cloudflare ainda bloqueando.")
        return None

# --------------------------------------------------
# CLI
# --------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python tg_scraper.py <URL_da_receita>")
        sys.exit(1)
    url = sys.argv[1]
    asyncio.run(fetch_and_extract(url))
