export const STAKEHOLDER_KEY = "netaware-ax-stakeholder";
export const STAKEHOLDER_EVENT = "netaware-ax-stakeholder-change";
export const STAKEHOLDERS = ["enterprise", "operator", "aggregator", "explore"];

export function readStakeholder() {
  try {
    const value = sessionStorage.getItem(STAKEHOLDER_KEY);
    return STAKEHOLDERS.includes(value) ? value : "";
  } catch {
    return "";
  }
}

export function writeStakeholder(value) {
  const next = STAKEHOLDERS.includes(value) ? value : "";
  try {
    if (next) sessionStorage.setItem(STAKEHOLDER_KEY, next);
    else sessionStorage.removeItem(STAKEHOLDER_KEY);
  } catch {
    /* private mode */
  }
  window.dispatchEvent(new CustomEvent(STAKEHOLDER_EVENT, { detail: next }));
}

export function startHref(value) {
  if (value === "explore") return "/home";
  if (value === "enterprise" || value === "operator" || value === "aggregator") return `/start/${value}`;
  return "/";
}
