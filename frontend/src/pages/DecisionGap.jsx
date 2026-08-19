export function DecisionGapVisual({ trace, lens }) {
  const gap = trace?.decisionGap;
  if (!gap) return null;
  const already = gap.alreadyHave || [];
  const adds = gap.networkAdds || [];
  const ax = gap.ax || [];
  return (
    <section className="decision-gap" aria-label="Network Decision Gap">
      <p className="kicker">Network Decision Gap</p>
      <ol className="gap-flow">
        <li className="gap-node domain">
          <span className="kicker">You already have</span>
          <strong>Enterprise systems</strong>
          <ul className="list compact">
            {already.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </li>
        <li className="gap-arrow" aria-hidden="true">
          ↓
        </li>
        <li className="gap-node">
          <span className="kicker">You need to decide</span>
          <strong>{gap.decide}</strong>
        </li>
        <li className="gap-arrow" aria-hidden="true">
          ↓
        </li>
        <li className="gap-node gap-highlight">
          <span className="kicker">Network Decision Gap</span>
          <strong>{gap.gap}</strong>
        </li>
        <li className="gap-arrow" aria-hidden="true">
          ↓
        </li>
        <li className="gap-node network">
          <span className="kicker">Network adds</span>
          <strong>{adds[0] || "Network capability"}</strong>
          {adds.slice(1).map((item) => (
            <span className="tiny" key={item}>
              {item}
            </span>
          ))}
        </li>
        <li className="gap-arrow" aria-hidden="true">
          ↓
        </li>
        <li className="gap-node ax">
          <span className="kicker">NetAware AX</span>
          <div className="gap-ax-pills">
            {ax.map((item) => (
              <span className="pill" key={item}>
                {item}
              </span>
            ))}
          </div>
        </li>
        <li className="gap-arrow" aria-hidden="true">
          ↓
        </li>
        <li className="gap-node outcome">
          <span className="kicker">Outcome</span>
          <strong>{trace?.outcome?.outcome || gap.outcome}</strong>
          {lens === "ADVANCED" && trace?.scenarioComplexity ? (
            <span className="tiny">
              Scenario complexity {trace.scenarioComplexity} · lens is presentation depth, not complexity
            </span>
          ) : null}
        </li>
      </ol>
    </section>
  );
}

export function FiveStateTable({ trace }) {
  const rows = trace?.candidateFiveStates || [];
  if (!rows.length) return null;
  return (
    <article className="panel">
      <h3>Relevant · Available · Entitled · Permitted · Needed</h3>
      <p className="tiny">Same discovery engine. Presentation only — not a second planner.</p>
      <div className="matrix-wrap">
        <table className="discovery-matrix">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Relevant</th>
              <th>Available</th>
              <th>Entitled</th>
              <th>Permitted</th>
              <th>Needed</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.candidate || row.capability}>
                <td>{row.capability || row.candidate}</td>
                <td>{row.relevant}</td>
                <td>{row.available}</td>
                <td>{row.entitled}</td>
                <td>{row.permitted}</td>
                <td>{row.needed}</td>
                <td>
                  <strong>{row.action}</strong>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  );
}

export function HfBaggageWorld({ trace }) {
  const visual = trace?.hfVisual || {};
  const steps = visual.baggageWorld || [];
  const outcome = trace?.outcome?.outcome || visual.outcome;
  if (!steps.length) return null;
  return (
    <section className="nv-path-visual hf-baggage-world">
      <p className="kicker">Baggage world — airline systems stay in place</p>
      <p className="lede nv-headline">{visual.headline}</p>
      <ol className="nv-flow">
        {steps.map((step, idx) => (
          <li key={step.id} className={`nv-node ${step.state || ""}`}>
            {idx ? (
              <div className="pipeline-arrow" aria-hidden="true">
                ↓
              </div>
            ) : null}
            <div className={`nv-card ${step.state || ""}`}>
              <strong>{step.label}</strong>
              {step.detail ? <span className="tiny">{step.detail}</span> : null}
              {step.state === "ok" ? <span className="nv-check">✓</span> : null}
              {step.state === "break" ? <span className="nv-x">✕</span> : null}
            </div>
          </li>
        ))}
      </ol>
      <article className="nv-card gap-highlight">
        <p className="kicker">Network Decision Gap</p>
        <strong>{visual.gap || "Can this assigned connected scanner complete the digital workflow?"}</strong>
        <span className="tiny">DEVICE REACHABILITY · DATA reachable?</span>
      </article>
      <div className="vis-split">
        <article className={`nv-card ${outcome === "CONTINUE" ? "ok" : ""}`}>
          <p className="kicker">YES</p>
          <strong>CONTINUE</strong>
        </article>
        <article className={`nv-card ${outcome === "SWAP_DEVICE" ? "break" : ""}`}>
          <p className="kicker">NO</p>
          <strong>SWAP DEVICE</strong>
          {outcome === "SWAP_DEVICE" ? (
            <span className="tiny">Enterprise handheld inventory performs device reassignment.</span>
          ) : null}
        </article>
      </div>
      <p className="tiny">
        NETWORK PROVIDES REACHABILITY EVIDENCE. ENTERPRISE SYSTEM PERFORMS DEVICE REASSIGNMENT. NETAWARE DOES NOT TRACK
        OR MOVE THE BAG.
      </p>
    </section>
  );
}

const HF_VARIANTS = [
  { id: "scanner-ready", label: "Assigned scanner reachable" },
  { id: "scanner-unreachable", label: "Assigned scanner not reachable" },
];

export function HfVariantBar({ variantId, onChange, disabled }) {
  return (
    <section className="nv-variant-bar">
      <p className="kicker">Simulate operational context</p>
      <p className="tiny">
        Presenter control only. The application still sends one Intent. NetAware resolves whether the assigned scanner can
        participate — the airline does not choose a Network API.
      </p>
      <div className="nv-variant-row">
        {HF_VARIANTS.map((row) => (
          <button
            key={row.id}
            type="button"
            className={variantId === row.id ? "on primary" : ""}
            disabled={disabled}
            onClick={() => onChange(row.id)}
          >
            {row.label}
          </button>
        ))}
      </div>
    </section>
  );
}

export function HfDemandNote({ trace }) {
  const opp = trace?.networkOpportunity || trace?.demandSupply || {};
  if (!opp.businessDemand && !opp.note) return null;
  const unreachableSuccess = opp.apiSuccessfullyReportedUnreachable;
  return (
    <section className={`network-opportunity ${unreachableSuccess ? "ok" : opp.fulfilled === false ? "gap" : "ok"}`}>
      <p className="kicker">Demand vs API result</p>
      <h3>
        {unreachableSuccess
          ? "API succeeded — device reported unreachable"
          : opp.fulfilled === false
            ? "Unfulfilled qualified demand"
            : "Qualified demand fulfilled"}
      </h3>
      <p className="tiny">{opp.note}</p>
      {unreachableSuccess ? (
        <p className="tiny">
          Unreachable is not the same as an unfulfilled Network API. The Reachability call worked; the business action
          changed to SWAP_DEVICE.
        </p>
      ) : null}
    </section>
  );
}
