from django.urls import path
from .views import (
    MusicLocalListView, MusicLocalViewFileByName, RecipeLocalListView, RecipeLocalViewFileByName
    )

urlpatterns = [
    path("music/local/", MusicLocalListView.as_view(), name="music-local-list"),
    path("music/local/<slug:slug>/", MusicLocalViewFileByName.as_view(),name="find-music-local-file"),
    path("recipe/local/", RecipeLocalListView.as_view(), name="recipe-local-list"),
    path("recipe/local/<slug:slug>/", RecipeLocalViewFileByName.as_view(),name="find-recipe-local-file")
]