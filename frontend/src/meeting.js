import { writeLens } from "./lens.jsx";
import { writeStakeholder } from "./stakeholder.js";
import { apiPost } from "./api.js";

export const MEET_DEPTH_KEY = "netaware-ax-meet-depth";
export const MEET_CUES_KEY = "netaware-ax-meet-cues";
export const MEET_EVENT = "netaware-ax-meet-change";

export function readMeetDepth() {
  try {
    const value = sessionStorage.getItem(MEET_DEPTH_KEY);
    return ["exec", "sales", "tech"].includes(value) ? value : "";
  } catch {
    return "";
  }
}

export function writeMeetDepth(value) {
  const next = ["exec", "sales", "tech"].includes(value) ? value : "";
  try {
    if (next) sessionStorage.setItem(MEET_DEPTH_KEY, next);
    else sessionStorage.removeItem(MEET_DEPTH_KEY);
  } catch {
    /* private mode */
  }
  window.dispatchEvent(new CustomEvent(MEET_EVENT, { detail: { depth: next } }));
}

export function readCuesHidden() {
  try {
    return sessionStorage.getItem(MEET_CUES_KEY) !== "show";
  } catch {
    return true;
  }
}

export function writeCuesHidden(hidden) {
  try {
    sessionStorage.setItem(MEET_CUES_KEY, hidden ? "hide" : "show");
  } catch {
    /* private mode */
  }
  window.dispatchEvent(new CustomEvent(MEET_EVENT, { detail: { cues: hidden } }));
}

export async function resetDemo() {
  writeStakeholder("");
  writeLens("BASIC");
  writeMeetDepth("");
  writeCuesHidden(true);
  try {
    await apiPost("/executions/reset", {});
  } catch {
    /* empty store is fine */
  }
  window.location.hash = "#/";
}
