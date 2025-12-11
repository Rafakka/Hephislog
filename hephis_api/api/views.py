from rest_framework.views import APIView
from rest_framework.response import Response
from hephis_core.infra.retrievers.caller import call_retrievers

class MusicLocalListView(APIView):
    def get(self, request):
        results = call_retrievers(domain="music", input_type="list")
        return Response(results)

class MusicLocalViewFileByName(APIView):
    def get(self, request, slug):
        results = call_retrievers(domain="music", input_type="file",value=slug)
        if not results:
            return Response({"error":"Not found"}, status=404)
        return Response(results[0])

class RecipeLocalListView(APIView):
    def get(self, request):
        results = call_retrievers(domain="recipe", input_type="list")
        return Response(results)

class RecipeLocalViewFileByName(APIView):
    def get(self, request, slug):
        results = call_retrievers(domain="recipe", input_type="file",value=slug)
        if not results:
            return Response({"error":"Not found"}, status=404)
        return Response(results[0])