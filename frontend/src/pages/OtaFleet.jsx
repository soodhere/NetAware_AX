export function OtaVariantBar({ variantId, onChange, disabled }) {
  return (
    <div className="nv-variant-bar">
      <p className="kicker">Simulate later observation</p>
      <p className="tiny">Same Intent. Same campaign. Later runtime context. Application does not choose a different job.</p>
      <div className="nv-variant-row">
        <button type="button" className={variantId === "prepare" ? "on" : ""} disabled={disabled} onClick={() => onChange("prepare")}>
          Step 1 · Prepare cohort
        </button>
        <button type="button" className={variantId === "reassess" ? "on" : ""} disabled={disabled} onClick={() => onChange("reassess")}>
          Step 2 · Reassess deferred
        </button>
      </div>
    </div>
  );
}

function Dots({ count, cap = 48, tone }) {
  const n = Math.max(4, Math.min(cap, Math.round((Number(count) || 0) / 200)));
  return (
    <div className={`ota-dots ${tone || ""}`.trim()} aria-hidden="true">
      {Array.from({ length: n }, (_, i) => (
        <i key={i} />
      ))}
    </div>
  );
}

export function OtaFleetVisual({ trace, lens }) {
  const visual = trace?.otaVisual;
  if (!visual) return null;
  const cohorts = visual.cohorts || {};
  const movement = visual.movement || {};
  const volume = visual.volume || {};
  const moving = visual.wave === "reassess" && movement.added > 0;
  return (
    <section className="ota-fleet" aria-label="Simulated OTA fleet">
      <p className="kicker">{visual.enterprise}</p>
      <h2>{visual.campaign}</h2>
      <p className="lede">{visual.headline}</p>
      <p className="tiny ota-labels">
        {(visual.labels || []).map((label) => (
          <span className="pill muted" key={label}>
            {label}
          </span>
        ))}
      </p>
      <p className="tiny">{visual.adjacentApplication}</p>

      <ol className="ota-funnel">
        {(visual.funnel || []).map((step) => (
          <li key={step.id} className={step.tone || ""}>
            <span className="kicker">{step.owner}</span>
            <strong>{step.count?.toLocaleString?.() ?? step.count}</strong>
            <em>{step.label}</em>
          </li>
        ))}
      </ol>

      <div className="ota-lanes">
        <article className="panel outcome ready">
          <p className="kicker">ROLL OUT NOW</p>
          <strong>{cohorts.rollOutNow?.toLocaleString?.()}</strong>
          <Dots count={cohorts.rollOutNow} tone="ok" />
          {moving ? <p className="tiny ok-text">+{movement.added.toLocaleString()} moved from DEFER</p> : null}
        </article>
        <article className="panel">
          <p className="kicker">DEFER — UNREACHABLE</p>
          <strong>{cohorts.deferUnreachable?.toLocaleString?.()}</strong>
          <Dots count={cohorts.deferUnreachable} tone="warn" />
          {moving && movement.fromUnreachable ? <p className="tiny">−{movement.fromUnreachable.toLocaleString()} now reachable</p> : null}
        </article>
        <article className="panel">
          <p className="kicker">DEFER — ROAMING POLICY</p>
          <strong>{cohorts.deferRoamingPolicy?.toLocaleString?.()}</strong>
          <Dots count={cohorts.deferRoamingPolicy} />
          {moving && movement.fromRoaming ? <p className="tiny">−{movement.fromRoaming.toLocaleString()} now home network</p> : null}
        </article>
        <article className="panel outcome gap">
          <p className="kicker">UNFULFILLED — PROVIDER/API GAP</p>
          <strong>{cohorts.unfulfilledApiGap?.toLocaleString?.()}</strong>
          <Dots count={cohorts.unfulfilledApiGap} tone="warn" />
        </article>
      </div>

      <section className="grid-2 section">
        <article className="panel finder-block">
          <p className="kicker">Telco Finder</p>
          <h3>Group the fleet by provider</h3>
          <ul className="list compact">
            {(visual.providers || []).map((row) => (
              <li key={row.providerId || row.label}>
                <strong>{row.label}</strong>
                <span className="tiny">
                  {" "}
                  · {row.region} · {row.route}
                  {row.via ? ` via ${row.via}` : ""} · {row.campaignDevices?.toLocaleString?.()} campaign / {row.enterpriseEligible?.toLocaleString?.()} eligible
                </span>
              </li>
            ))}
          </ul>
          <p className="tiny">Telco Finder does not evaluate Reachability or Roaming.</p>
        </article>
        <article className="panel finder-block">
          <p className="kicker">API Finder</p>
          <h3>Capability availability by route</h3>
          <ul className="list compact">
            {(visual.apiFinder || []).map((row) => (
              <li key={row.label}>
                <strong>{row.label}</strong>
                <span className="tiny">
                  {" "}
                  · Reachability {row.reachability ? "yes" : "no"} · Roaming {row.roaming ? "yes" : "unavailable"}
                  {row.via ? ` · ${row.route} via ${row.via}` : ` · ${row.route}`}
                </span>
              </li>
            ))}
          </ul>
          <p className="tiny">API Finder is visually separate from Telco Finder.</p>
        </article>
      </section>

      <article className="panel">
        <p className="kicker">Why deferred?</p>
        <ul className="list compact">
          {(visual.deferredReasons || []).map((row) => (
            <li key={row.id}>
              <strong>{row.count?.toLocaleString?.()}</strong> {row.label}
              {lens === "ADVANCED" ? <span className="tiny"> · {row.note}</span> : null}
            </li>
          ))}
        </ul>
        <p className="tiny">{visual.policy?.roaming}</p>
      </article>

      <article className="network-opportunity">
        <p className="kicker">{volume.label}</p>
        <p className="nv-headline">ONE BUSINESS INTENT → THOUSANDS OF QUALIFIED NETWORK API INTERACTIONS</p>
        <p>
          Reachability checks {Number(volume.reachabilityLive || 0).toLocaleString()}
          {volume.reachabilityReused ? ` · reused ${Number(volume.reachabilityReused).toLocaleString()}` : ""} · Roaming checks {Number(volume.roamingLive || 0).toLocaleString()}
        </p>
        <p className="tiny">{volume.note}</p>
      </article>

      {moving ? (
        <p className="banner">DEFERRED → RECHECK → NOW READY → EXPAND COHORT. Firmware is still not installed by NetAware.</p>
      ) : null}

      <div className="ota-close">
        {(visual.close || []).map((line, idx) => (
          <p key={line}>
            <strong>{idx + 1}.</strong> {line}
          </p>
        ))}
        <p className="tiny">Enterprise value · {visual.enterpriseValue}</p>
        <p className="tiny">Network value · {visual.networkValue}</p>
        <p className="nv-headline">{visual.footer}</p>
      </div>
    </section>
  );
}
