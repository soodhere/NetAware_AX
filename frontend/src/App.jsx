import { useEffect, useState } from "react";
import { href } from "./api.js";
import Close from "./pages/Close.jsx";
import Briefing from "./pages/Briefing.jsx";
import DemoPick from "./pages/DemoPick.jsx";
import Explore from "./pages/Explore.jsx";
import Home from "./pages/Home.jsx";
import Runtime from "./pages/Runtime.jsx";

function parseHash() {
  const raw = (window.location.hash || "#/").replace(/^#/, "") || "/";
  const parts = raw.split("/").filter(Boolean);
  return { path: `/${parts.join("/")}`, parts };
}

export default function App() {
  const [route, setRoute] = useState(parseHash);

  useEffect(() => {
    const onHash = () => setRoute(parseHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const [section, ...rest] = route.parts;
  const page = !section ? (
    <Home />
  ) : section === "demo" && rest.length === 0 ? (
    <DemoPick />
  ) : section === "demo" && rest.length === 1 ? (
    <DemoPick enterpriseId={rest[0]} />
  ) : section === "demo" && rest.length >= 3 && rest[2] === "run" ? (
    <Runtime enterpriseId={rest[0]} useCaseId={rest[1]} />
  ) : section === "demo" && rest.length >= 2 ? (
    <Briefing enterpriseId={rest[0]} useCaseId={rest[1]} />
  ) : section === "explore" ? (
    <Explore parts={rest} />
  ) : section === "close" ? (
    <Close />
  ) : (
    <Home />
  );

  const exploreOn = section === "explore";
  const demoOn = section === "demo";

  return (
    <div className="shell">
      <header className="mast">
        <div>
          <p className="brand-mark">NetAware AX</p>
          <a href={href("/")} style={{ color: "inherit", textDecoration: "none" }}>
            Network Intent
          </a>
        </div>
        <nav className="nav">
          <a className={`nav-link${demoOn ? " on" : ""}`} href={href("/demo")}>
            Start Demo
          </a>
          <a className={`nav-link${exploreOn ? " on" : ""}`} href={href("/explore")}>
            Explore
          </a>
        </nav>
      </header>
      {page}
      <footer className="footer-bar">
        <p className="footer-note">Cadence 6 · presentation freeze · product behavior frozen · fictional enterprises</p>
        <a className="tiny" href={href("/close")}>
          Product close
        </a>
      </footer>
    </div>
  );
}
