import React, { useState } from 'react';
import axios from 'axios';
import './CodeCheckerForm.css';

const CodeCheckerForm = () => {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [correctedCode, setCorrectedCode] = useState('');
  const [unusedImports, setUnusedImports] = useState([]);
  const [anomalyDetectionResult, setAnomalyDetectionResult] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [codeSmells, setCodeSmells] = useState([]);
  const [deprecatedLibraries, setDeprecatedLibraries] = useState([]);
  const [codeClones, setCodeClones] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setCorrectedCode('');
    setUnusedImports([]);
    setAnomalyDetectionResult('');
    setKeywords([]);
    setCodeSmells([]);
    setDeprecatedLibraries([]);
    setCodeClones([]);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/check/', { code });
      setResult(response.data.result || 'No syntax errors detected.');
      setCorrectedCode(response.data.corrected_code || code);
      setUnusedImports(response.data.unused_imports || []);
      setAnomalyDetectionResult(response.data.anomaly_detection_result || 'No anomalies detected.');
      setKeywords(response.data.keywords || []);
      setCodeSmells(response.data.code_smells || []);
      setDeprecatedLibraries(response.data.deprecated_libraries || []);
      setCodeClones(response.data.code_clones || []);
    } catch (err) {
      setError('There was an error checking your code. Please try again.');
    }
  };

  return (
    <div className="code-checker">
      <h1 className="header">Code Checker</h1>
      <form onSubmit={handleSubmit}>
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
          <br />
          <button className="submit-button" type="submit">Check Code</button>
        </div>
      </form>
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
        {anomalyDetectionResult && (
          <div className="anomaly-detection">
            <h3 className="section-title">Anomaly Detection</h3>
            <p>{anomalyDetectionResult}</p>
          </div>
        )}
        {keywords.length > 0 && (
          <div className="keywords">
            <h3 className="section-title">Keywords</h3>
            <ul>
              {keywords.map((keyword, index) => (
                <li key={index}>{keyword}</li>
              ))}
            </ul>
          </div>
        )}
        {codeSmells.length > 0 && (
          <div className="code-smells">
            <h3 className="section-title">Code Smells</h3>
            <ul>
              {codeSmells.map((smell, index) => (
                <li key={index}>{smell}</li>
              ))}
            </ul>
          </div>
        )}
        {deprecatedLibraries.length > 0 && (
          <div className="deprecated-libraries">
            <h3 className="section-title">Deprecated Libraries</h3>
            <ul>
              {deprecatedLibraries.map((lib, index) => (
                <li key={index}>{lib.library} ({lib.version}): {lib.description}</li>
              ))}
            </ul>
          </div>
        )}
        {codeClones.length > 0 && (
          <div className="code-clones">
            <h3 className="section-title">Code Clones</h3>
            <ul>
              {codeClones.map((clone, index) => (
                <li key={index}>
                  <p>Snippet 1: {clone.snippet1}</p>
                  <p>Snippet 2: {clone.snippet2}</p>
                  <p>Similarity: {clone.similarity.toFixed(2)}</p>
                </li>
              ))}
            </ul>
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
