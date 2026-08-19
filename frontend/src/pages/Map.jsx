import { useEffect, useMemo, useState } from "react";
import { api, href } from "../api.js";
import { readLens } from "../lens.jsx";
import {
  AgenticLoopVisual,
  CloseBridge,
  ConfigVsRuntime,
  DxAxSplit,
  FinderStages,
  FlowChain,
  StateBadge,
  StaticToAx,
  SupplyGapGraph,
  TopologyVisual,
} from "../visuals/VisualKit.jsx";

export default function Map({ parts }) {
  const kind = parts?.[0] || "forward";
  const selected = parts?.[1] || "";
  const view =
    kind === "family" || kind === "capability" ? "reverse" : kind === "use-case" ? "forward" : kind;
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [industry, setIndustry] = useState("");
  const [motion, setMotion] = useState("");
  const [maturity, setMaturity] = useState("");
  const [picked, setPicked] = useState(null);
  const technical = readLens() === "ADVANCED";

  useEffect(() => {
    api("/map")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  const useCases = useMemo(() => {
    return (data?.useCases || []).filter((row) => {
      if (industry && row.industry !== industry) return false;
      if (motion && !(row.motion || []).includes(motion)) return false;
      if (maturity && row.maturity !== maturity) return false;
      return true;
    });
  }, [data, industry, motion, maturity]);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  const matrix = data.matrix || {};
  const active =
    view === "use-case"
      ? useCases.find((u) => u.useCaseId === selected) || useCases[0]
      : useCases[0];

  return (
    <div className="map-page">
      <p className="kicker">Use Case ↔ API Map</p>
      <h1>
        <span>What could apply.</span>
        <span>Then what AX actually does.</span>
      </h1>
      <p className="lede">{data.question}</p>
      <p className="tiny honesty">{data.honesty}</p>
      <p className="plus-line">{data.productStatement}</p>

      <div className="tabs">
        {[
          ["forward", "Use case → API", "/map"],
          ["reverse", "API → use case", "/map/reverse"],
          ["matrix", "Matrix", "/map/matrix"],
          ["enterprise", "Application graph", "/map/enterprise"],
          ["ax", "Static → AX", "/map/ax"],
        ].map(([id, label, to]) => (
          <a key={id} href={href(to)}>
            <button className={view === id ? "on" : ""} type="button">
              {label}
            </button>
          </a>
        ))}
      </div>

      <div className="filter-row">
        <label>
          Industry
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            <option value="">All</option>
            {(data.filters?.industries || []).map((row) => (
              <option key={row.id} value={row.id}>
                {row.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Motion
          <select value={motion} onChange={(e) => setMotion(e.target.value)}>
            <option value="">All</option>
            {(data.filters?.motions || []).map((row) => (
              <option key={row.id} value={row.id}>
                {row.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Maturity
          <select value={maturity} onChange={(e) => setMaturity(e.target.value)}>
            <option value="">All</option>
            {(data.filters?.maturities || []).map((row) => (
              <option key={row} value={row}>
                {row}
              </option>
            ))}
          </select>
        </label>
      </div>

      {view === "reverse" ? (
        <ReverseView data={data} selected={kind === "reverse" ? "" : selected} />
      ) : view === "matrix" ? (
        <MatrixView matrix={matrix} useCases={useCases} picked={picked} setPicked={setPicked} />
      ) : view === "enterprise" ? (
        <EnterpriseView enterprises={data.enterprises} selected={selected} />
      ) : view === "ax" ? (
        <>
          <StaticToAx data={data.staticToAx} />
          <FinderStages distinction={data.finderDistinction} />
          <TopologyVisual topology={data.topology} />
          <SupplyGapGraph gaps={data.supplyGaps} />
          {technical ? <ConfigVsRuntime data={data.configuredVsRuntime} technical /> : null}
          <DxAxSplit dxAx={data.dxAx} />
          <AgenticLoopVisual agentic={data.agentic} />
          <CloseBridge close={data.closeVisual} />
        </>
      ) : (
        <ForwardView rows={useCases} active={active} />
      )}
    </div>
  );
}

function ForwardView({ rows, active }) {
  const row = active || rows[0];
  if (!row) return <p className="tiny">No configured demo use cases in this filter.</p>;
  return (
    <div className="grid-2 section">
      <div>
        {(rows || []).map((u) => (
          <a key={u.useCaseId} className="stake-card" href={href(`/map/use-case/${u.useCaseId}`)} style={{ display: "block", marginBottom: 8 }}>
            <strong>{u.useCaseLabel}</strong>
            <span>
              {u.enterpriseLabel} · {u.applicationLabel}
            </span>
            <em>{u.maturity}</em>
          </a>
        ))}
      </div>
      <article className="panel">
        <p className="kicker">{row.industryLabel}</p>
        <h3>{row.useCaseLabel}</h3>
        <p>{row.businessProblem}</p>
        <p className="tiny">Decision gap · {row.decisionGap}</p>
        <FlowChain
          items={[
            row.industryLabel,
            row.enterpriseLabel,
            row.applicationLabel,
            row.useCaseLabel,
            row.intentLabel || row.intentId,
            "NETWORK DECISION GAP",
            ...(row.capabilities || []).map((c) => c.label),
            ...(row.families || []).map((f) => f.label),
          ]}
        />
        <div className="chips" style={{ marginTop: 12 }}>
          {(row.families || []).map((f) => (
            <span key={f.id}>
              <StateBadge state={f.state} /> {f.label}
            </span>
          ))}
        </div>
        <p className="tiny">{(row.families || [])[0]?.why}</p>
        <p>
          <a href={href(row.demoHref)}>Open the business story</a>
          {" · "}
          <a href={href(`/coverage/enterprise/${row.enterpriseId}`)}>Fulfillment</a>
        </p>
      </article>
    </div>
  );
}

function ReverseView({ data, selected }) {
  const families = data.reverseFamilies || [];
  const caps = data.reverseCapabilities || [];
  const fam = families.find((f) => f.id === selected) || families.find((f) => (f.useCases || []).length) || families[0];
  const cap = caps.find((c) => c.id === selected);
  const target = cap || fam;
  const hits = target?.useCases || [];
  return (
    <div className="grid-2 section">
      <div>
        <p className="kicker">Network API family</p>
        {families.map((f) => (
          <a key={f.id} className="stake-card" href={href(`/map/family/${f.id}`)} style={{ display: "block", marginBottom: 8 }}>
            <strong>{f.label}</strong>
            <span>{(f.useCases || []).length} configured demo use cases</span>
          </a>
        ))}
        <p className="kicker" style={{ marginTop: 16 }}>
          Business capability
        </p>
        {caps
          .filter((c) => (c.useCases || []).length)
          .map((c) => (
            <a key={c.id} className="coverage-link" href={href(`/map/capability/${c.id}`)}>
              {c.label}
            </a>
          ))}
      </div>
      <article className="panel">
        <p className="kicker">WHERE CAN I ENABLE THIS CAPABILITY?</p>
        <h3>{target?.label}</h3>
        <p className="tiny">{target?.note || fam?.note}</p>
        <FlowChain items={["CAPABILITY / API FAMILY", "INTENTS", "APPLICATIONS", "USE CASES", "ENTERPRISES", "INDUSTRIES"]} />
        <ul className="list compact">
          {hits.map((hit) => (
            <li key={`${hit.useCaseId}-${hit.intentId}`}>
              <a href={href(`/map/use-case/${hit.useCaseId}`)}>{hit.useCaseLabel || hit.useCaseId}</a>
              <span className="tiny">
                {" "}
                · {hit.enterpriseLabel} · {hit.intentId} · {hit.maturity}
                {hit.state ? ` · ${hit.state}` : ""}
              </span>
              <div className="tiny">{hit.note}</div>
            </li>
          ))}
        </ul>
      </article>
    </div>
  );
}

function MatrixView({ matrix, useCases, picked, setPicked }) {
  const [focusUse, setFocusUse] = useState("");
  const [focusFam, setFocusFam] = useState("");
  const [hover, setHover] = useState({ row: "", col: "" });
  const [stage, setStage] = useState(false);
  const allowed = new Set((useCases || []).map((u) => u.useCaseId));
  const rows = (matrix.rows || []).filter((r) => allowed.has(r.useCaseId) && (!focusUse || r.useCaseId === focusUse));
  const cols = (matrix.columns || []).filter((c) => !focusFam || c.id === focusFam);
  const cellMap = {};
  for (const cell of matrix.cells || []) {
    cellMap[`${cell.useCaseId}::${cell.familyId}`] = cell;
  }
  return (
    <section className={`section vis-matrix-stage${stage ? " on" : ""}`}>
      <p className="tiny">{matrix.note}</p>
      <p className="tiny">{matrix.emptyMeans}</p>
      <div className="filter-row">
        <label>
          Selected use case
          <select value={focusUse} onChange={(e) => setFocusUse(e.target.value)}>
            <option value="">All 17</option>
            {(matrix.rows || [])
              .filter((r) => allowed.has(r.useCaseId))
              .map((row) => (
                <option key={row.useCaseId} value={row.useCaseId}>
                  {row.label}
                </option>
              ))}
          </select>
        </label>
        <label>
          Selected API family
          <select value={focusFam} onChange={(e) => setFocusFam(e.target.value)}>
            <option value="">All 13</option>
            {(matrix.columns || []).map((col) => (
              <option key={col.id} value={col.id}>
                {col.label}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className={stage ? "on" : ""} onClick={() => setStage((v) => !v)}>
          {stage ? "Exit projector focus" : "Projector focus"}
        </button>
      </div>
      <div className="matrix-wrap vis-matrix">
        <table className="discovery-matrix">
          <thead>
            <tr>
              <th>Use case</th>
              {cols.map((col) => (
                <th key={col.id} title={col.label} className={hover.col === col.id || picked?.familyId === col.id ? "hl" : ""}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.useCaseId} className={hover.row === row.useCaseId || picked?.useCaseId === row.useCaseId ? "hl" : ""}>
                <td>
                  <strong>{row.label}</strong>
                  <div className="tiny">
                    {row.enterprise} · {row.maturity}
                  </div>
                </td>
                {cols.map((col) => {
                  const cell = cellMap[`${row.useCaseId}::${col.id}`];
                  const on = picked && picked.useCaseId === row.useCaseId && picked.familyId === col.id;
                  const dim = picked && !on;
                  return (
                    <td
                      key={col.id}
                      className={`${hover.col === col.id ? "hl" : ""}${dim ? " dim" : ""}`}
                      onMouseEnter={() => setHover({ row: row.useCaseId, col: col.id })}
                      onMouseLeave={() => setHover({ row: "", col: "" })}
                    >
                      {cell ? (
                        <button
                          type="button"
                          className={`cov-cell ${cell.state === "REQUIRED" ? "ok" : cell.state === "FILTERED" ? "bad" : "warn"}${on ? " on" : ""}`}
                          onClick={() => setPicked(cell)}
                        >
                          {cell.state === "REQUIRED" ? "REQ" : cell.state === "CONDITIONAL" ? "COND" : "FILT"}
                        </button>
                      ) : (
                        <span className="tiny">·</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {picked ? (
        <article className="panel vis-why" style={{ marginTop: 16 }}>
          <p className="kicker">WHY THIS API IS RELEVANT</p>
          <h3>
            {picked.familyLabel} · <StateBadge state={picked.state} />
          </h3>
          <p>{picked.why}</p>
          <p className="tiny">{picked.source}</p>
        </article>
      ) : (
        <p className="tiny">Click a populated cell. Empty cells are not relevant — not invented.</p>
      )}
    </section>
  );
}

function EnterpriseView({ enterprises, selected }) {
  const rows = enterprises || [];
  const ent = rows.find((e) => e.id === selected) || rows[0];
  if (!ent) return null;
  return (
    <div className="grid-2 section">
      <div>
        {rows.map((e) => (
          <a key={e.id} className="stake-card" href={href(`/map/enterprise/${e.id}`)} style={{ display: "block", marginBottom: 8 }}>
            <strong>{e.label}</strong>
            <span>
              {(e.applications || []).length} applications · {(e.sharedCapabilities || []).length} reusable capabilities
            </span>
          </a>
        ))}
      </div>
      <article className="panel">
        <p className="kicker">{ent.leverage}</p>
        <h3>{ent.label}</h3>
        {(ent.applications || []).map((app) => (
          <div key={app.id} style={{ marginBottom: 16 }}>
            <p className="kicker">APPLICATION</p>
            <strong>{app.label}</strong>
            {(app.useCases || []).map((uc) => (
              <div key={uc.useCaseId}>
                <FlowChain items={[uc.useCaseLabel, uc.intentLabel || uc.intentId, uc.decisionGap, ...(uc.capabilities || []).map((c) => c.label)]} />
              </div>
            ))}
          </div>
        ))}
      </article>
    </div>
  );
}
