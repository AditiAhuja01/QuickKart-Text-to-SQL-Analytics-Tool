import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Suggestions from "./components/Suggestions";
import ResultsTable from "./components/ResultsTable";
import SQLExplainer from "./components/SQLExplainer";
import History from "./components/History";
import SchemaExplorer from "./components/SchemaExplorer";
import { askQuestion } from "./api";
import "./App.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [historyRefresh, setHistoryRefresh] = useState(0);

  // This runs only when the user submits a question.
  // It does NOT run on page load — so the page is never blank on load.
  const handleSearch = async (question) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await askQuestion(question);
      setResult(data);
      setHistoryRefresh((n) => n + 1); // trigger history panel reload
    } catch (err) {
      // Only show an error if the user actually submitted something
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div>
              <span className="logo-name">QuickKart</span>
              <span className="logo-tag">Domain: Retail Analytics</span>
            </div>
          </div>
          <p className="header-tagline">
            Ask questions in plain English. Get instant data answers.
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="main">

        {/* Search bar */}
        <SearchBar onSearch={handleSearch} loading={loading} />

        {/* Loading indicator */}
        {loading && (
          <div className="loading-state">
            <div className="loading-dots">
              <span /><span /><span />
            </div>
            <p>Generating your query...</p>
          </div>
        )}

        {/* Error message — only shows after a failed user query */}
        {error && (
          <div className="error-box">
            <span></span>
            <p>{error}</p>
          </div>
        )}

        {/* Results — only shows after a successful user query */}
        {result && !loading && (
          <>
            <SQLExplainer sql={result.sql} />
            <ResultsTable data={result} />
          </>
        )}

        {/* Suggested questions — shown when no result and no error yet */}
        {!result && !loading && !error && (
          <Suggestions onSelect={handleSearch} />
        )}

      </main>

      {/* Floating side panels — always visible, load independently */}
      <History onSelect={handleSearch} refreshTrigger={historyRefresh} />
      <SchemaExplorer />
    </div>
  );
}
