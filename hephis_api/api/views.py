from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from hephis_core.infra.retrievers.caller import call_retrievers
from hephis_core.events.event_bus import EventBus
from hephis_core.pipe_line import process_input
from hephis_core.pipeline.results import get_result, pop_result
import time
import uuid



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

    MAX_WAIT_SECONDS = 10
    POLL_INTERVAL = 0.05


    def post(self, request):
        raw = request.data.get("input")
        if not raw and "input_file" in request.FILES:
            raw = request.FILES["input_file"].read().decode("utf-8")

        if not raw:
            return Response({"error": "Missing input"}, status=status.HTTP_400_BAD_REQUEST)

        run_id =str(uuid.uuid4())

        EventBus.emit(
            "system.input_received",{
                "input": raw,
                "run_id":run_id,
                "source":"api",
            }
        )

        start_time = time.time()

        while (time.time() - start_time) < self.MAX_WAIT_SECONDS:
            result = get_result(run_id)

            if result is not None:
                pop_result(run_id)

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        time.sleep(self.POLL_INTERVAL)

        return Response (
            {
                "status":"processing",
                "run_id":run_id,
                "message":"Pipeline still running",
            },
            status=status.HTTP_202_ACCEPTED,
        )