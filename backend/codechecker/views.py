import ast
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import pandas as pd
from sklearn.ensemble import IsolationForest
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import logging

import io
import base64
import numpy as np
from .ml_model import (
    analyze_code,
    analyze_github_repo,
    fetch_repo_contents,
    analyze_code_contents,
    detect_security_vulnerabilities,
    detect_code_clones,
    detect_code_clusters,
    extract_keywords_from_code,
    detect_code_smells,
    detect_deprecated_libraries,
    detect_anomalies
)
from .utils import find_unused_imports, remove_unused_imports  
from .serializers import CodeSnippetSerializer

class CodeCheckView(APIView):
    permission_classes = [AllowAny]

    def correct_syntax_errors(self, code):
        """
        Attempts to correct common syntax errors in the provided code.
        """
        correction_message = None
        max_iterations = 10  

        for _ in range(max_iterations):
            try:
                ast.parse(code)
                return code, correction_message  
            except SyntaxError as e:
                lines = code.split('\n')
                error_line_number = e.lineno - 1  
                error_line = lines[error_line_number]

                new_correction_message = None

               
                if error_line.count('(') > error_line.count(')'):
                    lines[error_line_number] = error_line + ')'
                    new_correction_message = "Added missing closing parenthesis."

                # Fix: Missing closing bracket
                elif error_line.count('[') > error_line.count(']'):
                    lines[error_line_number] = error_line + ']'
                    new_correction_message = "Added missing closing bracket."

                # Fix: Missing closing brace
                elif error_line.count('{') > error_line.count('}'):
                    lines[error_line_number] = error_line + '}'
                    new_correction_message = "Added missing closing brace."

                # Fix: Missing colon at the end of control structures
                elif any(error_line.strip().startswith(keyword) for keyword in ('if', 'elif', 'else', 'for', 'while', 'def', 'class')):
                    if not error_line.strip().endswith(':'):
                        lines[error_line_number] = error_line + ':'
                        new_correction_message = "Added missing colon at the end of the statement."

                # Fix: Missing quotation mark (double or single)
                elif error_line.count('"') % 2 != 0:
                    lines[error_line_number] = error_line + '"'
                    new_correction_message = "Added missing double quotation mark."
                elif error_line.count("'") % 2 != 0:
                    lines[error_line_number] = error_line + "'"
                    new_correction_message = "Added missing single quotation mark."

                # Fix: Indentation errors
                elif 'expected an indented block' in str(e):
                    indentation_level = len(error_line) - len(error_line.lstrip())
                    lines.insert(error_line_number + 1, ' ' * (indentation_level + 4) + 'pass')
                    new_correction_message = "Added 'pass' statement to fix indentation."

                # Fix: Unexpected EOF while parsing
                elif 'unexpected EOF while parsing' in str(e):
                    lines[error_line_number] = error_line + '\npass'
                    new_correction_message = "Added 'pass' to complete the statement."

                # Fix: Assignments without expressions
                elif 'cannot assign to' in str(e) and error_line.strip().endswith('='):
                    lines[error_line_number] = error_line + ' None'
                    new_correction_message = "Added 'None' to complete the assignment."

                else:
                    # If no automatic fix can be applied, return the original code with an error message
                    return code, f"Syntax Error: {e}"

                code = '\n'.join(lines)
                correction_message = (correction_message or "") + " " + new_correction_message

        # If maximum iterations are reached, return the current state of the code
        return code, correction_message or "Reached maximum iterations, some errors might still be present."

    def post(self, request, *args, **kwargs):
        serializer = CodeSnippetSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get("code")

            # Correct syntax errors if possible
            corrected_code, correction_message = self.correct_syntax_errors(code)

            # Check for remaining syntax errors after correction
            try:
                ast.parse(corrected_code)
            except SyntaxError as e:
                return Response({"result": f"Syntax Error: {e}"}, status=status.HTTP_200_OK)
            
            # List unused imports
            unused_imports = find_unused_imports(corrected_code)

            # Now remove unused imports from the corrected code
            corrected_code = remove_unused_imports(corrected_code)

            # Analyze the code using various functions
            anomaly_detection_result = detect_anomalies([corrected_code])
            code_clones = detect_code_clones([corrected_code, corrected_code])
            keywords = extract_keywords_from_code(corrected_code)
            code_smells = detect_code_smells(corrected_code)
            deprecated_libraries = detect_deprecated_libraries(corrected_code)
            clusters = detect_code_clusters([corrected_code, corrected_code])

            response_data = {
                "result": correction_message if correction_message else "No syntax errors detected.",
                "unused_imports": unused_imports,  # Listing unused imports
                "corrected_code": corrected_code,  # Now includes both syntax corrections and removal of unused imports
                "anomaly_detection_result": anomaly_detection_result,
                "keywords": keywords,
                "code_smells": code_smells,
                "deprecated_libraries": deprecated_libraries,
                "code_clones": code_clones,
                "clusters": clusters,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

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
        
        
        
        
class DatasetCheckView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Load dataset into a DataFrame
            df = pd.read_csv(file)

            # Check for numeric features
            numeric_features = df.select_dtypes(include=[np.number])
            if numeric_features.empty:
                return Response({'error': 'Dataset does not contain numeric features for anomaly detection.'}, status=status.HTTP_400_BAD_REQUEST)
            
            features = numeric_features.values
            
            # Anomaly detection using Isolation Forest
            model = IsolationForest(contamination=0.1)
            model.fit(features)
            predictions = model.predict(features)
            
            # Identify anomalies
            anomalies = np.where(predictions == -1)[0]
            num_anomalies = len(anomalies)
            
            # Generate a graph
            plt.figure(figsize=(10, 6))
            plt.scatter(range(len(features)), features[:, 0], c='blue', label='Normal')
            plt.scatter(anomalies, features[anomalies, 0], c='red', label='Anomaly')
            plt.title('Anomaly Detection')
            plt.xlabel('Index')
            plt.ylabel('Feature Value')
            plt.legend()
            plt.grid(True)
            
            # Save plot to a BytesIO object
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            
            return Response({
                'num_anomalies': num_anomalies,
                'anomalies': anomalies.tolist(),
                'anomaly_graph': img_str  # Include the base64-encoded image here
            })

        except pd.errors.EmptyDataError:
            return Response({'error': 'Uploaded file is empty. Please upload a non-empty CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
        except pd.errors.ParserError:
            return Response({'error': 'Error parsing the file. Please ensure the file is a valid CSV format.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)