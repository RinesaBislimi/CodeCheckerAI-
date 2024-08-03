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
from .utils import find_unused_imports, remove_unused_imports  # Import from utils

class CodeSnippetSerializer(serializers.Serializer):
    code = serializers.CharField()

class CodeCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CodeSnippetSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get("code")

            try:
                ast.parse(code)
            except SyntaxError as e:
                return Response({"result": f"Syntax Error: {e}"}, status=status.HTTP_200_OK)

            unused_imports = find_unused_imports(code)
            anomaly_detection_result = detect_anomalies([code])
            code_clones = detect_code_clones([code, code])
            keywords = extract_keywords_from_code(code)
            code_smells = detect_code_smells(code)
            deprecated_libraries = detect_deprecated_libraries(code)
            clusters = detect_code_clusters([code, code])

            response_data = {
                "result": "No syntax errors detected.",
                "unused_imports": unused_imports,
                "corrected_code": remove_unused_imports(code),
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