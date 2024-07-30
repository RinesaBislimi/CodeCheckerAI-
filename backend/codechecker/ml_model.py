import random
import requests
import re


def analyze_code(code, visualization_type):

    labels = ['Function A', 'Function B', 'Function C']
    data = [random.randint(0, 10) for _ in range(3)]

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
