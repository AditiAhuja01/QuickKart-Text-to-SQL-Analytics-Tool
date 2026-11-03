import React, { useEffect, useState } from "react";
import { getSuggestions } from "../api";

// These questions are shown immediately so the page is never blank.
// If the backend responds with its own list, those replace these.
const FALLBACK_SUGGESTIONS = [
  "Which products are below reorder level?",
  "Show top 10 customers by loyalty points",
  "What is total revenue this month?",
  "Which cashier processed the most orders?",
  "Which products were returned the most?",
];

export default function Suggestions({ onSelect }) {
  // Start with the fallback list so something always shows on load
  const [suggestions, setSuggestions] = useState(FALLBACK_SUGGESTIONS);

  useEffect(() => {
    getSuggestions()
      .then((data) => {
        // Only replace the fallback if the backend gives a valid non-empty list
        if (data.suggestions && data.suggestions.length > 0) {
          setSuggestions(data.suggestions);
        }
      })
      .catch(() => {
        // Backend is unreachable or REACT_APP_API_URL is wrong.
        // Keep the fallback — the page stays usable.
      });
  }, []);

  if (!suggestions.length) return null;

  return (
    <div className="suggestions-section">
      <p className="suggestions-label"> Try asking</p>
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
