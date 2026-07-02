// All requests are same-origin; nginx (prod) or Vite proxy (dev) routes /api.

export async function shortenUrl(url) {
  const res = await fetch("/api/shorten", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Failed to shorten URL");
  return data;
}

export async function getStats(code) {
  const res = await fetch(`/api/stats/${code}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Failed to load stats");
  return data;
}
