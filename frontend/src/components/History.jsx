import React, { useEffect, useState } from "react";
import { getHistory, clearHistory } from "../api";

export default function History({ onSelect, refreshTrigger }) {
  const [history, setHistory] = useState([]);
  const [open, setOpen] = useState(false);

  const load = () => {
    getHistory()
      .then((data) => setHistory(data.history || []))
      .catch(() => {});
  };

  useEffect(() => {
    load();
  }, [refreshTrigger]);

  const handleClear = async () => {
    if (!window.confirm("Clear all history?")) return;
    await clearHistory();
    setHistory([]);
  };

  const formatTime = (ts) => {
    const d = new Date(ts);
    return d.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className={`history-panel ${open ? "open" : ""}`}>
      <button className="history-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "✕" : "📋"}{" "}
        {!open && history.length > 0 && (
          <span className="history-badge">{history.length}</span>
        )}
      </button>

      {open && (
        <div className="history-content">
          <div className="history-panel-header">
            <span>Query History</span>
            {history.length > 0 && (
              <button className="clear-btn" onClick={handleClear}>
                Clear
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <p className="history-empty">No queries yet. Ask something!</p>
          ) : (
            <ul className="history-list">
              {history.map((item) => (
                <li
                  key={item.id}
                  className="history-item"
                  onClick={() => {
                    onSelect(item.question);
                    setOpen(false);
                  }}
                >
                  <p className="history-question">{item.question}</p>
                  <div className="history-meta">
                    <span>{item.result_count} rows</span>
                    <span>{formatTime(item.created_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
