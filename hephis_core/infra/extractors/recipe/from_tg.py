import re
import json
from bs4 import BeautifulSoup
from hephis_core.utils.logger_decorator import log_action
from hephis_core.infra.extractors.registry import extractor

@log_action(action="extract_recipe_from_tg_html")
@extractor(domain="recipe", input_type="html")
def extract_recipe_from_tg_html(html):
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