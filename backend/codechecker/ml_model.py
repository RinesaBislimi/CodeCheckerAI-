import random
import requests
import re
from sklearn.ensemble import IsolationForest
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from .utils import remove_unused_imports

def preprocess_code_for_analysis(code):
    """
    Preprocess code by removing unused imports before further analysis.
    """
    cleaned_code = remove_unused_imports(code)
    return cleaned_code
def analyze_code_snippets(code_snippets):
    """
    Analyze code snippets by first cleaning them and then performing various analyses.
    """
    cleaned_snippets = [preprocess_code_for_analysis(code) for code in code_snippets]
    
    # Proceed with the rest of your analysis using cleaned_snippets
    features = [extract_features_from_code(code) for code in cleaned_snippets]
    features = np.array(features)
    
    # Example anomaly detection
    model = IsolationForest(contamination=0.1)
    model.fit(features)
    
    anomalies = model.predict(features)
    
    return [cleaned_snippets[i] for i, anomaly in enumerate(anomalies) if anomaly == -1]


def reduce_features_with_pca(code_snippets, n_components=2):
    features = [extract_features_from_code(code) for code in code_snippets]
    features = np.array(features)
    
    pca = PCA(n_components=n_components)
    reduced_features = pca.fit_transform(features)
    
    return reduced_features


def detect_code_clusters(code_snippets, n_clusters=5):
    features = [extract_features_from_code(code) for code in code_snippets]
    features = np.array(features)
    
    # Ensure that the number of clusters is not greater than the number of samples
    n_clusters = min(n_clusters, len(code_snippets))
    
    if n_clusters < 1:
        raise ValueError("Number of clusters must be at least 1.")
    
    model = KMeans(n_clusters=n_clusters)
    model.fit(features)
    
    labels = model.labels_
    cluster_centers = model.cluster_centers_
    
    return {
        'labels': labels,
        'cluster_centers': cluster_centers,
    }



# def detect_anomalies_with_svm(code_snippets):
#     features = [extract_features_from_code(code) for code in code_snippets]
#     features = np.array(features)
    
#     model = OneClassSVM(nu=0.1, kernel='rbf', gamma='auto')
#     model.fit(features)
    
#     anomalies = model.predict(features)
    
#     return [code_snippets[i] for i, anomaly in enumerate(anomalies) if anomaly == -1]



def compute_code_embeddings(code_snippets):
    """
    Compute TF-IDF embeddings for a list of code snippets.
    """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(code_snippets)
    return X

def detect_code_clones(code_snippets, threshold=0.9):
    """
    Detect code clones by comparing the similarity of code snippets.
    """
    embeddings = compute_code_embeddings(code_snippets)
    similarity_matrix = cosine_similarity(embeddings)

    clones = []
    num_snippets = len(code_snippets)
    for i in range(num_snippets):
        for j in range(i + 1, num_snippets):
            if similarity_matrix[i, j] > threshold:
                clones.append({
                    'snippet1': code_snippets[i],
                    'snippet2': code_snippets[j],
                    'similarity': similarity_matrix[i, j]
                })
    return clones


def extract_keywords_from_code(code):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([code])
    return vectorizer.get_feature_names_out()


def detect_code_smells(code):
    lines = code.splitlines()
    metrics = {
        'line_count': len(lines),
        'method_count': code.count('def '),
        'complexity': sum(line.count('if ') + line.count('else') for line in lines)
    }
    
    smells = []
    if metrics['line_count'] > 100:
        smells.append('High line count')
    if metrics['method_count'] > 10:
        smells.append('Too many methods')
    if metrics['complexity'] > 20:
        smells.append('High complexity')

    return smells


DEPRECATED_LIBRARIES = {'oldlib': '1.0.0'}

def detect_deprecated_libraries(code):
    deprecated = []
    for lib, version in DEPRECATED_LIBRARIES.items():
        if lib in code:
            deprecated.append({
                'library': lib,
                'version': version,
                'description': 'This library is deprecated. Consider updating.'
            })
    return deprecated



def analyze_code(code, visualization_type):
    # Extract keywords from the code
    keywords = re.findall(r'\b\w+\b', code)
    # Count the frequency of each keyword
    keyword_counts = Counter(keywords)
    
    # Prepare analysis results
    labels = list(keyword_counts.keys())
    data = list(keyword_counts.values())
    
    return {
        'labels': labels,
        'data': data,
    }


def analyze_github_repo(repo_url):
    # Regular expression to match GitHub repository URL in various formats
    pattern = re.compile(r'^https://github\.com/([^/]+)/([^/]+)(?:\.git)?$', re.IGNORECASE)
    match = pattern.match(repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL. URL should be in the format 'https://github.com/owner/repo'.")
    
    owner, repo = match.groups()
    
    # Construct the GitHub API URL
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    try:
        # Fetch repository information
        response = requests.get(api_url)
        response.raise_for_status()  # Check if request was successful
        repo_data = response.json()
        
        # Extract and return relevant repository data
        analysis_result = {
            'repository': repo_url,
            'name': repo_data.get('name', 'No name available'),
            'owner': repo_data.get('owner', {}).get('login', 'No owner available'),
            'description': repo_data.get('description', 'No description available'),
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0),
        }
        
        return analysis_result
    
    except requests.RequestException as e:
        raise ValueError(f"Error fetching repository data: {e}")
    
    
def fetch_repo_contents(repo_url):
    # Extract owner and repo from the URL
    pattern = re.compile(r'https://github\.com/([^/]+)/([^/]+)', re.IGNORECASE)
    match = pattern.match(repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL.")
    
    owner, repo = match.groups()
    
    # GitHub API URL for repository contents
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Check if request was successful
        contents = response.json()
        
        # Extract file content from the response
        files = [item for item in contents if item['type'] == 'file']
        file_contents = {}
        
        for file in files:
            file_url = file['download_url']
            file_response = requests.get(file_url)
            file_contents[file['name']] = file_response.text
        
        return file_contents
    
    except requests.RequestException as e:
        raise ValueError(f"Error fetching repository contents: {e}")
    
    
    
def analyze_code_contents(code_contents):
    # Example analysis function
    analysis_results = {}
    
    for filename, content in code_contents.items():
        # Perform static code analysis (e.g., linting, syntax checks)
        if 'import' in content:
            analysis_results[filename] = "Contains import statements. Check for unused imports."
        else:
            analysis_results[filename] = "No issues detected."
    
    return analysis_results


def detect_security_vulnerabilities(code_contents):

    vulnerabilities = []
    for filename, code in code_contents.items():
        if "eval(" in code:
            vulnerabilities.append({
                'issue': 'Use of eval()',
                'description': 'The use of eval() is dangerous as it can execute arbitrary code.',
                'severity': 'High'
            })
    return vulnerabilities



def extract_features_from_code(code):
    """
    Basic feature extraction function for code.
    For demonstration purposes, this function calculates simple features such as the number of lines and the length of each line.
    
    Parameters:
    - code (str): The code to extract features from.
    
    Returns:
    - features (list): A list of features extracted from the code.
    """
    if isinstance(code, list):
        code = "\n".join(code)  # Join list items into a single string
    
    lines = code.split('\n')
    num_lines = len(lines)
    line_lengths = [len(line) for line in lines]
    avg_line_length = np.mean(line_lengths) if line_lengths else 0
    
    return [num_lines, avg_line_length]

def detect_anomalies(user_code):
    """
    Detect anomalies in the provided code using Isolation Forest.
    
    Parameters:
    - user_code (str): The code provided by the user.
    
    Returns:
    - result (str): Message indicating whether the code contains anomalies.
    """
    
    # Extract features from the provided code
    features = extract_features_from_code(user_code)
    features = np.array([features])
    
    # Initialize IsolationForest model
    model = IsolationForest(contamination=0.1)
    model.fit(features)
    
    # Predict anomaly
    anomaly = model.predict(features)[0]
    
    # Determine and return result
    if anomaly == -1:
        return 'Anomaly detected in the code.'
    else:
        return 'No anomalies detected.'
    
    
