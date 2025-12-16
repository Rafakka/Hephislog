from rest_framework.views import APIView
from rest_framework.response import Response
from hephis_core.infra.retrievers.caller import call_retrievers
from hephis_core.events.event_bus import EventBus
from hephis_core.pipeline import process_input
from rest_framework import status


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

class UniversalInput(APIView):

    def post(self, request):
        raw = request.data.get("input")
        if not raw and "input_file" in request.FILES:
            raw = request.FILES["input_file"].read().decode("utf-8")

        if raw is None:
            return Response({"error": "Missing input"}, status=status.HTTP_400_BAD_REQUEST)

        event_bus = EventBus()
        event_bus.emit("system.input_received", {"input": raw})

        try:
            result = process_input(raw)
        except Exception as e:
            return Response(
                {"error": "Internal processing error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not result:
            return Response(
                {"status": "no_match"},
                status=status.HTTP_202_ACCEPTED
            )

        return Response(result, status=status.HTTP_200_OK)