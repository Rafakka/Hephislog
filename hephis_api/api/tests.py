from rest_framework.test import APITestCase
from rest_framework import status

SAMPLE_RECIPE_TEXT = """
Ingredientes
2 ovos
1 xícara de farinha

Modo de preparo
Misture tudo
Asse por 30 minutos
"""

class TestUniversalInputAPI(APITestCase):

    def test_recipe_text_routes_to_recipe_with_smell(self):
        response = self.client.post(
            "/api/input/",
            data={"input": SAMPLE_RECIPE_TEXT},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        # --- routing decision ---
        self.assertEqual(data.get("domain"), "recipe")

        # --- interpreted structure ---
        self.assertIn("ingredients", data)
        self.assertIn("steps", data)

        # --- smell influence ---
        self.assertIn("confidence", data)
        self.assertGreater(data["confidence"], 0.5)

    def test_music_url_routes_to_music(self):
        response = self.client.post(
            "/api/input/",
            data={"input": "http://bettyloumusic.com/takeonme.htm"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data.get("domain"), "music")

    def test_garbage_input_is_gracefully_rejected(self):
        garbage_inputs = [
            "asdasd123 !!! ###",
            "%%%%%%%",
            "🤡🤡🤡🤡",
            "http://",
            "<not html but looks like < >",
        ]

        for garbage in garbage_inputs:
            response = self.client.post(
                "/api/input/",
                data={"input": garbage},
                format="json"
            )

            # --- must not crash ---
            self.assertNotEqual(response.status_code, 500)

            # --- no forced interpretation ---
            if response.status_code == status.HTTP_200_OK:
                self.assertNotIn("domain", response.data)
            else:
                self.assertIn(response.status_code, (202, 400))
