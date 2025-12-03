
import json
import asyncio
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hephis_core.infra.sources.t_g_scraper import fetch_and_extract
from hephis_core.infra.sources.music_scraper import extract_chords_and_lyrics
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.schemas.mappers.music_mapper import map_music_data

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
def import_music_chords_and_lyrics (request):
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

    organized = music_organizer(scraped)

    model = map_music_data(
        title="Unknown Title",
        sections=organized,
        source="scraped",
        url=url,
        run_id="django-api"
    )

    packed = pack_data("music", model)
    packed["path"] = str(packed["path"])

    return JsonResponse(
        {
            "success": True,
            "scraped": [str(p) for p in scraped],
            "organized": organized,
            "model": model.model_dump(),
            "packed": packed,
        },
        safe=False,
    )
