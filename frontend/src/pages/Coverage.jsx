import { useEffect, useMemo, useState } from "react";
import { api, href } from "../api.js";
import { OperatorLadder } from "../visuals/VisualKit.jsx";

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function statusTone(status) {
  const v = String(status || "");
  if (v === "FULFILLABLE" || v === "FULFILLABLE_WITH_REDUCED_EVIDENCE") return "ok";
  if (v === "PARTIALLY_FULFILLABLE") return "warn";
  if (v === "BLOCKED" || v === "NOT_AVAILABLE") return "bad";
  return "muted";
}

function statusLabel(status) {
  if (status === "NOT_CONFIGURED") return "NOT CONFIGURED";
  if (status === "FULFILLABLE_WITH_REDUCED_EVIDENCE") return "FULFILLABLE · REDUCED EVIDENCE";
  return String(status || "").replaceAll("_", " ");
}

function parseCoverage(parts) {
  const [a, b, c, d] = parts || [];
  if ((a === "enterprise" || a === "enterprises") && c === "use-case") return { kind: "demand", enterpriseId: b, useCaseId: d };
  if (a === "enterprise" || a === "enterprises") return { kind: "demand", enterpriseId: b };
  if (a === "provider" || a === "providers") return { kind: "supply", providerId: b };
  if (a === "capability" || a === "capabilities") return { kind: "capability", capabilityId: b };
  if (a === "family") return { kind: "family", familyId: b };
  if (a === "record") return { kind: "record", recordId: b };
  return { kind: "home" };
}

function FinderStrip() {
  return (
    <section className="grid-3 vis-finders section">
      <article className="inset">
        <p className="kicker">Telco Finder</p>
        <p>Which network/operator applies?</p>
      </article>
      <article className="inset">
        <p className="kicker">API Finder</p>
        <p>Which relevant Network APIs are available through which providers?</p>
      </article>
      <article className="inset ax-lane">
        <p className="kicker">Fulfillment</p>
        <p>Can the Intent actually be satisfied given governance, readiness, required capabilities and route?</p>
      </article>
    </section>
  );
}

function Heatmap({ records, onPick }) {
  const intents = [];
  const providers = [];
  const seenI = new Set();
  const seenP = new Set();
  for (const rec of records || []) {
    if (rec.intentId && !seenI.has(rec.intentId)) {
      seenI.add(rec.intentId);
      intents.push({ id: rec.intentId, label: rec.intentLabel || rec.intentId });
    }
    if (rec.provider && !seenP.has(rec.provider)) {
      seenP.add(rec.provider);
      providers.push({ id: rec.provider, label: rec.providerLabel || rec.provider });
    }
  }
  const cell = (intentId, providerId) =>
    (records || []).find((r) => r.intentId === intentId && r.provider === providerId);
  return (
    <section className="section">
      <p className="kicker">Fulfillment heatmap</p>
      <p className="tiny">Intent × provider. Click a cell for why. Same C13 records.</p>
      <div className="matrix-wrap vis-matrix">
        <table className="discovery-matrix">
          <thead>
            <tr>
              <th>Intent</th>
              {providers.map((p) => (
                <th key={p.id}>{p.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {intents.map((intent) => (
              <tr key={intent.id}>
                <td>{intent.label}</td>
                {providers.map((p) => {
                  const rec = cell(intent.id, p.id);
                  return (
                    <td key={p.id}>
                      {rec ? (
                        <button type="button" className={`cov-cell ${statusTone(rec.fulfillmentStatus)}`} onClick={() => onPick(rec.id)}>
                          {String(rec.fulfillmentStatus || "").replaceAll("_", " ").slice(0, 12)}
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
    </section>
  );
}

function Funnel({ funnel }) {
  if (!funnel) return null;
  const steps = [
    ["candidate", "Candidate capabilities"],
    ["relevant", "Relevant"],
    ["permitted", "Permitted"],
    ["available", "Available"],
    ["operatorReady", "Operator-ready"],
    ["routable", "Routable"],
  ];
  return (
    <ol className="cov-funnel">
      {steps.map(([key, label]) => (
        <li key={key}>
          <strong>{funnel[key] ?? "—"}</strong>
          <span>{label}</span>
        </li>
      ))}
      <li className="result">
        <strong>{statusLabel(funnel.intentStatus)}</strong>
        <span>Intent</span>
      </li>
    </ol>
  );
}

function WhyPanel({ record, technical }) {
  if (!record) {
    return <p className="tiny">Select a region, provider, or cell to see why.</p>;
  }
  const why = record.why || {};
  const caps = why.capabilities || record.capabilities || [];
  return (
    <article className="panel cov-why">
      <div className="chips">
        <Pill tone={statusTone(record.fulfillmentStatus)}>{statusLabel(record.fulfillmentStatus)}</Pill>
        {record.accessType ? <Pill>{record.accessType}</Pill> : null}
        {record.route ? <Pill>{record.route}</Pill> : null}
        {record.selectedPath ? <Pill>{record.selectedPath}</Pill> : null}
      </div>
      <p className="kicker">
        {record.enterpriseLabel} · {record.applicationLabel} · {record.intentLabel}
      </p>
      <h3>
        {record.regionLabel} · {record.providerLabel}
      </h3>
      <p className="tiny">
        Relevant ≠ permitted ≠ available ≠ ready ≠ routable ≠ fulfillable.
      </p>
      <div className="cov-lanes">
        {(record.capabilities || []).map((cap) => (
          <div key={cap.id} className="cov-node">
            <p className="kicker">{cap.role}</p>
            <strong>{cap.label}</strong>
            <ul>
              <li>Relevant {cap.relevant}</li>
              <li>Permitted {cap.permitted}</li>
              <li>API {cap.apiAvailability}</li>
              <li>Ready {cap.ready}</li>
              <li>Route {cap.route || "—"}</li>
              <li>Fulfillable {cap.fulfillable}</li>
            </ul>
            {(cap.operatorReadiness?.applicable) ? (
              <p className="tiny">
                OPERATOR PREREQUISITE · Entitlement Server {cap.operatorReadiness.ecs}. Not a CAMARA API.
                NetAware does not control the operator ECS.
              </p>
            ) : null}
            {(cap.gaps || []).map((g) => (
              <p key={`${cap.id}-${g.code}`} className="cov-gap">
                Blocking gap · {g.code}
              </p>
            ))}
          </div>
        ))}
      </div>
      <Funnel funnel={record.funnel} />
      {record.fulfillmentVsOutcome ? (
        <div className="banner">
          <p>
            <strong>Fulfillment</strong> asks: {record.fulfillmentVsOutcome.fulfillmentAsks}
          </p>
          <p>
            <strong>Business outcome</strong> asks: {record.fulfillmentVsOutcome.businessOutcomeAsks}
          </p>
          <p className="tiny">
            API may return {record.fulfillmentVsOutcome.apiMayReturn}. That is still fulfillment success — not a
            supply failure.
          </p>
        </div>
      ) : null}
      {record.qualifiedDemand?.unfulfilledCount ? (
        <div className="banner">
          <p className="kicker">Capability gap → affected cohort → fulfillment impact</p>
          <p>
            {record.qualifiedDemand.unfulfilledCount} {record.qualifiedDemand.unit} cannot obtain{" "}
            {record.qualifiedDemand.capabilityId}. Qualified demand exists. Not revenue.
          </p>
        </div>
      ) : null}
      {record.portfolioHref ? (
        <p>
          <a href={href(record.portfolioHref)}>Back to business story</a>
          {" · "}
          <a href={href(`/demand/enterprise/${record.enterpriseId}`)}>See Demand</a>
        </p>
      ) : null}
      {technical ? (
        <dl className="dl">
          <dt>Telco Finder</dt>
          <dd>Which network/operator applies to this subject?</dd>
          <dt>API Finder</dt>
          <dd>
            {caps[0]?.operationId ? <code>{caps[0].operationId}</code> : "Candidate operations"} through{" "}
            {record.routeProviderLabel}
          </dd>
          <dt>Fulfillment Coverage</dt>
          <dd>Can the configured minimum sufficient set actually be satisfied here?</dd>
          <dt>Minimum sufficient set</dt>
          <dd>{(record.minimumSufficientSet || []).join(" · ") || "—"}</dd>
          <dt>Purpose / DPV</dt>
          <dd>{record.purposeLabel || record.purpose}</dd>
          <dt>Subscription / entitlement</dt>
          <dd>
            {record.subscription} / {record.entitlement}
          </dd>
          <dt>Consent</dt>
          <dd>{record.consent}</dd>
          <dt>Provenance</dt>
          <dd>
            {(record.provenance || []).map((row) => (
              <div key={row.fact} className="tiny">
                {row.source} · {row.fact}
              </div>
            ))}
          </dd>
        </dl>
      ) : (
        <p className="tiny">Open Technical View for Intent Profile, DPV, Telco Finder, API Finder, and provenance.</p>
      )}
    </article>
  );
}

export default function Coverage({ parts }) {
  const sel = parseCoverage(parts);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [view, setView] = useState(sel.kind === "supply" ? "supply" : sel.kind === "capability" || sel.kind === "family" ? "catalog" : "demand");
  const [technical, setTechnical] = useState(false);
  const [picked, setPicked] = useState(sel.recordId || "");
  const [enterpriseId, setEnterpriseId] = useState(sel.enterpriseId || "");
  const [providerId, setProviderId] = useState(sel.providerId || "");

  useEffect(() => {
    api("/coverage")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  const records = data?.records || [];
  const filtered = useMemo(() => {
    return records.filter((row) => {
      if (sel.recordId) return row.id === sel.recordId;
      if (sel.useCaseId) return row.useCaseId === sel.useCaseId && row.enterpriseId === sel.enterpriseId;
      if (sel.enterpriseId) return row.enterpriseId === sel.enterpriseId;
      if (sel.providerId) return row.provider === sel.providerId || row.routeProvider === sel.providerId;
      if (sel.capabilityId) {
        const ids = [...(row.requiredCapabilities || []), ...(row.optionalCapabilities || []), ...(row.conditionalCapabilities || [])];
        return ids.includes(sel.capabilityId);
      }
      if (sel.familyId) return (row.capabilities || []).some((c) => c.familyId === sel.familyId);
      if (view === "demand" && enterpriseId) return row.enterpriseId === enterpriseId;
      if (view === "supply" && providerId) return row.provider === providerId || row.routeProvider === providerId;
      return true;
    });
  }, [records, sel, view, enterpriseId, providerId]);

  const selected = records.find((r) => r.id === picked) || filtered[0] || null;
  const summary = data?.summary || {};
  const enterprises = [...new Map(records.map((r) => [r.enterpriseId, r])).values()];

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  return (
    <div className="coverage-page">
      <p className="kicker">Fulfillment Coverage</p>
      <h1>
        <span>Can we actually fulfill this?</span>
      </h1>
      <p className="lede">{data.question}</p>
      <p className="tiny honesty">{data.honesty}</p>

      <section className="leverage-strip section">
        <article>
          <span>{summary.salesVisibleUseCases}</span>
          <strong>sales-visible use cases</strong>
        </article>
        <article>
          <span>{summary.configuredFulfillmentCoverage}</span>
          <strong>with configured coverage</strong>
        </article>
        <article>
          <span>{summary.fullyFulfillable}</span>
          <strong>fully fulfillable</strong>
        </article>
        <article>
          <span>{summary.partial}</span>
          <strong>partial</strong>
        </article>
        <article>
          <span>{summary.blocked}</span>
          <strong>blocked</strong>
        </article>
        <article>
          <span>{summary.unknown}</span>
          <strong>unknown</strong>
        </article>
      </section>

      <ol className="cov-chain">
        {(data.chain || []).map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
      <FinderStrip />
      <OperatorLadder records={records} />

      <div className="tabs">
        {[
          ["demand", "Enterprise / demand"],
          ["supply", "Network / supply"],
          ["catalog", "Capability / catalog"],
        ].map(([id, label]) => (
          <button key={id} className={view === id ? "on" : ""} type="button" onClick={() => setView(id)}>
            {label}
          </button>
        ))}
        <button className={technical ? "on" : ""} type="button" onClick={() => setTechnical((v) => !v)}>
          {technical ? "Business View" : "Technical View"}
        </button>
      </div>

      {view === "demand" ? (
        <>
          <label className="cov-select">
            Enterprise
            <select
              value={enterpriseId}
              onChange={(e) => {
                setEnterpriseId(e.target.value);
                setPicked("");
              }}
            >
              <option value="">All</option>
              {enterprises.map((row) => (
                <option key={row.enterpriseId} value={row.enterpriseId}>
                  {row.enterpriseLabel}
                </option>
              ))}
            </select>
          </label>
          <div className="cov-visual">
            {filtered.map((row) => (
              <button
                key={row.id}
                type="button"
                className={`cov-lane ${picked === row.id ? "on" : ""}`}
                onClick={() => setPicked(row.id)}
              >
                <p className="kicker">
                  {row.applicationLabel} / {row.intentLabel}
                </p>
                <div className="cov-flow">
                  <span>{row.regionLabel}</span>
                  <span>{row.providerLabel}</span>
                  <span>{row.route || "—"}</span>
                  <Pill tone={statusTone(row.fulfillmentStatus)}>{statusLabel(row.fulfillmentStatus)}</Pill>
                </div>
                {row.accessType ? <p className="tiny">{row.accessType} · path {row.selectedPath || "none"}</p> : null}
              </button>
            ))}
          </div>
          <section className="section">
            <h3>Application / region</h3>
            {(data.matrix || [])
              .filter((app) => !enterpriseId || app.enterpriseId === enterpriseId)
              .map((app) => (
                <article key={`${app.enterpriseId}-${app.applicationId}`} className="panel cov-matrix">
                  <h3>
                    {app.enterpriseLabel} — {app.applicationLabel}
                  </h3>
                  {(app.intents || []).map((intent) => (
                    <div key={intent.intentId} className="cov-matrix-row">
                      <span>{intent.intentLabel}</span>
                      {(intent.cells || []).map((cell) => (
                        <button
                          key={`${intent.intentId}-${cell.region}`}
                          type="button"
                          className={`cov-cell ${statusTone(cell.fulfillmentStatus)}`}
                          onClick={() => cell.recordId && setPicked(cell.recordId)}
                        >
                          <em>{cell.region}</em>
                          {statusLabel(cell.fulfillmentStatus)}
                        </button>
                      ))}
                    </div>
                  ))}
                </article>
              ))}
          </section>
          <Heatmap records={filtered} onPick={setPicked} />
        </>
      ) : null}

      {view === "supply" ? (
        <section className="grid-2 section">
          <article className="panel">
            <h3>What can this network enable?</h3>
            {(data.providers || []).map((p) => (
              <button
                key={p.id}
                type="button"
                className={`cov-provider ${providerId === p.id ? "on" : ""}`}
                onClick={() => {
                  setProviderId(p.id);
                  setPicked("");
                }}
              >
                <strong>{p.label}</strong>
                <span className="tiny">
                  {p.providerType}
                  {p.doesNotOwnApis ? " · routes; does not own APIs" : ""}
                </span>
              </button>
            ))}
          </article>
          <article className="panel">
            {(() => {
              const p = (data.providers || []).find((row) => row.id === providerId) || data.providers?.[0];
              if (!p) return null;
              return (
                <>
                  <p className="kicker">{p.providerType}</p>
                  <h3>{p.label}</h3>
                  {p.aggregatorNote ? <p className="tiny">{p.aggregatorNote}</p> : null}
                  <p className="tiny">Capabilities advertised: {(p.operations || []).join(" · ")}</p>
                  <h4>Intents enabled</h4>
                  <ul className="list">
                    {(p.intentsEnabled || []).map((row) => (
                      <li key={`${row.recordId}`}>
                        <button type="button" onClick={() => setPicked(row.recordId)}>
                          {row.enterpriseLabel} · {row.applicationLabel} · {row.intentLabel}
                        </button>
                        <Pill tone={statusTone(row.fulfillmentStatus)}>{statusLabel(row.fulfillmentStatus)}</Pill>
                      </li>
                    ))}
                  </ul>
                </>
              );
            })()}
          </article>
        </section>
      ) : null}

      {view === "catalog" ? (
        <section className="section">
          <p className="tiny">Where is this available? Which intents depend on it? Not a commercial ranking.</p>
          {(data.capabilities || [])
            .filter((cap) => !sel.capabilityId || cap.id === sel.capabilityId)
            .filter((cap) => !sel.familyId || cap.familyId === sel.familyId)
            .map((cap) => (
              <article key={cap.id} className="panel" style={{ marginBottom: 12 }}>
                <h3>{cap.label}</h3>
                <p className="tiny">
                  <code>{cap.operationId}</code> · API Finder surface. Telco Finder is a different question.
                </p>
                <div className="cov-flow wrap">
                  {(cap.providers || []).slice(0, 8).map((row, idx) => (
                    <button key={`${cap.id}-${idx}`} type="button" onClick={() => row.recordId && setPicked(row.recordId)}>
                      {row.regionLabel} · {row.providerLabel} · {row.route || "—"}
                    </button>
                  ))}
                </div>
                <ul className="list compact">
                  {(cap.intents || []).map((hit) => (
                    <li key={`${cap.id}-${hit.intentId}-${hit.applicationLabel}`}>
                      {hit.enterpriseLabel} · {hit.applicationLabel} · {hit.intentLabel}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
        </section>
      ) : null}

      <section className="section grid-2">
        <WhyPanel record={selected} technical={technical} />
        <article className="panel">
          <h3>Three distinct questions</h3>
          <dl className="dl">
            <dt>Telco Finder</dt>
            <dd>{data.distinctions?.telcoFinder}</dd>
            <dt>API Finder</dt>
            <dd>{data.distinctions?.apiFinder}</dd>
            <dt>Fulfillment Coverage</dt>
            <dd>{data.distinctions?.fulfillmentCoverage}</dd>
          </dl>
          <p>
            <a href={href("/demo")}>Back to sales portfolio</a>
          </p>
        </article>
      </section>
    </div>
  );
}
