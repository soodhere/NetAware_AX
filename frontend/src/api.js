export async function api(path) {
  const res = await fetch(path, { credentials: "same-origin" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}${text ? `: ${text}` : ""}`);
  }
  return res.json();
}

export async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}${text ? `: ${text}` : ""}`);
  }
  return res.json();
}

export function href(path) {
  return `#${path.startsWith("/") ? path : `/${path}`}`;
}

export function maturityTone(value) {
  const v = String(value || "").toLowerCase();
  if (v === "experimental") return "warn";
  if (v === "incubating") return "accent";
  if (v === "stable") return "ok";
  return "";
}

export function apiVersionMaturityTone(value) {
  const v = String(value || "").toUpperCase();
  if (v.includes("EXPERIMENTAL")) return "warn";
  if (v.includes("INITIAL") || v.includes("PRE-STABLE")) return "accent";
  if (v.includes("STABLE")) return "ok";
  return "";
}

export function formatList(value) {
  if (Array.isArray(value)) return value.filter(Boolean).join(" · ");
  return value || "";
}
