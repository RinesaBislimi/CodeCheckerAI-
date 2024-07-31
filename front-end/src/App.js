import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './components/HomePage';
import CodeCheckerForm from './components/CodeCheckerForm';
import GithubRepoChecker from './components/GithubRepoChecker'; // Assume you have this component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/check-code" element={<CodeCheckerForm />} />
        <Route path="/check-repo" element={<GithubRepoChecker />} />
      </Routes>
    </Router>
  );
}

export default App;
