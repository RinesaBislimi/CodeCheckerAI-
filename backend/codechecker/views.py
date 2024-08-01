import ast
import re
import tempfile
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .serializers import CodeSnippetSerializer
from rest_framework.views import APIView
from .ml_model import (
    analyze_code,
    analyze_github_repo,
    fetch_repo_contents,
    analyze_code_contents,
    detect_security_vulnerabilities,
)


def find_unused_imports(code):
    """
    Detect unused imports in the given code string.
    """
    try:
        tree = ast.parse(code)
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import)]
        import_froms = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        all_imports = imports + import_froms

        used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

        unused_imports = []

        for node in all_imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        if alias.asname not in used_names:
                            unused_imports.append(alias.asname)
                    else:
                        if alias.name.split('.')[0] not in used_names:
                            unused_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname:
                        if alias.asname not in used_names:
                            unused_imports.append(alias.asname)
                    else:
                        if alias.name not in used_names:
                            unused_imports.append(alias.name)

        return unused_imports

    except Exception as e:
        return [f"Error analyzing imports: {e}"]

class CodeSnippetSerializer(serializers.Serializer):
    code = serializers.CharField()

class CodeCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CodeSnippetSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get("code")
            
            # Initialize results
            result = "No syntax errors detected."
            unused_imports = []

            # Check for syntax errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                result = f"Syntax Error: {e}"
                return Response({
                    "result": result,
                    "unused_imports": unused_imports,
                    "corrected_code": ""
                }, status=status.HTTP_200_OK)
            
            # Check for unused imports
            unused_imports = find_unused_imports(code)
            if unused_imports:
                result = "Code contains unused imports."

            # Replace placeholder
            corrected_code = re.sub(r'print\(([^f"]+)"', r'print(f"\1{"{PLACEHOLDER}"}")', code)

            return Response({
                "result": result,
                "unused_imports": unused_imports,
                "corrected_code": corrected_code
                 }, status=status.HTTP_200_OK)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def analyze_code_contents(code_contents):
    """
    Analyze the contents of the code files and detect issues such as unused imports.
    """
    analysis_results = {}

    for filename, code in code_contents.items():
        if filename.endswith('.py'):
            unused_imports = find_unused_imports(code)
            if unused_imports:
                analysis_results[filename] = {
                    "issue": "Contains import statements. Check for unused imports.",
                    "unused_imports": unused_imports
                }
            else:
                analysis_results[filename] = {"issue": "No issues detected."}
        else:
            analysis_results[filename] = {"issue": "No issues detected."}

    return analysis_results


class CodeAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code', '')
        visualization_type = request.data.get('visualization_type', 'bar')
        analysis_results = analyze_code(code, visualization_type)
        return Response(analysis_results, status=status.HTTP_200_OK)


class GithubRepoAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        repo_url = request.data.get('repo_url', '')
        try:
            repo_info = analyze_github_repo(repo_url)  # Basic repo info
            code_contents = fetch_repo_contents(repo_url)  # Fetch code files
            analysis_results = analyze_code_contents(code_contents)  # Analyze code
            security_vulnerabilities = detect_security_vulnerabilities(code_contents)  # Detect vulnerabilities
            
            return Response({
                'repository': repo_info,
                'analysis_results': analysis_results,
                'security_vulnerabilities': security_vulnerabilities,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Utility function for checking code errors
def check_code_for_errors(code):
    try:
        ast.parse(code)
        return "No syntax errors detected."
    except SyntaxError as e:
        return f"Syntax Error: {e}"
