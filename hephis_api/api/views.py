
import json
import asyncio

from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hephis_core.infra.sources.t_g_scraper import fetch_and_extract
from hephis_core.infra.sources.music_scraper import extract_chords_and_lyrics
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.schemas.mappers.music_mapper import map_music_data

from rest_framework.views import APIView
from rest_framework.response import Response
from hephis_core.utils.json_handler import find_json_files


def ping(request):
    return JsonResponse({"message": "alive"})

@csrf_exempt
def normalize_recipe_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    result = recipe_normalizer(body)
    return JsonResponse(result, safe=False)

def run_scraper_sync(url: str):
    return asyncio.run(fetch_and_extract(url))

@csrf_exempt
def import_recipe_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
        url = body["url"]
    except Exception:
        return JsonResponse({"error": "Invalid JSON or missing 'url'"}, status=400)

    scraped = run_scraper_sync(url)
    if scraped is None:
        return JsonResponse({"error": "Scraper failed"}, status=500)

    normalized = recipe_normalizer(scraped)
    if not normalized.get("success"):
        return JsonResponse(normalized, safe=False, status=400)

    from hephis_core.schemas.panaceia_schemas import RecipeSchema
    
    model = RecipeSchema(**normalized["data"])
    packed = pack_data("recipes", model)

    packed["path"] = str(packed["path"])

    return JsonResponse(
        {
            "success": True,
            "scraped": scraped,
            "normalized": normalized["data"],
            "packed": packed,
        },
        safe=False
    )

@csrf_exempt
def import_music_chords_and_lyrics(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
        url = body["url"]
    except Exception:
        return JsonResponse({"error": "Invalid JSON or missing 'url'"}, status=400)

    scraped = extract_chords_and_lyrics(url)

    if scraped is None:
        return JsonResponse({"error": "Scraper failed"}, status=500)

    paragraphs = scraped.get("paragraphs", []) if isinstance(scraped, dict) else scraped
    title = scraped.get("title", "Unknown Title") if isinstance(scraped, dict) else "Unknown Title"

    organized = music_organizer(paragraphs)

    # Call the normalizer using the signature it actually expects (no 'title' kwarg)
    from hephis_core.modules.music_normalizer.normalizer import music_normalizer
    model = music_normalizer(organized, url=url, run_id="django-api")

    # Ensure the final model/dict contains the title (defensive to handle different return types)
    # Case A: Pydantic model with .model_dump() / attribute assignment
    try:
        # If it's a Pydantic model, prefer setting attribute if writable
        if hasattr(model, "model_dump"):
            # Try attribute assignment first (works if model is mutable)
            try:
                setattr(model, "title", title)
            except Exception:
                # fallback: rebuild a model from its dict with title injected
                data = model.model_dump()
                data["title"] = title
                from hephis_core.schemas.music_schemas import ChordSheetSchema
                model = ChordSheetSchema(**data)
        # Case B: dict-like result
        elif isinstance(model, dict):
            model["title"] = title
        # Case C: some other object: try to set attribute
        else:
            try:
                setattr(model, "title", title)
            except Exception:
                # last resort: wrap into a dict for downstream packer
                model = {"title": title, "sections": getattr(model, "sections", organized), "source": "scraped", "url": url, "run_id": "django-api"}
    except Exception:
        # defensive fallback: construct a minimal model dict
        model = {"title": title, "sections": organized, "source": "scraped", "url": url, "run_id": "django-api"}

    # Now pack it (pack_data expects a Pydantic model or dict; your packer is defensive but we pass what's available)
    packed = pack_data("music", model)
    packed["path"] = str(packed["path"])

    return JsonResponse(
        {
            "success": True,
            "scraped": [str(p) for p in paragraphs],
            "organized": organized,
            # If model is Pydantic object, model_dump() returns dict. If it's already a dict, return it.
            "model": model.model_dump() if hasattr(model, "model_dump") else model,
            "packed": packed,
        },
        safe=False,
    )

class MusicListView(APIView):
    def get(self, request):
        files = find_json_files("data/music")
        results = []

        for f in files:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            title = data.get("title", "Unknown")
            slug = f.parent.name

            results.append({
                "title": title,
                "slug": slug,
                "path": str(f)
            })

        return Response({
            "success": True,
            "count": len(results),
            "items": results
        })