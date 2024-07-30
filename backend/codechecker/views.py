from rest_framework.views import APIView
from rest_framework import serializers
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
import ast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CodeSnippetSerializer
import ast
from .ml_model import analyze_code  , analyze_github_repo
import re
import tempfile
import subprocess


class CodeAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code', '')
        visualization_type = request.data.get('visualization_type', 'bar')
        analysis_results = analyze_code(code, visualization_type)
        return Response(analysis_results, status=status.HTTP_200_OK)


class CodeSnippetSerializer(serializers.Serializer):
    code = serializers.CharField()

def check_code_quality(code):
    if "import" in code:
        return "Code contains import statements, check for unused imports."
    else:
        return "Code looks good."

class CodeCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CodeSnippetSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get("code")
            try:
                ast.parse(code)
                result = "No syntax errors detected."

                corrected_code = re.sub(r'print\(([^f"]+)"', r'print(f"\1{"{PLACEHOLDER}"}")', code)

            except SyntaxError as e:
                result = f"Syntax Error: {e}"
                corrected_code = "" 

            return Response({
                "result": result,
                "corrected_code": corrected_code
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class GithubRepoAnalysisView(APIView):
    def post(self, request):
        repo_url = request.data.get('repo_url', '')
        try:
            analysis_results = analyze_github_repo(repo_url)
            return Response(analysis_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
def check_code_for_errors(code):
    try:
        ast.parse(code)
        return "No syntax errors detected."
    except SyntaxError as e:
        return f"Syntax Error: {e}"
    
class CodeAnalysisView(APIView):
    def post(self, request):
        code = request.data.get('code', '')
        analysis_results = analyze_code(code)
        return Response(analysis_results)