from rest_framework import serializers

class MusicListSerializer(serializers.Serializer):
    title = serializers.CharField()
    slug = serializers.CharField()
    path = serializers.CharField()