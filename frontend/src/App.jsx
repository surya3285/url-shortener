import { useState } from "react";
import { shortenUrl, getStats } from "./api.js";

export default function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setStats(null);
    setResult(null);
    setCopied(false);
    setLoading(true);
    try {
      const data = await shortenUrl(url.trim());
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function copyLink() {
    if (!result) return;
    const text = result.short_url;

    // navigator.clipboard only works in secure contexts (https / localhost).
    // Over plain http (e.g. an EC2 IP) it's undefined, so fall back to a
    // temporary textarea + execCommand, which works everywhere.
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("Couldn't copy automatically — please copy the link manually.");
    }
  }

  async function loadStats() {
    if (!result) return;
    setError("");
    try {
      setStats(await getStats(result.code));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <h1>URL Shortener</h1>
      <p className="subtitle">Paste a long link, get a short one.</p>

      <form onSubmit={handleSubmit} className="form">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/very/long/link"
          aria-label="URL to shorten"
        />
        <button type="submit" disabled={loading || !url.trim()}>
          {loading ? "Shortening…" : "Shorten"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="card">
          <div className="short-row">
            <a href={result.short_url} target="_blank" rel="noreferrer">
              {result.short_url}
            </a>
            <button className="ghost" onClick={copyLink}>
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <div className="original">→ {result.original_url}</div>
          <button className="ghost" onClick={loadStats}>
            View click stats
          </button>
        </div>
      )}

      {stats && (
        <div className="card stats">
          <h2>Stats for /{stats.code}</h2>
          <p>
            <strong>{stats.click_count}</strong> total clicks
          </p>
          <p className="muted">
            Created {new Date(stats.created_at).toLocaleString()}
          </p>
          {stats.recent_clicks.length > 0 ? (
            <>
              <p className="muted">Recent clicks:</p>
              <ul>
                {stats.recent_clicks.map((t, i) => (
                  <li key={i}>{new Date(t).toLocaleString()}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="muted">No clicks yet.</p>
          )}
        </div>
      )}
    </div>
  );
}
