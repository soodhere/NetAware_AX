export async function api(path) {
  const res = await fetch(path);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}${text ? `: ${text}` : ""}`);
  }
  return res.json();
}

export async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
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
