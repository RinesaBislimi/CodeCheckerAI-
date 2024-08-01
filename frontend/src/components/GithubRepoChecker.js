import React, { useState } from 'react';
import axios from 'axios';
import './GithubRepoChecker.css';

const GithubRepoChecker = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleCheckRepo = async () => {
    setResult(null);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/check-repo/', { repo_url: repoUrl });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'There was an error checking the repository. Please try again.');
    }
  };

  return (
    <div>
      <h2>GitHub Repository Checker</h2>
      <input
        type="text"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="Enter GitHub repository URL"
      />
      <button onClick={handleCheckRepo}>Check Repository</button>
      {result && (
        <div>
          <h3>Repository Info:</h3>
          <p><strong>Repository URL:</strong> {result.repository.repository}</p>
          <p><strong>Name:</strong> {result.repository.name}</p>
          <p><strong>Owner:</strong> {result.repository.owner}</p>
          <p><strong>Description:</strong> {result.repository.description}</p>
          <p><strong>Stars:</strong> {result.repository.stars}</p>
          <p><strong>Forks:</strong> {result.repository.forks}</p>
          
          <h3>Code Analysis Results:</h3>
          {Object.keys(result.analysis_results).map((filename) => (
            <div key={filename}>
              <h4>{filename}</h4>
              <p>{result.analysis_results[filename]}</p>
            </div>
          ))}
        </div>
      )}
      {error && <div style={{ color: 'red' }}><p>{error}</p></div>}
    </div>
  );
};

export default GithubRepoChecker;
