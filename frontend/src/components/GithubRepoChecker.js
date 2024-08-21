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
    <div className="github-repo-checker">
      <h2 className="title">GitHub Repository Checker</h2>
      <div className="input-container">
        <input
          className="repo-input"
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter GitHub repository URL"
        />
        <button className="check-button" onClick={handleCheckRepo}>Check Repository</button>
      </div>
      {result && (
        <div className="result-container">
          <h3 className="section-title">Repository Info:</h3>
          <p><strong>Repository URL:</strong> {result.repository.repository}</p>
          <p><strong>Name:</strong> {result.repository.name}</p>
          <p><strong>Owner:</strong> {result.repository.owner}</p>
          <p><strong>Description:</strong> {result.repository.description}</p>
          <p><strong>Stars:</strong> {result.repository.stars}</p>
          <p><strong>Forks:</strong> {result.repository.forks}</p>
          
          <h3 className="section-title">Code Analysis Results:</h3>
          {Object.keys(result.analysis_results).map((filename) => (
            <div key={filename} className="analysis-result">
              <h4 className="filename">{filename}</h4>
              <p>{result.analysis_results[filename].issue}</p>
              {result.analysis_results[filename].unused_imports && (
                <div className="unused-imports">
                  <p><strong>Unused Imports:</strong></p>
                  <ul>
                    {result.analysis_results[filename].unused_imports.map((imp, index) => (
                      <li key={index}>{imp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}

          <h3 className="section-title">Security Vulnerability Detection:</h3>
          {result.security_vulnerabilities && result.security_vulnerabilities.length > 0 ? (
            result.security_vulnerabilities.map((vulnerability, index) => (
              <div key={index} className="vulnerability">
                <p><strong>Vulnerability:</strong> {vulnerability.issue}</p>
                <p><strong>Description:</strong> {vulnerability.description}</p>
                <p><strong>Severity:</strong> {vulnerability.severity}</p>
              </div>
            ))
          ) : (
            <p>No vulnerabilities detected.</p>
          )}

          {/* Display the commit chart */}
          {result.commit_chart && (
            <div className="commit-chart">
              <h3 className="section-title">Commits per Day:</h3>
              <img src={`data:image/png;base64,${result.commit_chart}`} alt="Commits per Day Chart" />
            </div>
          )}
        </div>
      )}
      {error && <div className="error-message"><p>{error}</p></div>}
    </div>
  );
};

export default GithubRepoChecker;
