import React, { useState } from 'react';
import axios from 'axios';
import './CodeCheckerForm.css';

const CodeCheckerForm = () => {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [correctedCode, setCorrectedCode] = useState('');
  const [unusedImports, setUnusedImports] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setCorrectedCode('');
    setUnusedImports([]);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/check/', { code });
      setResult(response.data.result);
      setCorrectedCode(response.data.corrected_code || code);
      setUnusedImports(response.data.unused_imports || []);
    } catch (err) {
      setError('There was an error checking your code. Please try again.');
    }
  };

  return (
    <div className="code-checker">
      <h1 className="header">Code Checker</h1>
      <div className="code-input">
        <h2 className="section-title">Input Code</h2>
        <textarea
          className="code-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Enter your Python code here"
          rows="10"
          cols="70"
        />
        <br></br>
        <button className="submit-button" type="submit" onClick={handleSubmit}>Check Code</button>
      </div>
      <div className="code-output">
        <h2 className="section-title">Output</h2>
        {result && (
          <div className="result">
            <p>{result}</p>
          </div>
        )}
        {unusedImports.length > 0 && (
          <div className="unused-imports">
            <h3 className="section-title">Unused Imports</h3>
            <ul>
              {unusedImports.map((imp, index) => (
                <li key={index}>{imp}</li>
              ))}
            </ul>
          </div>
        )}
        {correctedCode && (
          <div className="corrected-code">
            <h3 className="section-title">Corrected Code</h3>
            <pre>{correctedCode}</pre>
          </div>
        )}
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeCheckerForm;
