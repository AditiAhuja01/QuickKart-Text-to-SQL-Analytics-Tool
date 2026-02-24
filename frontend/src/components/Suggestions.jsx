import React, { useEffect, useState } from "react";
import { getSuggestions } from "../api";

export default function Suggestions({ onSelect }) {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    getSuggestions()
      .then((data) => setSuggestions(data.suggestions))
      .catch(() => {});
  }, []);

  if (!suggestions.length) return null;

  return (
    <div className="suggestions-section">
      <p className="suggestions-label">✨ Try asking</p>
      <div className="suggestions-grid">
        {suggestions.map((s, i) => (
          <button
            key={i}
            className="suggestion-chip"
            onClick={() => onSelect(s)}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
