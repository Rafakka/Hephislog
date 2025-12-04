from django.urls import path
from .views import ping, normalize_recipe_view, import_recipe_view, import_music_chords_and_lyrics, MusicListView

urlpatterns = [
    path("ping/", ping),
    path("recipes/normalize/", normalize_recipe_view),
    path("recipes/import-url/", import_recipe_view),
    path("music/import-chord-and-lyrics/", import_music_chords_and_lyrics),
    path("music/list/", MusicListView.as_view())
]
