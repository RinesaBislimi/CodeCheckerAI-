import random
import requests
import re
from sklearn.ensemble import IsolationForest
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import OneClassSVM
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
from .utils import remove_unused_imports
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os


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
    
    features = [extract_features_from_code(code) for code in cleaned_snippets]
    features = np.array(features)
    
    model = IsolationForest(contamination=0.1)
    model.fit(features)
    
    anomalies = model.predict(features)
    
    return [cleaned_snippets[i] for i, anomaly in enumerate(anomalies) if anomaly == -1]

def reduce_features_with_pca(code_snippets, n_components=2):
    """
    Reduce feature dimensionality using PCA.
    """
    features = [extract_features_from_code(code) for code in code_snippets]
    features = np.array(features)
    
    pca = PCA(n_components=n_components)
    reduced_features = pca.fit_transform(features)
    
    return reduced_features

def detect_code_clusters(code_snippets, n_clusters=5):
    """
    Detect clusters in code snippets using KMeans.
    """
    features = [extract_features_from_code(code) for code in code_snippets]
    features = np.array(features)
    
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
    """
    Extract keywords from a single code snippet.
    """
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([code])
    return vectorizer.get_feature_names_out()

def detect_code_smells(code):
    """
    Detect code smells in a single code snippet.
    """
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
    """
    Detect deprecated libraries used in the code.
    """
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
    """
    Analyze a single code snippet and prepare data for visualization.
    """
    keywords = re.findall(r'\b\w+\b', code)
    keyword_counts = Counter(keywords)
    
    labels = list(keyword_counts.keys())
    data = list(keyword_counts.values())
    
    return {
        'labels': labels,
        'data': data,
    }

def analyze_github_repo(repo_url):
    """
    Analyze a GitHub repository by fetching and returning relevant data.
    """
    pattern = re.compile(r'^https://github\.com/([^/]+)/([^/]+)(?:\.git)?$', re.IGNORECASE)
    match = pattern.match(repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL. URL should be in the format 'https://github.com/owner/repo'.")
    
    owner, repo = match.groups()
    
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        repo_data = response.json()
        
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
    """
    Fetch the contents of a GitHub repository.
    """
    pattern = re.compile(r'https://github\.com/([^/]+)/([^/]+)', re.IGNORECASE)
    match = pattern.match(repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL.")
    
    owner, repo = match.groups()
    
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        contents = response.json()
        
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
    """
    Analyze the contents of code files from a repository.
    """
    analysis_results = {}
    
    for filename, content in code_contents.items():
        if 'import' in content:
            analysis_results[filename] = "Contains import statements. Check for unused imports."
        else:
            analysis_results[filename] = "No issues detected."
    
    return analysis_results

def detect_security_vulnerabilities(code_contents):
    """
    Detect security vulnerabilities in code contents.
    """
    vulnerabilities = []
    for filename, code in code_contents.items():
        if "eval(" in code:
            vulnerabilities.append({
                'issue': 'Use of eval()',
                'description': 'The use of eval() is dangerous as it can execute arbitrary code.',
                'severity': 'High'
            })
    return vulnerabilities

def extract_features_from_code(code: str) -> dict:
    """
    Extract features from the code snippet.
    """
    if not isinstance(code, str):
        raise TypeError("Expected code to be a string.")
    
    num_lines = len(code.split('\n'))
    line_lengths = [len(line) for line in code.split('\n')]
    avg_line_length = np.mean(line_lengths) if line_lengths else 0
    num_imports = code.count('import ')
    num_functions = code.count('def ')
    
    return [num_lines, avg_line_length, num_imports, num_functions]

def detect_anomalies(user_code):
    """
    Detect anomalies in code using Isolation Forest.
    """
    if isinstance(user_code, list):
        user_code = '\n'.join(user_code)
    
    if not isinstance(user_code, str):
        raise TypeError("user_code should be a string or a list of strings.")
    
    features = extract_features_from_code(user_code)
    features = np.array([features])
    
    model = IsolationForest(contamination=0.1)
    model.fit(features)
    
    anomaly = model.predict(features)
    
    return anomaly[0] == -1

def detect_code_clones(code_snippets):
    """
    Detect code clones by comparing the similarity of code snippets.
    """
    embeddings = compute_code_embeddings(code_snippets)
    similarity_matrix = cosine_similarity(embeddings)

    clones = []
    num_snippets = len(code_snippets)
    for i in range(num_snippets):
        for j in range(i + 1, num_snippets):
            if similarity_matrix[i, j] > 0.9:
                clones.append({
                    'snippet1': code_snippets[i],
                    'snippet2': code_snippets[j],
                    'similarity': similarity_matrix[i, j]
                })
    return clones

def fetch_commits(repo_url):
    """
    Fetch commits from the provided GitHub repository URL.
    """
    if repo_url.startswith('https://github.com/'):
        repo_path = repo_url[len('https://github.com/'):]
    else:
        raise ValueError('Invalid GitHub repository URL')

    api_url = f'https://api.github.com/repos/{repo_path}/commits'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error fetching commits: {response.status_code} Client Error")

def count_commits_per_day(commits):
    """
    Count the number of commits per day from a list of commit data.
    """
    commit_dates = [commit['commit']['committer']['date'][:10] for commit in commits]
    date_counts = defaultdict(int)
    
    for date in commit_dates:
        date_counts[date] += 1
    
    return dict(date_counts)

def visualize_commit_counts(commit_counts):
    """
    Visualize the number of commits per day.
    """
    if not commit_counts:
        return None
    
    dates = list(commit_counts.keys())
    counts = list(commit_counts.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(dates, counts)
    plt.xlabel('Date')
    plt.ylabel('Number of Commits')
    plt.title('Number of Commits per Day')
    plt.xticks(rotation=45)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return plot_data