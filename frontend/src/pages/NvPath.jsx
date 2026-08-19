function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

const VARIANTS = [
  { id: "cellular-nv1", label: "Cellular / Provider A" },
  { id: "wifi-nv2", label: "Wi-Fi / Provider A" },
  { id: "wifi-ecs-gap", label: "Wi-Fi / Provider B" },
];

export function NvVariantBar({ variantId, onChange, disabled }) {
  return (
    <section className="nv-variant-bar">
      <p className="kicker">Simulate runtime context</p>
      <p className="tiny">
        Presenter / demo simulation only. The application does not choose Cellular, Wi-Fi, NV1, NV2, or ECS. Those are
        runtime context and NetAware path selection.
      </p>
      <div className="nv-who-chooses">
        <article className="nv-card ok">
          <p className="kicker">Application chooses</p>
          <strong>Intent</strong>
          <span className="tiny">Verify this mobile number</span>
        </article>
        <article className="nv-card">
          <p className="kicker">NetAware resolves</p>
          <strong>Context</strong>
          <span className="tiny">Access type · operator · readiness</span>
        </article>
        <article className="nv-card">
          <p className="kicker">NetAware chooses</p>
          <strong>NV1 / NV2 path</strong>
          <span className="tiny">Not requested on the Intent</span>
        </article>
      </div>
      <div className="nv-variant-row">
        {VARIANTS.map((row) => (
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

export function NvIntentPin({ trace }) {
  const visual = trace?.nvVisual || {};
  return (
    <article className="nv-intent-pin">
      <p className="kicker">Business event</p>
      <strong>{visual.businessEvent || "CUSTOMER SIGNING IN"}</strong>
      <div className="pipeline-arrow" aria-hidden="true">
        ↓
      </div>
      <p className="kicker">Intent — pinned across variants</p>
      <h2>Verify this mobile number</h2>
      <p className="tiny">
        <code>verify_mobile_number</code> · the application does not request NV1, NV2, TS.43, ECS, or a CAMARA
        operationId.
      </p>
    </article>
  );
}

export function NvPathVisual({ trace }) {
  const visual = trace?.nvVisual || {};
  const steps = visual.steps || [];
  const ps = trace?.pathSelection || {};
  return (
    <section className="nv-path-visual">
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
              {step.state === "filtered" ? <span className="nv-x">✕</span> : null}
              {step.state === "ok" ? <span className="nv-check">✓</span> : null}
              {step.state === "break" ? <span className="nv-x">✕</span> : null}
            </div>
          </li>
        ))}
      </ol>
      <div className="grid-2 nv-path-cards">
        <article className={`nv-card ${(ps.paths || []).find((p) => p.id === "NV1_NETWORK_BASED")?.result === "SELECTED" ? "ok" : ""} ${(ps.paths || []).find((p) => p.id === "NV1_NETWORK_BASED")?.result === "FILTERED" ? "filtered" : ""}`}>
          <p className="kicker">Fulfillment path</p>
          <h3>NV1 · network-based</h3>
          <p className="tiny">{(ps.paths || []).find((p) => p.id === "NV1_NETWORK_BASED")?.humanReason}</p>
        </article>
        <article
          className={`nv-card ${(ps.paths || []).find((p) => p.id === "NV2_OPERATOR_TOKEN")?.result === "SELECTED" ? "ok" : ""} ${(ps.paths || []).find((p) => p.id === "NV2_OPERATOR_TOKEN")?.reasonCode === "ENTITLEMENT_SERVER_UNAVAILABLE" ? "break" : ""} ${(ps.paths || []).find((p) => p.id === "NV2_OPERATOR_TOKEN")?.result === "FILTERED" ? "filtered" : ""}`}
        >
          <p className="kicker">Fulfillment path</p>
          <h3>NV2 · operator token</h3>
          <p className="tiny">{(ps.paths || []).find((p) => p.id === "NV2_OPERATOR_TOKEN")?.humanReason}</p>
        </article>
      </div>
    </section>
  );
}

export function NvPathVsOperation({ trace, lens }) {
  const ps = trace?.pathSelection || {};
  if (lens !== "ADVANCED") return null;
  return (
    <article className="panel nv-path-op">
      <h3>Path vs operation</h3>
      <div className="grid-2">
        <div>
          <p className="kicker">Fulfillment path</p>
          <p>How the subscriber is authenticated / bound</p>
          <p>
            <code>{ps.selectedPath || "UNAVAILABLE"}</code>
          </p>
        </div>
        <div>
          <p className="kicker">CAMARA operation</p>
          <p>What Number Verification is asked to do</p>
          <p>
            <code>{ps.selectedOperation || "not invoked"}</code>
          </p>
        </div>
      </div>
      <p className="tiny">Do not label phoneNumberVerify = NV1 or phoneNumberShare = NV2.</p>
      {(ps.tokenFlowConceptual || []).length ? (
        <div className="nv-token-flow">
          <p className="kicker">Simulated / conceptual path</p>
          <ol className="nv-flow compact">
            {ps.tokenFlowConceptual.map((step, idx) => (
              <li key={step.id}>
                {idx ? <span className="tiny"> → </span> : null}
                {step.label}
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </article>
  );
}

export function NetworkOpportunity({ trace }) {
  const opp = trace?.networkOpportunity || {};
  if (!opp.businessDemand) return null;
  const failed = opp.fulfilled === false;
  return (
    <section className={`network-opportunity ${failed ? "gap" : "ok"}`}>
      <p className="kicker">See network opportunity</p>
      <h3>{failed ? "Unfulfilled qualified demand" : "Qualified demand fulfilled"}</h3>
      <dl className="dl">
        <dt>Business demand</dt>
        <dd>{opp.businessDemand}</dd>
        <dt>Qualified</dt>
        <dd>{opp.qualified ? "YES" : "NO"}</dd>
        <dt>Provider</dt>
        <dd>{opp.provider}</dd>
        {failed ? (
          <>
            <dt>Number Verification API</dt>
            <dd>{opp.numberVerificationApi}</dd>
            <dt>Fulfilled</dt>
            <dd>NO</dd>
            <dt>Blocking readiness gap</dt>
            <dd>{opp.blockingReadinessGap}</dd>
          </>
        ) : (
          <>
            <dt>Fulfilled</dt>
            <dd>YES</dd>
            <dt>Path</dt>
            <dd>
              <code>{opp.path}</code>
            </dd>
            <dt>Network API consumption</dt>
            <dd>{opp.networkApiConsumption}</dd>
          </>
        )}
      </dl>
      {opp.commercialMessage ? <p className="plus-line">{opp.commercialMessage}</p> : null}
      <div className="grid-2 section">
        <article className="inset">
          <p className="kicker">Enterprise</p>
          <p className="tiny">{opp.enterpriseValue}</p>
        </article>
        <article className="inset">
          <p className="kicker">Operator</p>
          <p className="tiny">{opp.operatorValue}</p>
        </article>
      </div>
    </section>
  );
}

export function NvHonesty({ trace }) {
  const h = trace?.honesty || {};
  return (
    <p className="tiny nv-honesty">
      {h.accessType || "SIMULATED ACCESS CONTEXT"} · {h.operatorReadiness || "CONFIGURED OPERATOR READINESS"} ·{" "}
      {h.operatorResponse || "SIMULATED OPERATOR RESPONSE"}
    </p>
  );
}

export function NvClose({ trace }) {
  const close = trace?.networkOpportunity?.close || {};
  return (
    <section className="nv-close grid-3">
      <article className="panel">
        <h3>For the application</h3>
        <p>{close.application || "One Intent. No NV1/NV2 integration logic."}</p>
      </article>
      <article className="panel">
        <h3>For the network</h3>
        <p>{close.network || "Operator readiness determines whether demand can be fulfilled."}</p>
      </article>
      <article className="panel ax-lane">
        <h3>NetAware AX</h3>
        <p>
          {close.ax ||
            "connects business demand to the Network API path that can actually serve it."}
        </p>
      </article>
    </section>
  );
}

export function NvFinderStrip({ trace }) {
  const ps = trace?.pathSelection || {};
  const telco = ps.telcoFinder || {};
  const api = ps.apiFinder || {};
  const ready = ps.operatorReadiness || {};
  const ecs = ready.entitlementServer || {};
  return (
    <section className="grid-3 nv-finders">
      <article className="inset">
        <p className="kicker">Telco Finder</p>
        <p>MSISDN</p>
        <div className="pipeline-arrow">↓</div>
        <p>
          <strong>{telco.provider || "Operator"}</strong>
        </p>
        <p className="tiny">Which operator applies? Not Wi-Fi vs cellular.</p>
      </article>
      <article className="inset">
        <p className="kicker">API Finder</p>
        <p>
          Number Verification ·{" "}
          <Pill tone={api.numberVerificationAvailable ? "ok" : "warn"}>
            {api.numberVerificationAvailable ? "AVAILABLE" : "UNAVAILABLE"}
          </Pill>
        </p>
        <p className="tiny">CAMARA API availability. Distinct from NV path support.</p>
      </article>
      <article className={`inset ${ecs.available === "UNAVAILABLE" ? "break-inset" : ""}`}>
        <p className="kicker">Fulfillment</p>
        <p>
          NV path · ECS · <Pill tone={ecs.available === "AVAILABLE" ? "ok" : "warn"}>{ecs.available || "—"}</Pill>
        </p>
        <p className="tiny">Path support and operator prerequisite / ECS readiness. Not a CAMARA ECS API.</p>
      </article>
    </section>
  );
}

export { VARIANTS };
