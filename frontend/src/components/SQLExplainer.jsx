import React, { useState } from "react";
import { explainSQL } from "../api";

export default function SQLExplainer({ sql }) {
  const [open, setOpen] = useState(false);
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!sql) return null;

  const handleExplain = async () => {
    if (explanation) {
      setOpen((o) => !o);
      return;
    }
    setOpen(true);
    setLoading(true);
    try {
      const data = await explainSQL(sql);
      setExplanation(data.explanation);
    } catch {
      setExplanation("Could not generate explanation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="explainer-section">
      <div className="explainer-header">
        <span className="explainer-title">🔍 SQL Generated</span>
        <div className="explainer-actions">
          <button className="explainer-btn" onClick={handleCopy}>
            {copied ? "✓ Copied!" : "Copy SQL"}
          </button>
          <button className="explainer-btn accent" onClick={handleExplain}>
            {open ? "Hide Explanation" : "What does this mean? →"}
          </button>
        </div>
      </div>

      <pre className="sql-code">{sql}</pre>

      {open && (
        <div className="explanation-box">
          {loading ? (
            <div className="explanation-loading">
              <span className="spinner dark" />
              <span>Explaining in plain English...</span>
            </div>
          ) : (
            <p className="explanation-text">💡 {explanation}</p>
          )}
        </div>
      )}
    </div>
  );
}
