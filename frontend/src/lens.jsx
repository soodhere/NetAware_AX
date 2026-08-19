export const LENS_KEY = "netaware-ax-presentation-lens";
export const LENS_EVENT = "netaware-ax-lens-change";

export function readLens() {
  try {
    return sessionStorage.getItem(LENS_KEY) === "ADVANCED" ? "ADVANCED" : "BASIC";
  } catch {
    return "BASIC";
  }
}

export function writeLens(lens) {
  const next = lens === "ADVANCED" ? "ADVANCED" : "BASIC";
  try {
    sessionStorage.setItem(LENS_KEY, next);
  } catch {
    /* private mode */
  }
  window.dispatchEvent(new CustomEvent(LENS_EVENT, { detail: next }));
}

export function LensToggle({ lens, onChange }) {
  return (
    <div className="lens-toggle" role="group" aria-label="Presentation lens">
      <button
        type="button"
        className={lens === "BASIC" ? "on" : ""}
        onClick={() => onChange("BASIC")}
      >
        BASIC — Business View
      </button>
      <button
        type="button"
        className={lens === "ADVANCED" ? "on" : ""}
        onClick={() => onChange("ADVANCED")}
      >
        ADVANCED — Technical View
      </button>
    </div>
  );
}
