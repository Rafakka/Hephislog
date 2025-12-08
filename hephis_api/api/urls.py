from django.urls import path
from .views import (
    ping,MusicListView, MusicDetailView, MusicImportView,
    RecipeDetailView, RecipeListView,RecipeImportView
    )

urlpatterns = [
    path("ping/", ping),

    path("music/list/", MusicListView.as_view()),
    path("music/detail/<slug:slug>/", MusicDetailView.as_view()),
    path("music/import/", MusicImportView.as_view()),

    path("recipes/list/", RecipeListView.as_view()),
    path("recipes/detail/<slug:slug>/", RecipeDetailView.as_view()),
    path("recipes/import/", RecipeImportView.as_view()),
]