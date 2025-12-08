
import json
import asyncio
from pathlib import Path

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from hephis_api.api.repositories.music_repository import MusicRepository
from hephis_api.api.repositories.recipe_repository import RecipeRepository


def ping(request):
    return JsonResponse({"message": "alive"})

class RecipeListView(APIView):
    def get(self, request):
        items = RecipeRepository.list()
        return Response({
            "success": True,
            "count": len(items),
            "items": items
        })

class RecipeDetailView(APIView):
    def get(self, request, slug):
        info = RecipeRepository.load(slug)

        if not info["success"]:
            return Response(info, status=404)

        return Response({
            "success": True,
            "slug": slug,
            "file": info["file_path"],
            "data": info["data"]
        })

class RecipeImportView(APIView):
    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response({"error": "Missing url"}, status=400)

        info = RecipeRepository.import_from_url(url)

        return Response(info)

class MusicListView(APIView):
    def get(self, request):
        items = MusicRepository.list()
        return Response({
            "success": True,
            "count": len(items),
            "items": items
        })

class MusicDetailView(APIView):
    def get(self, request, slug):
        info = MusicRepository.load(slug)

        if not info["success"]:
            return Response(info, status=404)

        return Response({
            "success": True,
            "slug": slug,
            "file": info["file_path"],
            "data": info["data"]
        })

class MusicImportView(APIView):
    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response({"error": "Missing url"}, status=400)

        info = MusicRepository.import_from_url(url)

        return Response(info)
