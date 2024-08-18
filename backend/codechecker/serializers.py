from rest_framework import serializers
from .models import CodeSnippet, AnalysisResult



class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = '__all__'

class CodeSnippetSerializer(serializers.Serializer):
    code = serializers.CharField()