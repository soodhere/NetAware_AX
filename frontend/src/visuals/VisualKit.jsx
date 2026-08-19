export function StateBadge({ state }) {
  const v = String(state || "").toUpperCase();
  const tone =
    ["REQUIRED", "SELECTED", "INVOKED", "VERIFIED", "OUTCOME", "FULFILLABLE", "FULFILLED"].includes(v)
      ? "ok"
      : ["CONDITIONAL", "FILTERED", "SKIPPED", "REUSED", "PARTIALLY_FULFILLABLE"].includes(v)
        ? "warn"
        : ["UNAVAILABLE", "BLOCKED", "NOT_AVAILABLE"].includes(v)
          ? "bad"
          : "muted";
  return <span className={`pill vis-state ${tone}`.trim()}>{v.replaceAll("_", " ")}</span>;
}

export function FlowChain({ items, className }) {
  return (
    <ol className={className || "vis-flow"}>
      {(items || []).map((row, idx) => {
        const label = typeof row === "string" ? row : row.label;
        const state = typeof row === "string" ? "" : row.state;
        return (
          <li key={`${label}-${idx}`} className={state || ""}>
            {idx ? <span className="vis-arrow">↓</span> : null}
            <strong>{label}</strong>
            {state ? <StateBadge state={state} /> : null}
          </li>
        );
      })}
    </ol>
  );
}

export function DxAxSplit({ dxAx }) {
  const data = dxAx || {};
  return (
    <section className="vis-split section" aria-label="DX to AX">
      <article className="panel">
        <p className="kicker">NETWORK API DX</p>
        <FlowChain items={data.dx} />
      </article>
      <article className="panel ax-lane">
        <p className="kicker">NETAWARE AX</p>
        <FlowChain items={data.ax} />
      </article>
      <p className="plus-line">{data.footer || "AX BUILDS ON NETWORK API DX. IT DOES NOT REPLACE IT."}</p>
    </section>
  );
}

export function AgenticLoopVisual({ agentic }) {
  const data = agentic || {};
  return (
    <section className="section">
      <p className="kicker">Why is this AX?</p>
      <FlowChain items={data.chain} className="vis-flow vis-loop" />
      <p className="tiny">{(data.proofs || []).join(" · ")}</p>
      <p className="tiny">{data.note}</p>
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

export function DiscoveryFunnel({ summary }) {
  const candidates = summary?.candidates || summary?.pipeline || [];
  const filtered = summary?.filtered || [];
  const selected = summary?.selected || [];
  const stages = [
    { label: "APPLICATION + INTENT", count: 1, tone: "" },
    { label: "CANDIDATES", count: (summary?.candidateCount || candidates.length || filtered.length + selected.length) || "—", tone: "" },
    { label: "GOVERNANCE", count: filtered.length, tone: "warn" },
    { label: "SELECTED", count: selected.length, tone: "ok" },
  ];
  return (
    <section className="vis-funnel" aria-label="Capability discovery funnel">
      <p className="kicker">How did NetAware choose this API?</p>
      <ol>
        {stages.map((step) => (
          <li key={step.label} className={step.tone}>
            <strong>{step.count}</strong>
            <span>{step.label}</span>
          </li>
        ))}
      </ol>
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
  ["agentIntent", "Application / Agent authorization"],
  ["purpose", "Purpose"],
  ["policy", "Policy"],
  ["agreement", "Agreement / DPA"],
  ["consent", "Consent"],
  ["subscription", "Subscription"],
  ["entitlement", "Entitlement"],
  ["autonomy", "Autonomy"],
];

export function GovernanceWaterfall({ row }) {
  if (!row) return <p className="tiny">Select a candidate to see the governance path.</p>;
  const checks = row.checks || {};
  const fail =
    row.reasonCode === "PURPOSE_NOT_PERMITTED"
      ? "purpose"
      : row.reasonCode === "CONSENT_MISSING"
        ? "consent"
        : row.reasonCode === "AGREEMENT_GAP"
          ? "agreement"
          : row.reasonCode === "NOT_SUBSCRIBED"
            ? "subscription"
            : row.reasonCode === "NOT_ENTITLED"
              ? "entitlement"
              : row.reasonCode === "AUTONOMY_FORBIDS"
                ? "autonomy"
                : "";
  return (
    <article className="panel">
      <p className="kicker">Governance waterfall</p>
      <h3>{row.label}</h3>
      <ol className="vis-flow">
        <li>
          <strong>Candidate capability</strong>
        </li>
        {GOVERNANCE_LAYERS.map(([id, label]) => (
          <li key={id} className={fail === id ? "break" : ""}>
            <span className="vis-arrow">↓</span>
            <strong>{label}</strong>
            <span className="tiny">{checks[id] || "—"}</span>
            {fail === id ? <StateBadge state="FILTERED" /> : null}
          </li>
        ))}
      </ol>
      <p className="tiny">Not every layer is evaluated identically for every API. Existing provenance only.</p>
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
  return (
    <section className="section">
      <p className="kicker">Provider / aggregator topology</p>
      <p className="tiny">{data.question}</p>
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
      <p className="tiny">Regions · {(data.regions || []).join(" · ")} · {data.hybrid}</p>
      <ul className="list compact">
        {(data.examples || []).slice(0, 8).map((row) => (
          <li key={`${row.intentId}-${row.region}-${row.provider}`}>
            <strong>{row.enterprise}</strong> · {row.intentLabel} · {row.regionLabel} · {row.language}
            {row.via ? ` ${row.via}` : ""} → {row.provider}
          </li>
        ))}
      </ul>
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
      <FlowChain
        items={[
          `OBJECTIVE ≤ ${slo} ms`,
          "OBSERVE",
          "78 ms",
          "BREACH",
          "REPLAN",
          "QoD NOT REQUIRED → SELECTED",
          "ACT",
          "OBSERVE AGAIN",
          "VERIFY",
          outcome,
        ]}
      />
      <p className="plus-line">201 CREATED IS NOT THE SUCCESS CONDITION. Success is OBJECTIVE VERIFIED.</p>
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

export function ConfigVsRuntime({ data, technical }) {
  const cfg = data || {};
  return (
    <section className="vis-split section">
      <article className="panel">
        <p className="kicker">WHAT NETAWARE ALREADY KNOWS</p>
        <p className="tiny">ONBOARDING · CONFIGURATION</p>
        <ul className="list compact">
          {(cfg.configured || []).map((row) => (
            <li key={row}>{row}</li>
          ))}
        </ul>
      </article>
      <article className="panel">
        <p className="kicker">WHAT NETAWARE DISCOVERS AT RUNTIME</p>
        <p className="tiny">RUNTIME · OPERATOR READINESS</p>
        <ul className="list compact">
          {(cfg.runtime || []).map((row) => (
            <li key={row}>{row}</li>
          ))}
        </ul>
      </article>
      {technical ? <p className="tiny">Same graph. Technical view adds provenance badges, not a second engine.</p> : null}
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
