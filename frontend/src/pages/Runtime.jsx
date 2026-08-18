import { useEffect, useMemo, useRef, useState } from "react";
import { api, apiPost, apiVersionMaturityTone, href } from "../api.js";
import { LENS_EVENT, LensToggle, readLens, writeLens } from "../lens.jsx";
import AxLoop from "../components/AxLoop.jsx";
import DiscoveryView, { OutcomeView } from "./Discovery.jsx";

const SCENARIOS = {
  "high-flight-airlines/baggage-connection": {
    kicker: "High Flight Airlines · Baggage Operations",
    title: "Ensure baggage connection",
    lede:
      "Airline systems stay in place. The agent sends an outcome. NetAware composes domain and Network APIs, replans when policy blocks location, and returns an airline-level result.",
    briefingHref: "/demo/high-flight-airlines/baggage-connection",
    closeHref: "/close",
    request: {
      intent: "ensure_baggage_connection",
      subject: { bagId: "HF123456", connectingFlight: "HF281" },
      context: { priority: "high" },
    },
    enterpriseLabel: "High Flight Airlines",
  },
  "rocket-bank/high-value-payment-protection": {
    kicker: "Rocket Bank · Payments Risk",
    title: "Assess network trust",
    lede:
      "Small outcome request. NetAware uses selective network evidence and returns a recommendation — Rocket Bank owns the financial decision.",
    briefingHref: "/demo/rocket-bank/high-value-payment-protection",
    closeHref: "/close",
    evidenceReuseHref: "/demo/rocket-bank/account-recovery-anomaly/run",
    request: {
      intent: "assess_network_trust",
      subject: { transactionId: "RB-78421", phoneNumber: "+1••••••0198" },
      context: { amount: 25000, currency: "USD" },
    },
    enterpriseLabel: "Rocket Bank",
  },
  "acme-manufacturing/critical-inspection-camera": {
    kicker: "Acme Manufacturing · Quality Inspection",
    title: "Maintain inspection experience",
    lede:
      "The application asks to maintain the camera experience — not to call QoD. NetAware observes, acts when the objective breaches, and verifies.",
    briefingHref: "/demo/acme-manufacturing/critical-inspection-camera",
    closeHref: "/close",
    request: {
      intent: "maintain_inspection_experience",
      subject: { cameraId: "ACME-CAM-14", lineId: "LINE-B" },
      context: { sloMs: 40 },
    },
    enterpriseLabel: "Acme Manufacturing",
  },
  "citycare-health/pharmacy-age-gate": {
    kicker: "CityCare Health · Pharmacy Eligibility",
    title: "Verify pharmacy age gate",
    lede:
      "Minimum permitted capability only. NetAware returns narrow eligibility — the pharmacist owns dispensing.",
    briefingHref: "/demo/citycare-health/pharmacy-age-gate",
    closeHref: "/close",
    request: {
      intent: "verify_pharmacy_age_gate",
      subject: { transactionId: "RX-10442", phoneNumber: "+1••••••8843" },
      context: { ageThreshold: 18 },
    },
    enterpriseLabel: "CityCare Health",
  },
  "rocket-bank/account-recovery-anomaly": {
    kicker: "Rocket Bank · Secondary",
    title: "Assess recovery continuity",
    secondary: true,
    lede:
      "After trust assessment, normalized evidence is reused when purpose, subject, TTL and policy allow. No duplicate Network API calls.",
    briefingHref: "/demo/rocket-bank/account-recovery-anomaly",
    closeHref: "/close",
    request: {
      intent: "assess_recovery_continuity",
      subject: { recoveryId: "RB-REC-19", phoneNumber: "+1••••••0198" },
      context: { channel: "web" },
    },
    enterpriseLabel: "Rocket Bank",
  },
};

const BASIC_TABS = [
  ["overview", "Overview"],
  ["discovery", "Discovery"],
  ["outcome", "Outcome"],
];

const ADVANCED_TABS = [
  ["overview", "Overview"],
  ["discovery", "Discovery"],
  ["flow", "Live Flow"],
  ["decisions", "Decisions"],
  ["apis", "APIs"],
  ["policy", "Policy"],
];

const LANE_LABELS = {
  "ROCKET BANK / AGENT": "APPLICATION / AGENT",
  "HIGH FLIGHT AGENT": "APPLICATION / AGENT",
  "ACME INSPECTION AGENT": "APPLICATION / AGENT",
  "CITYCARE AGENT": "APPLICATION / AGENT",
  "CATALOG / FINDERS": "API CATALOG / FINDERS",
  "DOMAIN APIs": "DOMAIN / ENTERPRISE",
  "ENTERPRISE GROUND OPERATIONS": "DOMAIN / ENTERPRISE",
  "TELCO FINDER": "API CATALOG / FINDERS",
  "API FINDER": "API CATALOG / FINDERS",
  AGGREGATOR: "AGGREGATOR",
};

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function stateTone(state) {
  const s = String(state || "");
  if (["INVOKED", "PERMITTED", "AUTHORIZED", "ALLOWED", "VERIFIED", "EVIDENCE_REUSED", "SELECTED"].includes(s))
    return "ok";
  if (["BLOCKED_BY_POLICY", "NOT_AUTHORIZED", "NOT_AVAILABLE"].includes(s)) return "warn";
  if (["REPLANNED", "NOT_REQUIRED"].includes(s)) return "muted";
  return "muted";
}

function laneLabel(lane) {
  return LANE_LABELS[lane] || lane;
}

function stepIcon(state) {
  if (state === "INVOKED" || state === "COMPLETED" || state === "EVIDENCE_REUSED") return "✓";
  if (state === "BLOCKED_BY_POLICY") return "✗";
  if (state === "NOT_REQUIRED") return "—";
  if (state === "PLANNED") return "○";
  return "·";
}

export default function Runtime({ enterpriseId, useCaseId }) {
  const key = `${enterpriseId}/${useCaseId}`;
  const scenario = SCENARIOS[key];
  const [trace, setTrace] = useState(null);
  const [valueClarity, setValueClarity] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState("overview");
  const [lens, setLens] = useState(readLens);
  const [beatN, setBeatN] = useState(0);
  const [paused, setPaused] = useState(false);
  const [speed, setSpeed] = useState(1);
  const started = useRef(0);
  const timer = useRef(0);
  const traceRef = useRef(null);

  if (!scenario) {
    return (
      <p className="err">
        No live run configured for {enterpriseId}/{useCaseId}.{" "}
        <a href={href("/demo")}>Return to demo picker</a>.
      </p>
    );
  }

  const beats = trace?.beats || [];
  const maxBeat = beats.at(-1)?.n || 0;
  const visibleBeats = useMemo(() => beats.filter((b) => b.n <= beatN), [beats, beatN]);
  const activeLane = visibleBeats.at(-1)?.lane;
  const done = Boolean(trace && beatN >= maxBeat);
  const lanes = useMemo(() => {
    const fromBeats = [...new Set(beats.map((b) => b.lane))];
    return fromBeats.length ? fromBeats : [];
  }, [beats]);

  useEffect(() => {
    return () => window.clearInterval(timer.current);
  }, []);

  useEffect(() => {
    api(`/demo/${enterpriseId}/${useCaseId}`)
      .then((body) => setValueClarity(body.valueClarity || null))
      .catch(() => setValueClarity(null));
  }, [enterpriseId, useCaseId]);

  useEffect(() => {
    const onLens = (event) => setLens(event.detail === "ADVANCED" ? "ADVANCED" : "BASIC");
    window.addEventListener(LENS_EVENT, onLens);
    return () => window.removeEventListener(LENS_EVENT, onLens);
  }, []);

  const tabs = lens === "ADVANCED" ? ADVANCED_TABS : BASIC_TABS;
  useEffect(() => {
    const ids = (lens === "ADVANCED" ? ADVANCED_TABS : BASIC_TABS).map(([id]) => id);
    if (!ids.includes(tab)) setTab("discovery");
  }, [lens, tab]);

  const changeLens = (next) => {
    writeLens(next);
    setLens(next);
  };

  const clearTimer = () => window.clearInterval(timer.current);

  const startTimer = (payload, fromMs = 0) => {
    clearTimer();
    started.current = Date.now() - fromMs / speed;
    setPaused(false);
    timer.current = window.setInterval(() => {
      const elapsed = (Date.now() - started.current) * speed;
      const reached = (payload.beats || []).filter((b) => b.tMs <= elapsed);
      const n = reached.length ? reached[reached.length - 1].n : 0;
      setBeatN(n);
      if (n >= (payload.beats || []).at(-1)?.n) clearTimer();
    }, 60);
  };

  const play = (payload, { fromBeat = 0 } = {}) => {
    traceRef.current = payload;
    setTrace(payload);
    const lastN = (payload.beats || []).at(-1)?.n || 0;
    if (readLens() === "BASIC") {
      clearTimer();
      setBeatN(lastN);
      setPaused(true);
      return;
    }
    const fromMs = fromBeat ? (payload.beats || []).find((b) => b.n === fromBeat)?.tMs || 0 : 0;
    setBeatN(fromBeat);
    startTimer(payload, fromMs);
  };

  const run = async () => {
    setBusy(true);
    setError("");
    try {
      if (scenario.request.intent === "assess_recovery_continuity") {
        await apiPost("/executions/reset", {});
        await apiPost("/intents", {
          intent: "assess_network_trust",
          subject: { transactionId: "RB-78421", phoneNumber: "+1••••••0198" },
          context: { amount: 25000, currency: "USD" },
        });
      }
      play(await apiPost("/intents", scenario.request));
      setTab(readLens() === "BASIC" ? "discovery" : "overview");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusy(false);
    }
  };

  const replay = () => {
    if (!traceRef.current) return;
    play(traceRef.current);
  };

  const pause = () => {
    clearTimer();
    setPaused(true);
  };

  const resume = () => {
    if (!traceRef.current) return;
    const current = (traceRef.current.beats || []).find((b) => b.n === beatN);
    startTimer(traceRef.current, current?.tMs || 0);
  };

  const step = () => {
    clearTimer();
    setPaused(true);
    setBeatN((n) => Math.min(n + 1, maxBeat));
  };

  const skipToEnd = () => {
    clearTimer();
    setPaused(true);
    setBeatN(maxBeat);
  };

  const reset = async () => {
    clearTimer();
    setTrace(null);
    traceRef.current = null;
    setBeatN(0);
    setPaused(false);
    setError("");
    try {
      await apiPost("/executions/reset", {});
    } catch {
      /* empty store is fine */
    }
  };

  const economy = trace?.economy;
  const visibleInvocations =
    done || !trace
      ? trace?.invocations
      : trace.invocations.filter((i) => visibleBeats.some((b) => b.title === i.operationId));

  return (
    <div>
      {scenario.secondary ? <p className="banner warn">Secondary demonstration · evidence reuse</p> : null}
      <p className="kicker">{scenario.kicker}</p>
      <h1>
        <span>{scenario.title}</span>
      </h1>
      <p className="lede">{scenario.lede}</p>
      {valueClarity?.headline ? <p className="lede value-headline">{valueClarity.headline}</p> : null}
      <AxLoop compact activeIndex={done ? 7 : Math.min(Math.floor(beatN / 3), 7)} />

      <div className="hero-actions run-controls">
        <button className="primary" type="button" disabled={busy} onClick={run}>
          Run
        </button>
        <LensToggle lens={lens} onChange={changeLens} />
        {lens === "ADVANCED" ? (
          <>
            <button type="button" disabled={!trace || busy} onClick={paused ? resume : pause}>
              {paused ? "Resume" : "Pause"}
            </button>
            <button type="button" disabled={!trace || busy} onClick={step}>
              Step
            </button>
            <button type="button" disabled={!trace || busy} onClick={replay}>
              Replay
            </button>
            <button type="button" disabled={!trace || busy} onClick={skipToEnd}>
              Skip to end
            </button>
            <label className="speed-toggle tiny">
              Speed
              <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))}>
                <option value={1}>1×</option>
                <option value={2}>2×</option>
                <option value={4}>4×</option>
              </select>
            </label>
          </>
        ) : null}
        <button type="button" disabled={!trace || busy} onClick={reset}>
          Reset
        </button>
        <a className="nav-link" href={href(scenario.briefingHref)}>
          Briefing
        </a>
        {scenario.evidenceReuseHref ? (
          <a className="nav-link" href={href(scenario.evidenceReuseHref)}>
            See evidence reuse
          </a>
        ) : null}
      </div>
      {error ? <p className="err">{error}</p> : null}

      {trace ? (
        <>
          <div className="economy">
            {(trace.discoverySummary?.pipeline || []).length && lens === "BASIC"
              ? trace.discoverySummary.pipeline.map((step) => (
                  <article key={step.label}>
                    <span>{step.label}</span>
                    <strong>{step.count}</strong>
                  </article>
                ))
              : (
                  <>
                    <article>
                      <span>Mapped</span>
                      <strong>{economy?.mappedToIntent}</strong>
                    </article>
                    <article>
                      <span>Invoked</span>
                      <strong>{economy?.invoked}</strong>
                    </article>
                    <article>
                      <span>Reused</span>
                      <strong>{economy?.evidenceReused || 0}</strong>
                    </article>
                    <article>
                      <span>Not required</span>
                      <strong>{(economy?.consideredNotRequired || 0) + (economy?.notRequiredUnmapped || 0)}</strong>
                    </article>
                    <article>
                      <span>Blocked</span>
                      <strong>{economy?.blockedByPolicy || 0}</strong>
                    </article>
                  </>
                )}
          </div>
          <div className="tabs">
            {tabs.map(([id, label]) => (
              <button key={id} className={tab === id ? "on" : ""} type="button" onClick={() => setTab(id)}>
                {label}
              </button>
            ))}
          </div>

          {tab === "overview" ? (
            <Overview trace={trace} done={done} scenario={scenario} decisions={trace.decisions} lens={lens} />
          ) : null}
          {tab === "discovery" ? (
            <DiscoveryView
              trace={trace}
              lens={lens}
              onOpenAdvanced={() => {
                changeLens("ADVANCED");
                setTab("flow");
              }}
            />
          ) : null}
          {tab === "outcome" ? <OutcomeView trace={trace} /> : null}
          {tab === "flow" ? <LiveFlow beats={visibleBeats} activeLane={activeLane} lanes={lanes} /> : null}
          {tab === "decisions" ? <Decisions rows={trace.decisions} trace={trace} /> : null}
          {tab === "apis" ? <Apis rows={visibleInvocations} evidence={trace.evidence} /> : null}
          {tab === "policy" ? <Policy trace={trace} /> : null}

          {done && scenario.closeHref ? (
            <p className="section tiny">
              <a href={href(scenario.closeHref)}>Continue to product close →</a>
            </p>
          ) : null}
        </>
      ) : (
        <section className="section">
          <ValueClarityPanel clarity={valueClarity} />
          <div className="grid-2 section">
            <article className="panel">
              <h3>What the application sends</h3>
              <pre className="code-block">{JSON.stringify(scenario.request, null, 2)}</pre>
            </article>
            <article className="panel">
              <h3>What NetAware already knows</h3>
              <p className="tiny">
                Enterprise, application, agent, purpose, subscriptions, policy, consent, DPA, autonomy — from onboarding.
              </p>
            </article>
          </div>
        </section>
      )}
    </div>
  );
}

function ValueClarityPanel({ clarity }) {
  if (!clarity?.myWorld) return null;
  return (
    <div className="value-ladder section">
      <article className="panel domain-lane">
        <h3>{clarity.myWorld.title || "My world"}</h3>
        <ul className="list compact">
          {(clarity.myWorld.items || []).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
      <article className="panel network-lane">
        <h3>{clarity.networkAdds?.title || "Network adds"}</h3>
        <ul className="list compact">
          {(clarity.networkAdds?.items || []).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
      <article className="panel ax-lane">
        <h3>{clarity.netawareAx?.title || "NetAware AX"}</h3>
        <ul className="list compact">
          {(clarity.netawareAx?.items || []).slice(0, 3).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
    </div>
  );
}

function PlanPanel({ plan, highlight }) {
  if (!plan) return null;
  return (
    <article className={`panel${highlight ? " outcome ready" : ""}`} style={{ marginBottom: 8 }}>
      <h3>{plan.label || `Plan v${plan.version}`}</h3>
      {plan.note ? <p className="tiny">{plan.note}</p> : null}
      <ol className="plan-steps">
        {(plan.steps || []).map((step) => (
          <li key={step.n}>
            <span>{stepIcon(step.state)} </span>
            {step.action}
            {step.state ? <Pill tone={stateTone(step.state)}> {step.state.replaceAll("_", " ")}</Pill> : null}
          </li>
        ))}
      </ol>
    </article>
  );
}

function Overview({ trace, done, scenario, decisions, lens }) {
  const outcome = trace.outcome || {};
  const blocked = (decisions || []).filter((d) => d.state === "BLOCKED_BY_POLICY");
  const reused = (decisions || []).filter((d) => d.state === "EVIDENCE_REUSED");
  const notRequired = (decisions || []).filter((d) => d.state === "NOT_REQUIRED");
  const domainEvidence = (trace.invocations || []).filter(
    (i) => i.apiKind === "DOMAIN" || i.apiKind === "ENTERPRISE"
  );
  const networkEvidence = (trace.invocations || []).filter((i) => (i.apiKind || "NETWORK") === "NETWORK");

  return (
    <div>
      {done ? (
        <section className="contribution-strip section">
          <article className="inset domain-lane">
            <h3>Business / domain evidence</h3>
            {domainEvidence.length ? (
              <ul className="list compact">
                {domainEvidence.map((row) => (
                  <li key={row.id}>
                    <strong>{lens === "ADVANCED" ? row.operationId : row.familyLabel || row.providerLabel || "Enterprise system"}</strong>
                    <span className="tiny"> · {row.providerLabel || "Enterprise API"}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="tiny">Enterprise context from configured onboarding.</p>
            )}
          </article>
          <article className="inset network-lane">
            <h3>Network contribution</h3>
            {networkEvidence.length ? (
              <ul className="list compact">
                {networkEvidence.map((row) => (
                  <li key={row.id}>
                    <strong>{lens === "ADVANCED" ? row.operationId : row.familyLabel || "Network capability"}</strong>
                    <span className="tiny"> · {row.familyLabel}</span>
                  </li>
                ))}
              </ul>
            ) : reused.length ? (
              <p className="tiny">Evidence reused — no duplicate Network API calls.</p>
            ) : (
              <p className="tiny">No Network APIs invoked in this run.</p>
            )}
          </article>
          <article className="inset ax-lane">
            <h3>NetAware decision</h3>
            <p>{outcome.summary || trace.replan?.narrative || "Minimum sufficient path under configured policy."}</p>
            {notRequired.length ? (
              <p className="tiny">{notRequired.length} capability(ies) considered but not required.</p>
            ) : null}
            {blocked.length ? (
              <p className="tiny">{blocked.length} blocked by configured policy.</p>
            ) : null}
          </article>
          <article className="inset outcome-lane">
            <h3>Business outcome</h3>
            <p className="kicker">{outcome.outcome}</p>
            {outcome.recommendedAction ? (
              <p className="tiny">Recommended · {outcome.recommendedAction}</p>
            ) : null}
          </article>
        </section>
      ) : null}

      <section className="grid-2 section">
        <article className="panel">
          <h3>What was asked</h3>
          <p className="tiny">Intent · {trace.intentId}</p>
          <pre className="code-block">{JSON.stringify(trace.request, null, 2)}</pre>
        </article>
        <article className="panel">
          <h3>What NetAware already knew</h3>
          <dl className="dl">
            {(trace.knownFromConfiguration?.rows || []).slice(0, 8).map((row) => (
              <div key={row.label} style={{ display: "contents" }}>
                <dt>{row.label}</dt>
                <dd>{row.value}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>

      <section className="grid-3 section">
        <article className="inset">
          <h3>Blocked / changed</h3>
          <p>{blocked.length ? `${blocked.length} blocked by policy` : "None blocked"}</p>
          {trace.replan ? <p className="tiny">{trace.replan.trigger}</p> : null}
          {trace.conditionChange ? <p className="tiny">{trace.conditionChange.trigger}</p> : null}
        </article>
        <article className="inset">
          <h3>Not required</h3>
          <p>{notRequired.length || reused.length ? `${notRequired.length + reused.length} capabilities skipped` : "—"}</p>
          {reused.length ? <p className="tiny">{reused.length} evidence reused</p> : null}
        </article>
        <article className="inset">
          <h3>Decision owner</h3>
          <p>{outcome.decisionOwner?.replaceAll("_", " ") || "Enterprise"}</p>
          {trace.autonomy?.selectedLevel ? (
            <p className="tiny">Autonomy · {trace.autonomy.selectedLevel}</p>
          ) : null}
        </article>
      </section>

      {(trace.planHistory || []).length || trace.plan ? (
        <section className="section">
          <h3>Plan</h3>
          {trace.replan ? <p className="tiny">{trace.replan.narrative}</p> : null}
          {(trace.planHistory || []).map((plan, idx) => (
            <PlanPanel key={plan.id} plan={plan} highlight={idx === (trace.planHistory || []).length - 1 && done} />
          ))}
          {!trace.planHistory?.length && trace.plan ? <PlanPanel plan={trace.plan} highlight={done} /> : null}
        </section>
      ) : null}

      <article className={`panel outcome ${done ? "ready" : ""}`}>
        <h3>Business outcome</h3>
        {done ? (
          <>
            <p className="kicker">{outcome.outcome}</p>
            <p className="plus-line">{outcome.summary}</p>
            <details className="req">
              <summary>Technical outcome fields</summary>
              <pre>{JSON.stringify(outcome, null, 2)}</pre>
            </details>
          </>
        ) : (
          <p className="tiny">Outcome appears when the run completes.</p>
        )}
      </article>
    </div>
  );
}

function LiveFlow({ beats, activeLane, lanes }) {
  return (
    <section className="section">
      <p className="tiny">Who called whom — route types shown in API trace.</p>
      <ol className="lanes" style={{ gridTemplateColumns: `repeat(${Math.min(lanes.length, 5)}, 1fr)` }}>
        {lanes.map((lane) => (
          <li key={lane} className={lane === activeLane ? "on" : ""} title={lane}>
            {laneLabel(lane)}
          </li>
        ))}
      </ol>
      <ol className="beat-log">
        {beats.map((b) => (
          <li key={b.n}>
            <time>{b.tMs}ms</time>
            <strong>{b.title}</strong>
            <span>{b.detail}</span>
            <span className="tiny"> · {laneLabel(b.lane)}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

function Decisions({ rows, trace }) {
  const stateImpact = (row) => {
    if (row.state === "INVOKED") return "Contributed evidence or action to the trace.";
    if (row.state === "NOT_REQUIRED") return "Considered — network is not the limiting factor or not needed.";
    if (row.state === "BLOCKED_BY_POLICY") return "Would add value but blocked by configured consent/policy.";
    if (row.state === "EVIDENCE_REUSED") return "Prior network evidence reused — no duplicate call.";
    return "Evaluated under configured mapping.";
  };
  return (
    <section className="section">
      <p className="tiny">Why relevant? What unique value? Why invoked / not invoked / blocked? What changed?</p>
      {(rows || []).map((row) => (
        <article key={row.id} className="panel" style={{ marginBottom: 8 }}>
          <div className="chips" style={{ marginBottom: 8 }}>
            <Pill tone={stateTone(row.state)}>{row.state?.replaceAll("_", " ")}</Pill>
            {row.relevant ? <Pill>Relevant</Pill> : <Pill tone="muted">Not relevant</Pill>}
          </div>
          <h2>{row.label}</h2>
          {row.operationId ? (
            <p className="tiny">
              Candidate · <code>{row.operationId}</code>
            </p>
          ) : null}
          <dl className="dl decision-why">
            <dt>Why relevant?</dt>
            <dd>{row.why}</dd>
            <dt>What changed?</dt>
            <dd>{stateImpact(row)}</dd>
          </dl>
          {row.state === "EVIDENCE_REUSED" && trace?.evidence ? (
            <p className="tiny">
              Source · {(trace.evidence.find((e) => e.operationId === row.operationId) || {}).sourceExecutionId}
            </p>
          ) : null}
        </article>
      ))}
    </section>
  );
}

function Apis({ rows, evidence }) {
  if (!rows?.length && !(evidence || []).some((e) => e.reused)) {
    return (
      <section className="section">
        <p className="tiny">No Network APIs invoked — evidence may have been reused.</p>
        {(evidence || [])
          .filter((e) => e.reused)
          .map((e) => (
            <article key={e.id} className="panel" style={{ marginBottom: 8 }}>
              <Pill tone="ok">EVIDENCE REUSED</Pill>
              <h2>
                <code>{e.operationId}</code>
              </h2>
              <p className="tiny">
                Source {e.sourceExecutionId} · age {e.ageSeconds}s · TTL check passed
              </p>
            </article>
          ))}
      </section>
    );
  }
  const network = (rows || []).filter((r) => (r.apiKind || "NETWORK") === "NETWORK");
  const domain = (rows || []).filter((r) => r.apiKind === "DOMAIN" || r.apiKind === "ENTERPRISE");

  return (
    <section className="section">
      {domain.length ? (
        <>
          <h3>Domain / Enterprise APIs</h3>
          {domain.map((row) => (
            <article key={row.id} className="panel" style={{ marginBottom: 8 }}>
              <div className="chips">
                <Pill tone="ok">{row.apiKind}</Pill>
                <Pill>SIMULATED</Pill>
              </div>
              <h2>
                <code>{row.operationId}</code>
              </h2>
              <p className="tiny">
                {row.providerLabel} · {row.latencyMs} ms
              </p>
            </article>
          ))}
        </>
      ) : null}
      {network.length ? (
        <>
          <h3 style={{ marginTop: domain.length ? 16 : 0 }}>Network APIs</h3>
          {network.map((row) => (
            <article key={row.id} className="panel" style={{ marginBottom: 8 }}>
              <p className="kicker">{row.familyLabel}</p>
              <h2>
                <code>{row.operationId}</code>
              </h2>
              <div className="chips">
                <Pill tone="ok">NetAware {(row.businessStatus || "").replaceAll("_", " ")}</Pill>
                {row.camaraApiVersion ? <Pill>CAMARA API {row.camaraApiVersion}</Pill> : null}
                {row.apiVersionMaturity ? (
                  <Pill tone={apiVersionMaturityTone(row.apiVersionMaturity)}>
                    API version {row.apiVersionMaturity}
                  </Pill>
                ) : null}
                <Pill>{row.routeType}</Pill>
              </div>
              {row.camaraProjectLifecycle ? (
                <p className="tiny" style={{ marginTop: 8 }}>
                  CAMARA project lifecycle · {row.camaraProjectLifecycle}
                </p>
              ) : null}
              <dl className="dl" style={{ marginTop: 10 }}>
                <dt>Method</dt>
                <dd>{row.method}</dd>
                <dt>Provider</dt>
                <dd>{row.providerLabel}</dd>
                <dt>Correlation</dt>
                <dd>{row.correlationId}</dd>
                <dt>Latency</dt>
                <dd>{row.latencyMs} ms (simulated)</dd>
              </dl>
            </article>
          ))}
        </>
      ) : null}
    </section>
  );
}

function Policy({ trace }) {
  const stages = [
    ["ACTOR_INTENT", "1 · Actor / Intent"],
    ["CAPABILITY_API", "2 · Capability / API"],
    ["EVIDENCE_REUSE", "2 · Evidence reuse"],
    ["AUTONOMY_ACTION", "3 · Autonomy / Action"],
  ];
  const auto = trace.autonomy || {};
  const autoRows = Object.entries(auto).filter(
    ([k]) => !["note", "source", "selectedAction", "selectedLevel", "approvalRequired"].includes(k)
  );

  return (
    <section className="section">
      <p className="tiny">CONFIGURED POLICY · not AI-invented governance</p>
      {stages.map(([stage, label]) => {
        const rows = (trace.policyEvaluations || []).filter((p) => p.stage === stage);
        if (!rows.length) return null;
        return (
          <div key={stage} className="section">
            <h3>{label}</h3>
            {rows.map((p) => (
              <article key={p.id} className="inset" style={{ marginBottom: 8 }}>
                <div className="chips">
                  <Pill tone={stateTone(p.result)}>{p.result}</Pill>
                  <Pill>{p.source}</Pill>
                </div>
                <p>
                  <strong>{p.subject}</strong> — {p.detail}
                </p>
              </article>
            ))}
          </div>
        );
      })}
      <article className="panel">
        <h3>Autonomy envelope</h3>
        <dl className="dl">
          {autoRows.map(([k, v]) => (
            <div key={k} style={{ display: "contents" }}>
              <dt>{k.replaceAll("_", " ")}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
        <p className="tiny">{auto.note}</p>
      </article>
    </section>
  );
}
