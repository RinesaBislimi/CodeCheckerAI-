import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Welcome to CodeCheckerAI</h1>
      <div className="options">
        <Link to="/check-code" className="option-card">
          <h2>Check Code Snippet</h2>
          <p>Analyze a single code snippet for issues and improvements.</p>
        </Link>
        <Link to="/check-repo" className="option-card">
          <h2>Check GitHub Repo</h2>
          <p>Analyze an entire GitHub repository for code quality and issues.</p>
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
