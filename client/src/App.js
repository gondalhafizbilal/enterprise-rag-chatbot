import React, { useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleIngest() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_URL}/ingest`, {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    alert(`Ingested: ${data.message}`);
  }

  async function handleQuery() {
    setLoading(true);
    setAnswer("");
    const res = await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q }),
    });
    const data = await res.json();
    setAnswer(data.answer || JSON.stringify(data));
    setLoading(false);
  }

  return (
    <div
      style={{
        maxWidth: 800,
        margin: "2rem auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Company Knowledge Chatbot</h1>

      <section style={{ marginTop: 24 }}>
        <h3>Upload & Ingest</h3>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button
          onClick={handleIngest}
          disabled={!file}
          style={{ marginLeft: 8 }}
        >
          Ingest
        </button>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Ask a Question</h3>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="e.g., What is our WFH policy?"
          style={{ width: "100%", padding: 8 }}
        />
        <button
          onClick={handleQuery}
          disabled={!q || loading}
          style={{ marginTop: 8 }}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
        <pre
          style={{
            whiteSpace: "pre-wrap",
            background: "#f6f6f6",
            padding: 12,
            marginTop: 12,
          }}
        >
          {answer}
        </pre>
      </section>
    </div>
  );
}

export default App;
