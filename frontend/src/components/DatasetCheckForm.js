import React, { useState } from 'react';
import axios from 'axios';
import './DatasetCheckForm.css';
import { Tooltip } from 'react-tooltip';

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
            data-tip="Upload your CSV file here"
          />
          <Tooltip />
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
            <p>
              <strong>Number of Anomalies (Isolation Forest):</strong> {result.num_iso_forest_anomalies || 'N/A'}
            </p>
            <p>
              <strong>Anomalies (Isolation Forest):</strong> {result.iso_forest_anomalies ? result.iso_forest_anomalies.join(', ') : 'N/A'}
            </p>
            <p>
              <strong>Explanations (Isolation Forest):</strong> {result.iso_forest_explanations ? result.iso_forest_explanations.join(' | ') : 'N/A'}
            </p>
            <p>
              <strong>Number of Anomalies (One-Class SVM):</strong> {result.num_svm_anomalies || 'N/A'}
            </p>
            <p>
              <strong>Anomalies (One-Class SVM):</strong> {result.svm_anomalies ? result.svm_anomalies.join(', ') : 'N/A'}
            </p>
            <p>
              <strong>Explanations (One-Class SVM):</strong> {result.svm_explanations ? result.svm_explanations.join(' | ') : 'N/A'}
            </p>
            {result.iso_forest_graph && (
              <div className="anomaly-graph">
                <h3>Isolation Forest Anomaly Graph</h3>
                <img src={`data:image/png;base64,${result.iso_forest_graph}`} alt="Isolation Forest Anomaly Graph" data-tip="Isolation Forest Anomaly Graph" />
                <Tooltip />
              </div>
            )}
            {result.svm_graph && (
              <div className="anomaly-graph">
                <h3>One-Class SVM Anomaly Graph</h3>
                <img src={`data:image/png;base64,${result.svm_graph}`} alt="One-Class SVM Anomaly Graph" data-tip="One-Class SVM Anomaly Graph" />
                <Tooltip />
              </div>
            )}
            {result.cluster_graph && (
              <div className="cluster-graph">
                <h3>KMeans Clustering</h3>
                <img src={`data:image/png;base64,${result.cluster_graph}`} alt="KMeans Clustering" data-tip="KMeans Clustering" />
                <Tooltip />
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
