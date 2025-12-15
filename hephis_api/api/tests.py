from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

SAMPLE_RECIPE_TEXT = """
Ingredientes
2 ovos
1 xícara de farinha

Modo de preparo
Misture tudo
Asse por 30 minutos
"""

class TestUniversalInputAPI(APITestCase):

    def test_recipe_text_does_not_crash(self):
        url = "/api/input/"
        response = self.client.post(
            url,
            data={"input": SAMPLE_RECIPE_TEXT},
            format="json"
        )

        # 🔴 THE MOST IMPORTANT ASSERT
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.content
        )

        # Optional sanity checks
        self.assertIn(response.status_code, (200, 202, 400))

        # Ensure response is JSON
        self.assertIsInstance(response.data, dict)

    def test_recipe_url_does_not_crash(self):
        url = "/api/input/"

        response = self.client.post(
            url,
            data={"input": "https://www.tudogostoso.com.br/receita/23-bolo-de-cenoura.html"},
            format="json"
        )
        self.assertNotEqual(response.status_code, 500)

    def test_music_url_does_not_crash(self):
        url = "/api/input/"

        response = self.client.post(
            url,
            data={"input": "http://bettyloumusic.com/takeonme.htm"},
            format="json"
        )
        self.assertNotEqual(response.status_code, 500)

    def test_garbage_input_does_not_crash(self):
        url = "/api/input/"

        garbage_inputs = [
            "asdasd123 !!! ###",
            "",
            "     ",
            "%%%%%%%",
            "🤡🤡🤡🤡",
            "<not html but looks like < >",
            "http://",
            "file:///etc/passwd",
        ]

        for garbage in garbage_inputs:
            response = self.client.post(
                url,
                data={"input": garbage},
                format="json"
            )

            # 🔴 core invariant: system must NOT crash
            self.assertNotEqual(
                response.status_code,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Crash with input: {garbage!r}"
            )

            # Acceptable outcomes for garbage
            self.assertIn(
                response.status_code,
                (200, 202, 400),
                f"Unexpected status {response.status_code} for input: {garbage!r}"
            )