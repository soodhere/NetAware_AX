import { useEffect, useMemo, useState } from "react";
import { api, href } from "../api.js";
import { SupplyGapGraph } from "../visuals/VisualKit.jsx";

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function tone(state) {
  const v = String(state || "");
  if (v === "FULFILLED") return "ok";
  if (v === "PARTIALLY_FULFILLED" || v === "QUALIFIED") return "warn";
  if (v === "UNFULFILLED") return "bad";
  return "muted";
}

function parseDemand(parts) {
  const [a, b] = parts || [];
  if (a === "enterprise" || a === "enterprises") return { kind: "demand", enterpriseId: b };
  if (a === "provider" || a === "providers") return { kind: "supply", providerId: b };
  if (a === "capability") return { kind: "capability", capabilityId: b };
  if (a === "capabilities") return { kind: "capability", capabilityId: b };
  if (a === "intent") return { kind: "intent", intentId: b };
  if (a === "intents") return { kind: "intent", intentId: b };
  if (a === "industry") return { kind: "industry", industryId: b };
  if (a === "industries") return { kind: "industry", industryId: b };
  if (a === "region") return { kind: "region", regionId: b };
  if (a === "regions") return { kind: "region", regionId: b };
  if (a === "motion") return { kind: "motion", motionId: b };
  if (a === "motions") return { kind: "motion", motionId: b };
  if (a === "gap" || a === "gaps") return { kind: "gap", gap: b };
  if (a === "family") return { kind: "family", familyId: b };
  return { kind: "home" };
}

export default function Demand({ parts }) {
  const sel = parseDemand(parts);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [view, setView] = useState(
    sel.kind === "supply" ? "supply" : sel.kind === "capability" || sel.kind === "family" ? "capability" : "demand"
  );
  const [technical, setTechnical] = useState(false);
  const [picked, setPicked] = useState("");
  const [enterpriseId, setEnterpriseId] = useState(sel.enterpriseId || "");
  const [providerId, setProviderId] = useState(sel.providerId || "");
  const [industryId, setIndustryId] = useState(sel.industryId || "");
  const [regionId, setRegionId] = useState(sel.regionId || "");
  const [motionId, setMotionId] = useState(sel.motionId || "");

  useEffect(() => {
    api("/demand")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  const records = data?.records || [];
  const filtered = useMemo(() => {
    return records.filter((row) => {
      if (sel.capabilityId) return row.capability === sel.capabilityId;
      if (sel.intentId) return row.intentId === sel.intentId;
      if (sel.gap) return row.blockingGap === sel.gap;
      if (sel.familyId) return row.familyId === sel.familyId;
      if (view === "demand" && enterpriseId) return row.enterpriseId === enterpriseId;
      if (view === "demand" && industryId) return row.industry === industryId;
      if (view === "demand" && regionId) return row.region === regionId;
      if (view === "demand" && motionId) return (row.commercialMotion || []).includes(motionId);
      if (view === "supply" && providerId) return row.provider === providerId || row.routeProvider === providerId;
      if (view === "capability" && sel.capabilityId) return row.capability === sel.capabilityId;
      return true;
    });
  }, [records, sel, view, enterpriseId, industryId, regionId, motionId, providerId]);

  const selected = records.find((r) => r.demandId === picked) || filtered[0] || null;
  const summary = data?.summary || {};
  const enterprises = [...new Map(records.map((r) => [r.enterpriseId, r])).values()];

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  return (
    <div className="demand-page">
      <p className="kicker">Demand Map</p>
      <h1>
        <span>Where is network API demand?</span>
      </h1>
      <p className="lede">
        Qualified demand is a configured business Intent that needs a network capability. It is not revenue, TAM, or an
        API call.
      </p>
      <p className="tiny honesty">{data.honesty}</p>

      <ol className="cov-chain">
        <li>INDUSTRY</li>
        <li>ENTERPRISE</li>
        <li>APPLICATION</li>
        <li>INTENT</li>
        <li>CAPABILITY DEMAND</li>
        <li>REGION</li>
        <li>PROVIDER / ROUTE</li>
        <li>FULFILLED / GAP</li>
      </ol>

      <section className="leverage-strip section">
        <article>
          <span>{summary.visibleUseCases}</span>
          <strong>visible use cases</strong>
        </article>
        <article>
          <span>{summary.qualifiedCapabilityDemands}</span>
          <strong>qualified capability demands</strong>
        </article>
        <article>
          <span>{summary.fulfilledDemands}</span>
          <strong>fulfilled</strong>
        </article>
        <article>
          <span>{summary.partialDemands}</span>
          <strong>partial</strong>
        </article>
        <article>
          <span>{summary.unfulfilledDemands}</span>
          <strong>unfulfilled</strong>
        </article>
      </section>

      <SupplyGapGraph gaps={data.enablement} />

      <section className="panel section why-na">
        <h3>Why NetAware?</h3>
        <div className="grid-2">
          <div>
            <p className="kicker">Without NetAware</p>
            <ul className="list compact">
              {(data.whyNetAware?.without || []).map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="kicker">With NetAware AX</p>
            <ol className="cov-funnel why-flow">
              {(data.whyNetAware?.with || []).map((line) => (
                <li key={line}>
                  <span>{line}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
        <p className="lede">{data.whyNetAware?.close}</p>
      </section>

      <ol className="demo-story">
        {(data.demoStory || []).map((step) => (
          <li key={step.step}>
            <strong>
              {step.step} · {step.label}
            </strong>
            <span>{step.line}</span>
          </li>
        ))}
      </ol>

      <div className="tabs">
        {[
          ["demand", "Enterprise / demand"],
          ["supply", "Operator / aggregator"],
          ["capability", "Capability leverage"],
          ["gaps", "Supply-gap impact"],
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
          <div className="filter-row">
            <label>
              Industry
              <select value={industryId} onChange={(e) => setIndustryId(e.target.value)}>
                <option value="">All</option>
                {(data.industries || []).map((ind) => (
                  <option key={ind.id} value={ind.id}>
                    {ind.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Motion
              <select value={motionId} onChange={(e) => setMotionId(e.target.value)}>
                <option value="">All</option>
                {(data.motions || []).map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Region
              <select value={regionId} onChange={(e) => setRegionId(e.target.value)}>
                <option value="">All · configured demo coverage</option>
                {(data.regions || []).map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Enterprise
              <select value={enterpriseId} onChange={(e) => setEnterpriseId(e.target.value)}>
                <option value="">All</option>
                {enterprises.map((row) => (
                  <option key={row.enterpriseId} value={row.enterpriseId}>
                    {row.enterpriseLabel}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="cov-visual">
            {filtered.map((row) => (
              <button
                key={row.demandId}
                type="button"
                className={`cov-lane ${picked === row.demandId ? "on" : ""}`}
                onClick={() => setPicked(row.demandId)}
              >
                <p className="kicker">
                  {row.industryLabel} · {row.enterpriseLabel}
                </p>
                <strong>
                  {row.applicationLabel} → {row.intentLabel}
                </strong>
                <p className="tiny">{row.decisionGap}</p>
                <div className="cov-flow">
                  <span>{row.capabilityLabel}</span>
                  <span>{row.regionLabel}</span>
                  <span>{row.providerLabel || "—"}</span>
                  <Pill tone={tone(row.demandState)}>{row.demandState}</Pill>
                  <Pill tone={row.maturity === "LIVE" ? "ok" : row.maturity === "GUIDED" ? "warn" : "muted"}>{row.maturity}</Pill>
                </div>
              </button>
            ))}
          </div>
        </>
      ) : null}

      {view === "supply" ? (
        <section className="grid-2 section">
          <article className="panel">
            <h3>What could this network enable?</h3>
            {(data.operators || []).map((p) => (
              <button
                key={p.id}
                type="button"
                className={`cov-provider ${providerId === p.id ? "on" : ""}`}
                onClick={() => setProviderId(p.id)}
              >
                <strong>{p.label}</strong>
                <span className="tiny">
                  {p.providerType}
                  {p.doesNotOwnApis ? " · routed / normalized through — does not own operator APIs" : ""}
                </span>
              </button>
            ))}
          </article>
          <article className="panel">
            {(() => {
              const p = (data.operators || []).find((row) => row.id === providerId) || data.operators?.[0];
              if (!p) return null;
              return (
                <>
                  <p className="kicker">{p.providerType}</p>
                  <h3>{p.label}</h3>
                  <p className="tiny">{p.note}</p>
                  {p.aggregatorNote ? <p className="tiny">{p.aggregatorNote}</p> : null}
                  <p className="kicker">Currently ready</p>
                  <p className="tiny">{(p.currentlyReady || []).join(" · ") || "—"}</p>
                  <p className="kicker">Gaps</p>
                  <ul className="list compact">
                    {(p.gaps || []).map((g) => (
                      <li key={`${g.gap}-${g.intentId}`}>
                        {g.gap} · {g.capability} · {g.intentId}
                      </li>
                    ))}
                  </ul>
                  <p className="tiny">
                    Fulfills {p.fulfillsIntents} configured Intents · {p.fulfillsApplications} applications ·{" "}
                    {p.fulfillsIndustries} industries
                  </p>
                </>
              );
            })()}
          </article>
        </section>
      ) : null}

      {view === "capability" ? (
        <section className="section">
          <p className="tiny">One capability → many business outcomes. No dollar value.</p>
          {!sel.capabilityId ? (
            <div className="cov-visual" style={{ marginBottom: 16 }}>
              {(data.familyLeverage || [])
                .filter((fam) => (fam.intents || []).length)
                .map((fam) => (
                  <article key={fam.id} className="cov-lane">
                    <p className="kicker">API family</p>
                    <strong>{fam.label}</strong>
                    <p className="tiny">
                      {(fam.intents || []).length} intents · {(fam.applications || []).length} applications ·{" "}
                      {(fam.industries || []).length} industries
                    </p>
                    <p className="tiny">{(fam.industries || []).join(" · ")}</p>
                    <a href={href(`/demand/family/${fam.id}`)}>See Demand</a>
                  </article>
                ))}
            </div>
          ) : null}
          {(data.capabilityLeverage || [])
            .filter((cap) => !sel.capabilityId || cap.id === sel.capabilityId)
            .map((cap) => (
              <article key={cap.id} className="panel" style={{ marginBottom: 12 }}>
                <h3>{cap.label}</h3>
                <p className="tiny">
                  {cap.industriesReached} industries · {cap.applicationsReached} applications · {cap.intentsReached}{" "}
                  intents
                </p>
                <ul className="list compact">
                  {(cap.intents || []).map((hit) => (
                    <li key={`${cap.id}-${hit.demandId || hit.id}`}>
                      <button type="button" onClick={() => hit.demandId && setPicked(hit.demandId)}>
                        {hit.enterpriseLabel} · {hit.applicationLabel} · {hit.label}
                      </button>
                      <Pill tone={hit.maturity === "LIVE" ? "ok" : hit.maturity === "GUIDED" ? "warn" : "muted"}>{hit.maturity}</Pill>
                      <Pill tone={tone(hit.demandState)}>{hit.demandState}</Pill>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
        </section>
      ) : null}

      {view === "gaps" ? (
        <section className="section">
          <p className="tiny">What does this gap prevent? Unfulfilled qualified demand — not lost revenue.</p>
          {(data.enablement || []).map((gap) => (
            <article key={gap.id} className="panel" style={{ marginBottom: 12 }}>
              <p className="kicker">{gap.kind}</p>
              <h3>{gap.label}</h3>
              <p>
                {gap.providerLabel} → {gap.prevents}
              </p>
              <p className="tiny">
                Affected Intent {gap.affectedIntent} · {gap.affectedApplication} · {gap.affectedMotion}
              </p>
              {gap.affectedUnitsLabel ? <p className="tiny">{gap.affectedUnitsLabel}</p> : null}
              <p>
                If enabled: {gap.ifEnabled?.from} → {gap.ifEnabled?.to}. {gap.ifEnabled?.note}
              </p>
            </article>
          ))}
        </section>
      ) : null}

      <section className="section grid-2">
        <article className="panel cov-why">
          {selected ? (
            <>
              <div className="chips">
                <Pill tone={tone(selected.demandState)}>{selected.demandState}</Pill>
                <Pill>{selected.requirementType}</Pill>
                {selected.route ? <Pill>{selected.route}</Pill> : null}
              </div>
              <p className="kicker">
                {selected.enterpriseLabel} · {selected.applicationLabel}
              </p>
              <h3>{selected.capabilityLabel}</h3>
              <p>{selected.decisionGap}</p>
              <p className="tiny">{selected.invocationNote}</p>
              {selected.fulfillmentVsOutcome ? (
                <div className="banner">
                  Negative network evidence can still be successful API fulfillment.
                </div>
              ) : null}
              {selected.contextualDemand ? (
                <div className="banner">
                  <p className="kicker">Contextual demand</p>
                  <p>
                    Initially {selected.contextualDemand.initially}. {selected.contextualDemand.trigger} →{" "}
                    {selected.contextualDemand.becomes}. {selected.contextualDemand.note}
                  </p>
                </div>
              ) : null}
              {selected.affectedUnitsLabel ? <p>{selected.affectedUnitsLabel}</p> : null}
              <p>
                <a href={href(selected.coverageHref || "/coverage")}>See Fulfillment</a>
                {selected.portfolioHref ? (
                  <>
                    {" · "}
                    <a href={href(selected.portfolioHref)}>Open business story</a>
                  </>
                ) : null}
              </p>
              {technical ? (
                <dl className="dl">
                  <dt>Intent</dt>
                  <dd>{selected.intentId}</dd>
                  <dt>Purpose of coverage</dt>
                  <dd>C13 answers can it be fulfilled. C14 asks what configured demand that coverage serves.</dd>
                  <dt>Blocking gap</dt>
                  <dd>{selected.blockingGap || "—"}</dd>
                  <dt>operationId</dt>
                  <dd>
                    <code>{selected.operationId || "—"}</code>
                  </dd>
                  <dt>Source / provenance</dt>
                  <dd>
                    {selected.source}
                    {(selected.provenance || []).slice(0, 4).map((row) => (
                      <div key={row.fact} className="tiny">
                        {row.source} · {row.fact}
                      </div>
                    ))}
                  </dd>
                </dl>
              ) : (
                <p className="tiny">Technical View adds Intent Profile, operationId, route, and provenance.</p>
              )}
            </>
          ) : (
            <p className="tiny">Select a demand node to see why.</p>
          )}
        </article>
        <article className="panel">
          <h3>Demand is not invocation</h3>
          <ul className="list compact">
            {(data.notInvocationReasons || []).map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          <p>
            <a href={href("/coverage")}>See Fulfillment Coverage</a>
            {" · "}
            <a href={href("/demo")}>Sales portfolio</a>
          </p>
        </article>
      </section>
    </div>
  );
}
