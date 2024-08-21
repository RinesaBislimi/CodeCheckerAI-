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
from io import BytesIO 
import logging
import seaborn as sns

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
    detect_anomalies,
    fetch_commits,
    count_commits_per_day,visualize_commit_counts
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

                # Fix: Missing closing parenthesis
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
                correction_message = (correction_message or "") + " " + (new_correction_message or "")

        return code, correction_message or "Reached maximum iterations, some errors might still be present."

    def visualize_keyword_distribution(self, keyword_data):
        """
        Generate a bar chart visualization of keyword distribution with increased spacing between bars.
        """
        labels = keyword_data['labels']
        data = keyword_data['data']

        fig, ax = plt.subplots(figsize=(14, 8))  # Increased figure size for better spacing
        bars = ax.bar(labels, data, width=0.6)  # Adjust the width of the bars

        ax.set_xlabel('Keywords')
        ax.set_ylabel('Frequency')
        ax.set_title('Keyword Distribution')

        # Add space between bars
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')  # Rotate labels for better readability

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        plt.tight_layout()  # Adjust layout to prevent clipping
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close(fig)

        return image_base64

    def visualize_code_clones_heatmap(self, code_clones):
        """
        Generate a heatmap visualization of code clone similarities.
        """
        snippets = [clone['snippet1'] for clone in code_clones] + [clone['snippet2'] for clone in code_clones]
        similarity_matrix = np.zeros((len(snippets), len(snippets)))

        for i, clone1 in enumerate(code_clones):
            for j, clone2 in enumerate(code_clones):
                similarity_matrix[i, j] = clone1['similarity'] if i == j else clone2['similarity']

        # Create a heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(similarity_matrix, annot=True, cmap='YlGnBu', fmt='.2f', ax=ax)
        plt.title('Code Clones Similarity Heatmap')
        plt.xlabel('Code Snippets')
        plt.ylabel('Code Snippets')
        plt.tight_layout()

        # Save and return the heatmap as an image
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close(fig)

        return image_base64

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
            corrected_code = remove_unused_imports(corrected_code)

            # Analyze the code using various functions
            anomaly_detection_result = detect_anomalies([corrected_code])
            code_clones = detect_code_clones([corrected_code, corrected_code])
            keywords = extract_keywords_from_code(corrected_code)
            code_smells = detect_code_smells(corrected_code)
            deprecated_libraries = detect_deprecated_libraries(corrected_code)
            clusters = detect_code_clusters([corrected_code, corrected_code])

            # Prepare data for visualization
            keyword_distribution = analyze_code(corrected_code, 'keyword_distribution')
            keyword_chart = self.visualize_keyword_distribution(keyword_distribution)
            code_clone_heatmap = self.visualize_code_clones_heatmap(code_clones)

            response_data = {
                "result": correction_message if correction_message else "No syntax errors detected.",
                "unused_imports": unused_imports,
                "corrected_code": corrected_code,
                "anomaly_detection_result": anomaly_detection_result,
                "keywords": keywords,
                "code_smells": code_smells,
                "deprecated_libraries": deprecated_libraries,
                "code_clones": code_clones,
                "clusters": clusters,
                "keyword_chart": keyword_chart,  # Base64 image data for keyword distribution visualization
                "code_clone_heatmap": code_clone_heatmap,  # Base64 image data for code clones heatmap visualization
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
            
            # Fetch and visualize commits
            commits = fetch_commits(repo_url)
            commit_counts = count_commits_per_day(commits)
            commit_chart = visualize_commit_counts(commit_counts)
            
            return Response({
                'repository': repo_info,
                'analysis_results': analysis_results,
                'security_vulnerabilities': security_vulnerabilities,
                'commit_chart': commit_chart,  # Adding commit chart to the response
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class DatasetCheckView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file)
            numeric_features = df.select_dtypes(include=[np.number])
            if numeric_features.empty:
                return Response({'error': 'Dataset does not contain numeric features.'}, status=status.HTTP_400_BAD_REQUEST)
            
            features = numeric_features.values
            
            iso_forest_data = self.detect_anomalies_with_iso_forest(features)
            svm_data = self.detect_anomalies_with_svm(features)
            cluster_graph = self.perform_clustering(features)
            
            return Response({
                **iso_forest_data,
                **svm_data,
                'cluster_graph': cluster_graph
            })

        except pd.errors.EmptyDataError:
            return Response({'error': 'Uploaded file is empty. Please upload a non-empty CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
        except pd.errors.ParserError:
            return Response({'error': 'Error parsing the file. Ensure it is a valid CSV format.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def detect_anomalies_with_iso_forest(self, features):
        model = IsolationForest(contamination=0.1)
        model.fit(features)
        predictions = model.predict(features)
        anomalies = np.where(predictions == -1)[0]
        explanations = [f'Anomaly detected at index {i}' for i in anomalies]
        
        return {
            'num_iso_forest_anomalies': len(anomalies),
            'iso_forest_anomalies': anomalies.tolist(),
            'iso_forest_explanations': explanations,
            'iso_forest_graph': self.generate_anomaly_graph(features, anomalies, 'Isolation Forest')
        }

    def detect_anomalies_with_svm(self, features):
        model = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
        model.fit(features)
        predictions = model.predict(features)
        anomalies = np.where(predictions == -1)[0]
        explanations = [f'Anomaly detected at index {i}' for i in anomalies]
        
        return {
            'num_svm_anomalies': len(anomalies),
            'svm_anomalies': anomalies.tolist(),
            'svm_explanations': explanations,
            'svm_graph': self.generate_anomaly_graph(features, anomalies, 'One-Class SVM')
        }

    def perform_clustering(self, features):
        model = KMeans(n_clusters=3)
        cluster_labels = model.fit_predict(features)
        
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(features[:, 0], features[:, 1], c=cluster_labels, cmap='viridis')
        plt.colorbar(scatter, label='Cluster Label')
        plt.title('KMeans Clustering')
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return img_str

    def generate_anomaly_graph(self, features, anomalies, model_name):
        plt.figure(figsize=(10, 6))
        plt.scatter(range(len(features)), features[:, 0], c='blue', label='Normal')
        plt.scatter(anomalies, features[anomalies, 0], c='red', label='Anomaly')
        plt.title(f'{model_name} Anomaly Detection')
        plt.xlabel('Index')
        plt.ylabel('Feature Value')
        plt.legend()
        plt.grid(True)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return img_str