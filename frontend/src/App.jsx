import { useEffect, useState } from "react";
import { api, href } from "./api.js";
import Close from "./pages/Close.jsx";
import Briefing from "./pages/Briefing.jsx";
import DemoPick from "./pages/DemoPick.jsx";
import Explore from "./pages/Explore.jsx";
import Home from "./pages/Home.jsx";
import Runtime from "./pages/Runtime.jsx";
import Coverage from "./pages/Coverage.jsx";
import Demand from "./pages/Demand.jsx";
import Start, { Welcome } from "./pages/Stakeholder.jsx";
import Meeting from "./pages/Meeting.jsx";
import Map from "./pages/Map.jsx";
import { readStakeholder, startHref, STAKEHOLDER_EVENT } from "./stakeholder.js";
import { resetDemo } from "./meeting.js";

function parseHash() {
  const raw = (window.location.hash || "#/").replace(/^#/, "") || "/";
  const parts = raw.split("/").filter(Boolean);
  return { path: `/${parts.join("/")}`, parts };
}

export default function App() {
  const [route, setRoute] = useState(parseHash);
  const [perspective, setPerspective] = useState(readStakeholder);
  const [preflight, setPreflight] = useState(null);

  useEffect(() => {
    const onHash = () => setRoute(parseHash());
    const onStake = () => setPerspective(readStakeholder());
    window.addEventListener("hashchange", onHash);
    window.addEventListener(STAKEHOLDER_EVENT, onStake);
    return () => {
      window.removeEventListener("hashchange", onHash);
      window.removeEventListener(STAKEHOLDER_EVENT, onStake);
    };
  }, []);

  useEffect(() => {
    api("/preflight")
      .then(setPreflight)
      .catch(() => setPreflight({ ready: false, label: "DEMO NOT READY" }));
  }, []);

  const [section, ...rest] = route.parts;
  const page = !section ? (
    <Welcome />
  ) : section === "home" ? (
    <Home />
  ) : section === "start" ? (
    <Start audience={rest[0] || "enterprise"} />
  ) : section === "meet" ? (
    <Meeting parts={rest} />
  ) : section === "map" ? (
    <Map parts={rest} />
  ) : section === "demo" && rest.length === 0 ? (
    <DemoPick />
  ) : section === "demo" && rest.length === 1 ? (
    <DemoPick enterpriseId={rest[0]} />
  ) : section === "demo" && rest.length >= 3 && rest[2] === "run" ? (
    <Runtime enterpriseId={rest[0]} useCaseId={rest[1]} />
  ) : section === "demo" && rest.length >= 2 ? (
    <Briefing enterpriseId={rest[0]} useCaseId={rest[1]} />
  ) : section === "coverage" ? (
    <Coverage parts={rest} />
  ) : section === "demand" ? (
    <Demand parts={rest} />
  ) : section === "explore" ? (
    <Explore parts={rest} />
  ) : section === "close" ? (
    <Close />
  ) : (
    <Welcome />
  );

  const exploreOn = section === "explore";
  const demoOn = section === "demo";
  const coverageOn = section === "coverage";
  const demandOn = section === "demand";
  const mapOn = section === "map";
  const homeOn = !section || section === "home" || section === "start" || section === "meet";
  const brandHref = startHref(perspective) || "/";

  return (
    <div className="shell">
      <header className="mast">
        <div>
          <p className="brand-mark">NetAware AX</p>
          <a href={href(brandHref)} style={{ color: "inherit", textDecoration: "none" }}>
            Network Intent
          </a>
        </div>
        <nav className="nav">
          <a className={`nav-link${homeOn ? " on" : ""}`} href={href("/")}>
            Home
          </a>
          <a className={`nav-link${demoOn ? " on" : ""}`} href={href("/demo")}>
            Portfolio
          </a>
          <a className={`nav-link${exploreOn ? " on" : ""}`} href={href("/explore")}>
            Explore
          </a>
          <a className={`nav-link${coverageOn ? " on" : ""}`} href={href("/coverage")}>
            Fulfillment
          </a>
          <a className={`nav-link${demandOn ? " on" : ""}`} href={href("/demand")}>
            Demand
          </a>
          <a className={`nav-link${mapOn ? " on" : ""}`} href={href("/map")}>
            Map
          </a>
        </nav>
      </header>
      {page}
      <footer className="footer-bar">
        <p className="footer-note">Cadence 17 · Visual intelligence · fictional enterprises</p>
        {preflight ? (
          <span className={`pill ${preflight.ready ? "ok" : "warn"}`}>{preflight.label}</span>
        ) : null}
        <button type="button" className="tiny" onClick={() => resetDemo()}>
          Reset Demo
        </button>
        <a className="tiny" href={href("/")}>
          Change perspective
        </a>
        <a className="tiny" href={href("/home")}>
          Product home
        </a>
        <a className="tiny" href={href("/close")}>
          Product close
        </a>
      </footer>
    </div>
  );
}
