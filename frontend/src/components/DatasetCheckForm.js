import React, { useState } from 'react';
import axios from 'axios';
import './DatasetCheckForm.css';

const DatasetCheckForm = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setError(null);

    if (!file) {
      setError('Please upload a dataset file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/check-dataset/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'There was an error checking your dataset. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dataset-checker">
      <h1 className="header">Dataset Checker</h1>
      <form onSubmit={handleSubmit}>
        <div className="file-input">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
          />
          <br />
          <button className="submit-button" type="submit" disabled={loading}>
            {loading ? 'Checking...' : 'Check Dataset'}
          </button>
        </div>
      </form>
      <div className="dataset-output">
        {result && (
          <div className="result">
            <h2>Results</h2>
            <p><strong>Number of Anomalies:</strong> {result.num_anomalies}</p>
            <p><strong>Anomalies:</strong> {result.anomalies.join(', ')}</p>
            {result.anomalous_rows && (
              <div className="anomalous-rows">
                <h3>Anomalous Rows</h3>
                <ul>
                  {result.anomalous_rows.map((row, idx) => (
                    <li key={idx}>
                      <strong>Row {row.index}:</strong> {JSON.stringify(row.row)}
                      <br />
                      <strong>Explanation:</strong> {JSON.stringify(row.explanation)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.anomaly_graph && (
              <div className="anomaly-graph">
                <h3>Anomaly Graph</h3>
                <img src={`data:image/png;base64,${result.anomaly_graph}`} alt="Anomaly Graph" />
              </div>
            )}
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

export default DatasetCheckForm;
