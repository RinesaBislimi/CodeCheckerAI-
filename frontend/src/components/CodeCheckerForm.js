import React, { useState } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeCheckerForm.css';

const CodeCheckerForm = () => {
  const [code, setCode] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [result, setResult] = useState(null);
  const [correctedCode, setCorrectedCode] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setCorrectedCode('');
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/check/', { code, githubUrl });
      setResult(response.data.result);
      setCorrectedCode(response.data.corrected_code || code);
    } catch (err) {
      setError('There was an error checking your code. Please try again.');
    }
  };

  return (
    <div className="code-checker">
      <h1>Code Checker</h1>
      <div className="code-input-output">
        <div className="code-input">
          <h2>Input Code</h2>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Enter your Python code here"
            rows="10"
            cols="50"
          />
          <input
            type="text"
            placeholder="Enter GitHub repo URL"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            className="github-input"
          />
          <br />
          <button type="submit" onClick={handleSubmit}>Check Code</button>
        </div>
        <div className="code-output">
          <h2>Output</h2>
          {result && (
            <div className="result">
              <p>{result}</p>
            </div>
          )}
          {correctedCode && (
            <div className="corrected-code">
              <h3>Corrected Code</h3>
              <SyntaxHighlighter language="python" style={vscDarkPlus}>
                {correctedCode}
              </SyntaxHighlighter>
            </div>
          )}
          {error && (
            <div className="error" style={{ color: 'red' }}>
              <p>{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeCheckerForm;
