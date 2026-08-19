import { useEffect, useState } from "react";
import { MEET_EVENT, readCuesHidden } from "../meeting.js";

export function Cue({ text }) {
  const [hidden, setHidden] = useState(readCuesHidden);
  useEffect(() => {
    const onChange = () => setHidden(readCuesHidden());
    window.addEventListener(MEET_EVENT, onChange);
    return () => window.removeEventListener(MEET_EVENT, onChange);
  }, []);
  if (!text || hidden) return null;
  return <p className="vis-cue">{text}</p>;
}

export function StateBadge({ state }) {
  const v = String(state || "").toUpperCase();
  const tone =
    ["REQUIRED", "SELECTED", "INVOKED", "VERIFIED", "OUTCOME", "FULFILLABLE", "FULFILLED", "SERVED", "READY", "EXPOSED", "CALL"].includes(v)
      ? "ok"
      : ["CONDITIONAL", "FILTERED", "SKIPPED", "REUSED", "PARTIALLY_FULFILLABLE", "REUSE"].includes(v)
        ? "warn"
        : ["UNAVAILABLE", "BLOCKED", "NOT_AVAILABLE", "SKIP", "FILTER"].includes(v)
          ? "bad"
          : "muted";
  return <span className={`pill vis-state ${tone}`.trim()}>{v.replaceAll("_", " ")}</span>;
}

export function FlowChain({ items, className }) {
  return (
    <ol className={className || "vis-flow vis-reveal"}>
      {(items || []).map((row, idx) => {
        const label = typeof row === "string" ? row : row.label;
        const state = typeof row === "string" ? "" : row.state;
        const note = typeof row === "string" ? "" : row.note;
        return (
          <li key={`${label}-${idx}`} className={state || ""} style={{ "--i": idx }}>
            {idx ? <span className="vis-arrow">↓</span> : null}
            <strong>{label}</strong>
            {state ? <StateBadge state={state} /> : null}
            {note ? <span className="tiny">{note}</span> : null}
          </li>
        );
      })}
    </ol>
  );
}

export function AxBrain({ outcome, technical, highlight, compact }) {
  const steps = ["Understand", "Discover", "Govern", "Fulfill", "Act / Observe", "Verify"];
  const hi = String(highlight || "").toLowerCase();
  return (
    <section className={`ax-brain section${compact ? " compact" : ""}`} aria-label="What NetAware AX does">
      <p className="kicker">SIGNATURE · INTENT → AX → OUTCOME</p>
      <Cue text="Applications ask for outcomes, not network implementation." />
      <p className="lede">Your application tells NetAware what it needs to achieve. NetAware determines how the network can help.</p>
      <div className="ax-brain-stack vis-reveal">
        <article className="lane-ent">
          <span className="kicker">APPLICATION / AUTHORIZED AGENT</span>
        </article>
        <span className="vis-arrow">↓</span>
        <article className="lane-ent">
          <strong>INTENT</strong>
        </article>
        <span className="vis-arrow">↓</span>
        <article className="ax-brain-box lane-ax">
          <p className="kicker">NETAWARE AX</p>
          <ol>
            {steps.map((label) => (
              <li key={label} className={hi && label.toLowerCase().includes(hi.split("/")[0].trim()) ? "on" : ""}>
                {label}
              </li>
            ))}
          </ol>
        </article>
        <span className="vis-arrow">↓</span>
        <article className="lane-out">
          <span className="kicker">OUTCOME</span>
          <strong>{outcome || "BUSINESS OUTCOME"}</strong>
        </article>
      </div>
      {technical ? (
        <div className="grid-3 vis-finders section">
          <article className="inset">
            <p className="kicker">Telco Finder</p>
            <p>Which network/operator applies?</p>
          </article>
          <article className="inset">
            <p className="kicker">API Finder</p>
            <p>Which relevant Network APIs are available?</p>
          </article>
          <article className="inset">
            <p className="kicker">Provider / route · Policy · Evidence · Autonomy</p>
            <p>Fulfillment uses these together. They are not a fake execution order.</p>
          </article>
        </div>
      ) : null}
    </section>
  );
}

export function DxAxSplit({ dxAx }) {
  const data = dxAx || {};
  return (
    <section className="vis-split section" aria-label="Without AX and with AX">
      <Cue text="DX remains the foundation. AX adds an intent-driven decision layer above it." />
      <article className="panel lane-dx">
        <p className="kicker">WITHOUT AX / DX-ONLY</p>
        <p className="tiny">Application logic must understand operator, API availability, capability differences, routes, policy, readiness, and responses.</p>
        <FlowChain items={data.dx} />
      </article>
      <article className="panel ax-lane lane-ax">
        <p className="kicker">WITH NETAWARE AX</p>
        <p className="tiny">Application / Agent → INTENT → NetAware AX → OUTCOME</p>
        <FlowChain items={data.ax} />
      </article>
      <p className="plus-line">{data.footer || "DX REMAINS THE FOUNDATION. AX BUILDS ON NETWORK API DX. IT DOES NOT REPLACE IT."}</p>
    </section>
  );
}

export function AgenticLoopVisual({ agentic, highlight }) {
  const data = agentic || {};
  const chain = data.chain || [
    "INTENT",
    "UNDERSTAND",
    "DISCOVER",
    "GOVERN",
    "SELECT",
    "ACT / REUSE / SKIP",
    "OBSERVE",
    "REPLAN IF NECESSARY",
    "VERIFY",
    "OUTCOME",
  ];
  const hi = String(highlight || "").toUpperCase();
  return (
    <section className="section">
      <p className="kicker">Why is this AX?</p>
      <Cue text="AX is governed Intent execution — not an API router and not LLM theater." />
      <ol className="vis-flow vis-loop vis-reveal">
        {chain.map((label, idx) => (
          <li key={label} className={hi && label.toUpperCase().includes(hi) ? "on" : ""} style={{ "--i": idx }}>
            {idx ? <span className="vis-arrow">↓</span> : null}
            <strong>{label}</strong>
          </li>
        ))}
      </ol>
      <p className="tiny">{(data.proofs || []).join(" · ")}</p>
      <p className="tiny">{data.note || "Deterministic configured behavior. No LLM theater."}</p>
    </section>
  );
}

export function CloseBridge({ close }) {
  const data = close || {};
  return (
    <section className="eq section close-market vis-bridge" aria-label="Demand and supply">
      <article className="domain-lane">
        <span>{data.left?.title || "ENTERPRISE DEMAND"}</span>
        <strong>{(data.left?.items || []).join(" · ")}</strong>
      </article>
      <i>→</i>
      <article className="ax-lane">
        <span>{data.center?.title || "NETAWARE AX"}</span>
        <strong>{(data.center?.items || []).join(" · ")}</strong>
      </article>
      <i>→</i>
      <article className="network-lane">
        <span>{data.right?.title || "NETWORK SUPPLY"}</span>
        <strong>{(data.right?.items || []).join(" · ")}</strong>
      </article>
      <i>=</i>
      <article className="result">
        <span>{data.outcome || "BUSINESS OUTCOMES"}</span>
        <strong>{data.line || "NETAWARE CONNECTS ENTERPRISE DEMAND TO NETWORK SUPPLY."}</strong>
      </article>
    </section>
  );
}

export function FlywheelClose({ close }) {
  const data = close || {};
  return (
    <section className="flywheel section" aria-label="Demand and supply flywheel">
      <p className="kicker">SIGNATURE · DEMAND ↔ SUPPLY</p>
      <Cue text="More qualified demand and more ready supply meet in NetAware. Not an automatic network-effect claim." />
      <div className="flywheel-grid">
        <article className="lane-ent">
          <p className="kicker">{data.left?.title || "ENTERPRISE DEMAND"}</p>
          <FlowChain items={["APPLICATIONS / AGENTS", "INTENTS", "QUALIFIED CAPABILITY DEMAND"]} />
        </article>
        <article className="ax-brain-box lane-ax">
          <p className="kicker">{data.center?.title || "NETAWARE AX"}</p>
          <ol>
            {(data.center?.items || ["Discover", "Govern", "Match", "Fulfill", "Verify"]).map((row) => (
              <li key={row}>{row}</li>
            ))}
          </ol>
        </article>
        <article className="lane-net">
          <p className="kicker">OPERATORS / AGGREGATORS</p>
          <FlowChain items={["CAPABILITIES", "REGIONS", "ROUTES"]} />
        </article>
      </div>
      <p className="tiny">More enterprise applications → more visible qualified demand. More operator capability/readiness → more fulfillment coverage. More coverage → more Intents can be fulfilled. Conceptual commercial flywheel. Not revenue.</p>
      <p className="lede statement">{data.line || "NETAWARE CONNECTS ENTERPRISE DEMAND TO NETWORK SUPPLY."}</p>
    </section>
  );
}

export function DiscoveryFunnel({ summary, catalogFamilies }) {
  const layers = summary?.layers || [];
  const relevant = layers.find((l) => l.id === "couldAdd") || {};
  const permitted = layers.find((l) => l.id === "configuration") || {};
  const deliverable = layers.find((l) => l.id === "possibleNow") || {};
  const selected = summary?.selected || [];
  const filtered = summary?.filtered || [];
  const catalog = catalogFamilies || summary?.catalogFamilies || summary?.catalogUniverse || "13";
  const candidates = summary?.candidateCount ?? relevant.count ?? "—";
  const stages = [
    { label: "CATALOG UNIVERSE", count: catalog, note: "13 API families. Not runtime candidates." },
    { label: "RELEVANT TO THIS INTENT", count: relevant.count ?? candidates, note: "Generated candidates from this Intent." },
    { label: "CONFIGURED / PERMITTED", count: permitted.count ?? "—", note: "Purpose, policy, subscription, entitlement, consent." },
    { label: "DELIVERABLE NOW", count: deliverable.count ?? "—", note: "Operator, API availability, route, readiness." },
    { label: "SELECTED", count: selected.length, note: "Minimum sufficient network action." },
  ];
  return (
    <section className="vis-funnel vis-narrow" aria-label="Capability discovery funnel">
      <p className="kicker">SIGNATURE · HOW DID NETAWARE GET FROM INTENT TO THIS API?</p>
      <Cue text="NetAware selects the minimum useful network capability." />
      <p className="plus-line">
        {catalog} API families in the catalog → relevant capabilities discovered → feasible candidates evaluated →
        minimum sufficient network action selected
      </p>
      <ol className="vis-reveal vis-narrow-ol">
        {stages.map((step) => (
          <li key={step.label}>
            <strong>{step.count}</strong>
            <span>{step.label}</span>
            <em className="tiny">{step.note}</em>
          </li>
        ))}
      </ol>
      <p className="tiny">CALL · REUSE · SKIP · FILTER · UNAVAILABLE</p>
      {filtered.length ? (
        <ul className="list compact">
          {filtered.map((row) => (
            <li key={`${row.label}-${row.reasonCode}`}>
              <StateBadge state={row.reasonCode} /> {row.label}
              <span className="tiny"> — {row.humanReason}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

const GOVERNANCE_LAYERS = [
  ["purpose", "PURPOSE", ["PURPOSE_NOT_PERMITTED"]],
  ["agreement", "AGREEMENT / DPA", ["AGREEMENT_GAP"]],
  ["consent", "CONSENT", ["CONSENT_MISSING"]],
  ["subscription", "SUBSCRIPTION", ["NOT_SUBSCRIBED"]],
  ["entitlement", "ENTITLEMENT", ["NOT_ENTITLED"]],
  ["autonomy", "AUTONOMY", ["AUTONOMY_FORBIDS"]],
];

export function GovernanceWaterfall({ row }) {
  if (!row) return <p className="tiny">Select a candidate to see the governance path.</p>;
  const checks = row.checks || {};
  const applicable = GOVERNANCE_LAYERS.filter(([id]) => {
    const v = checks[id];
    return v && v !== "—" && v !== "NOT_EVALUATED";
  });
  const gates = applicable.length ? applicable : GOVERNANCE_LAYERS;
  const fail = gates.find(([, , codes]) => codes.includes(row.reasonCode));
  return (
    <article className="panel vis-gates">
      <p className="kicker">Governance gates</p>
      <Cue text="An available API can still fail a governance gate." />
      <h3>{row.label}</h3>
      <ol className="vis-flow vis-reveal">
        <li>
          <strong>Candidate capability</strong>
        </li>
        {gates.map(([id, label, codes], idx) => {
          const blocked = codes.includes(row.reasonCode);
          return (
            <li key={id} className={blocked ? "break" : "ok"} style={{ "--i": idx }}>
              <span className="vis-arrow">↓</span>
              <strong>
                {label} {blocked ? "✕" : "✓"}
              </strong>
              <span className="tiny">{checks[id] || "applicable"}</span>
              {blocked ? <StateBadge state="FILTERED" /> : null}
            </li>
          );
        })}
        {fail ? null : (
          <li className="ok">
            <span className="vis-arrow">↓</span>
            <strong>CALL / REUSE</strong>
          </li>
        )}
      </ol>
      {fail ? (
        <p className="plus-line">
          {fail[1]} ✕ · FILTERED
          {row.humanReason ? ` · ${row.humanReason}` : ""}
        </p>
      ) : null}
      <p className="tiny">Only existing provenance. Not every layer is evaluated identically for every API.</p>
    </article>
  );
}

export function FinderStages({ distinction }) {
  const d = distinction || {};
  return (
    <section className="grid-3 vis-finders section">
      <article className="inset">
        <p className="kicker">Telco Finder</p>
        <p>{d.telcoFinder || "Which network/operator applies?"}</p>
      </article>
      <article className="inset">
        <p className="kicker">API Finder</p>
        <p>{d.apiFinder || "Which relevant Network APIs are available through which providers?"}</p>
      </article>
      <article className="inset ax-lane">
        <p className="kicker">Fulfillment</p>
        <p>{d.fulfillment || "Can the Intent actually be satisfied?"}</p>
      </article>
    </section>
  );
}

export function TopologyVisual({ topology }) {
  const data = topology || {};
  const byRegion = {};
  for (const row of data.examples || []) {
    const key = row.region || row.regionLabel;
    if (!byRegion[key]) byRegion[key] = row;
  }
  const lanes = Object.values(byRegion);
  return (
    <section className="section">
      <p className="kicker">ONE ENTERPRISE INTENT · DIFFERENT NETWORK SUPPLY · ONE NORMALIZED OUTCOME</p>
      <Cue text="Configured demo coverage only. Aggregators do not own operator APIs." />
      <p className="tiny">{data.question}</p>
      <div className="region-lanes">
        {lanes.length
          ? lanes.map((row) => (
              <article key={`${row.region}-${row.provider}`} className="panel">
                <p className="kicker">{row.regionLabel || row.region}</p>
                <p>
                  Enterprise → NetAware
                  {row.via ? ` → ${row.via}` : ""} → {row.provider}
                </p>
                <StateBadge state={row.route || row.language} />
                <p className="tiny">
                  {row.language}
                  {row.via ? ` ${row.via}` : ""} · {row.status}
                </p>
              </article>
            ))
          : (
            <div className="grid-2">
              <article className="panel">
                <p className="kicker">DIRECT</p>
                <p>{data.direct}</p>
              </article>
              <article className="panel">
                <p className="kicker">AGGREGATED</p>
                <p>{data.aggregated}</p>
                <p className="tiny">Aggregator A does not own operator APIs.</p>
              </article>
            </div>
          )}
      </div>
      <p className="tiny">Regions · {(data.regions || []).join(" · ")} · {data.hybrid}</p>
      <p className="tiny">{data.note}</p>
    </section>
  );
}

export function InspectionLoop({ trace }) {
  const slo = trace?.sloMs || 40;
  const outcome = trace?.outcome?.outcome || "ASSURED";
  return (
    <section className="vis-loop-box section" aria-label="Closed loop">
      <p className="kicker">Closed-loop AX</p>
      <Cue text="HTTP/API success is not the same as the business objective verified." />
      <FlowChain
        items={[
          { label: `OBJECTIVE · inspection experience ≤ ${slo} ms` },
          { label: "OBSERVE" },
          { label: "SLO OK? QoD NOT REQUIRED" },
          { label: "OBSERVE · simulated breach" },
          { label: "REPLAN", note: "QoD now useful" },
          { label: "CREATE SESSION" },
          { label: "OBSERVE AGAIN" },
          { label: "OBJECTIVE SATISFIED" },
          { label: outcome, state: "OUTCOME" },
        ]}
      />
      <div className="vis-split">
        <article className="panel">
          <p className="kicker">HTTP / API SUCCESS</p>
          <p>201 CREATED is not the success condition.</p>
        </article>
        <article className="panel outcome ready">
          <p className="kicker">BUSINESS OBJECTIVE VERIFIED</p>
          <p>{outcome}</p>
        </article>
      </div>
    </section>
  );
}

export function CityCareMin({ decisions }) {
  const age = (decisions || []).find((d) => d.capabilityId === "age_verification" || /age/i.test(d.label || ""));
  const kyc = (decisions || []).find((d) => d.capabilityId === "kyc_match" || /kyc/i.test(d.label || ""));
  return (
    <section className="vis-split section">
      <article className="panel outcome ready">
        <p className="kicker">AGE VERIFICATION</p>
        <p>Minimum sufficient · permitted · selected · CALL</p>
        <StateBadge state={age?.state || "SELECTED"} />
      </article>
      <article className="panel">
        <p className="kicker">KYC MATCH</p>
        <p>Broader than needed · not permitted for this purpose · FILTER</p>
        <StateBadge state={kyc?.state || "FILTERED"} />
      </article>
      <p className="plus-line">AVAILABLE DOES NOT MEAN APPROPRIATE. NetAware selects the minimum sufficient capability.</p>
    </section>
  );
}

export function ReuseGraph({ evidence, invocations }) {
  const reused = (evidence || []).filter((e) => e.reused);
  const called = (invocations || []).filter((i) => (i.apiKind || "NETWORK") === "NETWORK" && !i.reused);
  return (
    <section className="section">
      <p className="kicker">Evidence reuse</p>
      <FlowChain items={["assess_network_trust", "SIM / device / roaming evidence", "assess_recovery_continuity", "tenant · subject · purpose · TTL · policy", "REUSE"]} />
      <p className="lede">{reused.length || called.length === 0 ? "0 NEW NETWORK INVOCATIONS" : `${called.length} network invocation(s)`}</p>
      <p className="tiny">AX is not “call every API every time.” Fresh, purpose-compatible evidence can be reused.</p>
    </section>
  );
}

export function ConfigVsRuntime({ data, technical, known, runtimeRows }) {
  const cfg = data || {};
  const left = (known || cfg.configured || []).filter(Boolean);
  const right = (runtimeRows || cfg.runtime || []).filter(Boolean);
  return (
    <section className="vis-split section">
      <p className="kicker" style={{ gridColumn: "1 / -1" }}>
        SIGNATURE · WHAT NETAWARE KNOWS
      </p>
      <Cue text="The decision combines what was onboarded with what is true now." />
      <article className="panel">
        <p className="kicker">CONFIGURED / ONBOARDED</p>
        <p className="tiny">ONBOARDING · CONFIGURATION</p>
        <ul className="list compact">
          {left.map((row) => (
            <li key={typeof row === "string" ? row : row.label}>
              {technical ? <span className="source-badge">{(row.source || "CONFIGURATION").replaceAll("_", " ")}</span> : null}{" "}
              {typeof row === "string" ? row : `${row.label}${row.value ? `: ${row.value}` : ""}`}
            </li>
          ))}
        </ul>
      </article>
      <article className="panel">
        <p className="kicker">RUNTIME DISCOVERY / CONTEXT</p>
        <p className="tiny">RUNTIME · DERIVED</p>
        <ul className="list compact">
          {right.map((row) => (
            <li key={typeof row === "string" ? row : row.label}>
              {technical ? <span className="source-badge">{(row.source || "RUNTIME").replaceAll("_", " ")}</span> : null}{" "}
              {typeof row === "string" ? row : `${row.label}${row.value ? `: ${row.value}` : ""}`}
            </li>
          ))}
        </ul>
      </article>
      <p className="plus-line" style={{ gridColumn: "1 / -1" }}>
        Both converge in NetAware AX → CALL | REUSE | SKIP | FILTER | UNAVAILABLE
      </p>
    </section>
  );
}

export function StaticToAx({ data }) {
  const d = data || {};
  return (
    <section className="section">
      <p className="kicker">From static map to AX</p>
      <div className="vis-split">
        <article className="panel">
          <p className="kicker">A STATIC MAPPING TELLS YOU</p>
          <strong>WHAT COULD APPLY</strong>
          <FlowChain items={d.static} />
        </article>
        <article className="panel ax-lane">
          <p className="kicker">NETAWARE AX DETERMINES</p>
          <strong>WHAT SHOULD APPLY NOW</strong>
          <FlowChain items={d.ax} />
        </article>
      </div>
      <p className="plus-line">{d.line}</p>
    </section>
  );
}

export function SupplyGapGraph({ gaps }) {
  return (
    <section className="section">
      <p className="kicker">What would enabling this unlock?</p>
      {(gaps || []).map((g) => (
        <article key={g.id} className="panel" style={{ marginBottom: 10 }}>
          <FlowChain
            items={[
              g.label || g.gap,
              g.prevents,
              g.affectedIntent,
              g.affectedApplication,
              g.affectedUnitsLabel || "configured qualified demand unfulfilled",
            ].filter(Boolean)}
          />
          <p className="tiny">{g.ifEnabled?.note || "Fulfillment impact. Not revenue."}</p>
        </article>
      ))}
    </section>
  );
}

export function ReverseGraph({ target, hits, onPick }) {
  return (
    <section className="rev-graph">
      <p className="kicker">SIGNATURE · USE CASE ↔ CAPABILITY ↔ API</p>
      <Cue text="One network capability can serve many enterprise applications." />
      <article className="ax-brain-box lane-net">
        <strong>{target?.label || "CAPABILITY / API FAMILY"}</strong>
      </article>
      <span className="vis-arrow">↓</span>
      <ul className="rev-branches vis-reveal">
        {(hits || []).map((hit) => (
          <li key={`${hit.useCaseId}-${hit.intentId}`}>
            <button type="button" className="rev-node lane-ent" onClick={() => onPick?.(hit)}>
              <strong>{hit.enterpriseLabel || hit.enterprise}</strong>
              <span>{hit.useCaseLabel || hit.useCaseId}</span>
              <em className="tiny">
                {hit.intentLabel || hit.intentId}
                {hit.state ? ` · ${hit.state}` : ""}
              </em>
            </button>
          </li>
        ))}
      </ul>
      <p className="tiny">Configured demo use cases. Same mapping source as the 17×13 matrix. Not invented.</p>
    </section>
  );
}

export function OperatorLadder({ records }) {
  const rows = records || [];
  const served = rows.find((r) => r.intentId === "verify_mobile_number" && r.fulfillmentStatus === "FULFILLABLE");
  const blocked = rows.find(
    (r) => r.intentId === "verify_mobile_number" && (r.fulfillmentStatus === "BLOCKED" || r.showcase === "ECS_GAP" || (r.blockingGaps || []).some((g) => g.code === "ENTITLEMENT_SERVER_UNAVAILABLE"))
  );
  const cards = [
    ["EXPOSED", served, true],
    ["READY", served, Boolean(served)],
    ["FULFILLABLE", served, served?.fulfillmentStatus === "FULFILLABLE"],
    ["DEMAND SERVED", served, served?.fulfillmentStatus === "FULFILLABLE"],
  ];
  if (!served && !blocked) return null;
  return (
    <section className="section vis-ladder">
      <p className="kicker">SIGNATURE · API EXPOSED → READY → FULFILLABLE → DEMAND SERVED</p>
      <Cue text="Exposing an API is not enough — the enterprise Intent must be fulfillable." />
      <p className="plus-line">API AVAILABLE ≠ BUSINESS INTENT FULFILLABLE</p>
      {served ? (
        <article className="panel">
          <p className="kicker">{served.providerLabel} · {served.accessType || "configured slice"}</p>
          <ol className="vis-flow vis-reveal">
            {cards.map(([label, rec, ok]) => (
              <li key={label} className={ok ? "ok" : "break"}>
                <strong>
                  {ok ? "✓" : "✕"} {label}
                </strong>
                <span className="tiny">
                  {label === "EXPOSED"
                    ? "Number Verification API"
                    : label === "READY"
                      ? rec?.operatorReadiness || "prerequisites"
                      : label === "FULFILLABLE"
                        ? rec?.intentLabel || rec?.intentId
                        : "Configured mobile-sign-in demand"}
                </span>
              </li>
            ))}
          </ol>
        </article>
      ) : null}
      {blocked ? (
        <article className="panel outcome gap">
          <p className="kicker">{blocked.providerLabel} · {blocked.accessType || "Wi-Fi"}</p>
          <ol className="vis-flow">
            <li className="ok">
              <strong>✓ API EXPOSED</strong>
              <span className="tiny">Number Verification API</span>
            </li>
            <li className="ok">
              <strong>✓ NV2 supported</strong>
            </li>
            <li className="break">
              <strong>✕ Entitlement Server</strong>
              <span className="tiny">{(blocked.blockingGaps || [])[0]?.detail || blocked.operatorReadiness || "ECS unavailable"}</span>
            </li>
            <li className="break">
              <strong>INTENT BLOCKED</strong>
            </li>
          </ol>
        </article>
      ) : null}
    </section>
  );
}

export function IntentTrace({ trace, open }) {
  if (!trace) return null;
  const items = [
    ["Application", trace.application?.label || trace.discoverySummary?.application],
    ["Intent", trace.request?.intent || trace.intentId],
    ["Purpose", trace.purpose?.audienceLabel || trace.purpose?.label],
    ["Candidates", String(trace.discoverySummary?.candidateCount ?? (trace.discoverySummary?.layers || []).find((l) => l.id === "couldAdd")?.count ?? "")],
    ["Governance", (trace.discoverySummary?.filtered || []).length ? "FILTERED candidates present" : "permitted set evaluated"],
    ["Telco Finder", trace.pathSelection?.telcoFinder?.provider || trace.telcoFinder?.result?.network],
    ["API Finder", trace.pathSelection?.apiFinder?.numberVerificationAvailable != null ? (trace.pathSelection.apiFinder.numberVerificationAvailable ? "NV available" : "NV unavailable") : (trace.apiFinder?.results || []).length ? `${trace.apiFinder.results.length} operations` : ""],
    ["Provider / route", trace.route?.display || trace.route?.type],
    ["NV path", trace.pathSelection?.selectedPath],
    ["Invocation", (trace.invocations || []).filter((i) => (i.apiKind || "NETWORK") === "NETWORK").map((i) => i.operationId).filter(Boolean).join(" · ")],
    ["Evidence", (trace.evidence || []).length ? `${trace.evidence.length} evidence item(s)` : ""],
    ["Outcome", trace.outcome?.outcome],
  ].filter(([, v]) => v);
  return (
    <details className="intent-trace panel" open={open}>
      <summary>
        <span className="kicker">SMALL INTENT IN</span>
        <strong>{trace.request?.intent || trace.intentId}</strong>
        <span className="tiny"> → explainable governed execution out</span>
      </summary>
      <Cue text="Start with the Intent. Expand only if the room needs the machinery." />
      <ol className="vis-flow vis-reveal">
        {items.map(([label, value], idx) => (
          <li key={label} style={{ "--i": idx }}>
            {idx ? <span className="vis-arrow">↓</span> : null}
            <strong>{label}</strong>
            <span className="tiny">{value}</span>
          </li>
        ))}
      </ol>
    </details>
  );
}

export function CompactDemandSupply() {
  return (
    <section className="compact-ds" aria-label="Enterprise demand to network supply">
      <article className="lane-ent">
        <span>ENTERPRISE DEMAND</span>
      </article>
      <span>↓</span>
      <article className="lane-ax">
        <strong>NETAWARE AX</strong>
      </article>
      <span>↓</span>
      <article className="lane-net">
        <span>NETWORK SUPPLY</span>
      </article>
    </section>
  );
}
