import React, { useState } from "react";

export default function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSearch(input.trim());
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <div className="search-wrapper">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder='Ask anything... e.g. "Which products are low on stock?"'
          className="search-input"
          disabled={loading}
          autoFocus
        />
        <button type="submit" className="search-btn" disabled={loading || !input.trim()}>
          {loading ? (
            <span className="spinner" />
          ) : (
            "Ask →"
          )}
        </button>
      </div>
    </form>
  );
}
