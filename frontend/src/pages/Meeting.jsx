import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import { readCuesHidden, writeCuesHidden, writeMeetDepth } from "../meeting.js";
import { writeStakeholder } from "../stakeholder.js";
import {
  AgenticLoopVisual,
  AxBrain,
  ConfigVsRuntime,
  DiscoveryFunnel,
  DxAxSplit,
  FlywheelClose,
  OperatorLadder,
  TopologyVisual,
} from "../visuals/VisualKit.jsx";

function Flow({ items }) {
  return (
    <ol className="cov-chain">
      {(items || []).map((row) => (
        <li key={row}>{row}</li>
      ))}
    </ol>
  );
}

export default function Meeting({ parts }) {
  const audience = ["enterprise", "operator", "aggregator"].includes(parts?.[0]) ? parts[0] : "enterprise";
  const depth = ["exec", "sales", "tech"].includes(parts?.[1]) ? parts[1] : "exec";
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [cuesHidden, setCuesHidden] = useState(readCuesHidden);
  const [coverage, setCoverage] = useState(null);

  useEffect(() => {
    writeStakeholder(audience);
    writeMeetDepth(depth);
  }, [audience, depth]);

  useEffect(() => {
    api("/meet")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
    api("/coverage")
      .then(setCoverage)
      .catch(() => setCoverage(null));
  }, []);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  const depths = data.depths || {};
  const path = ((data.paths || {})[audience] || {})[depth] || {};
  const close = data.closeVisual || {};
  const recs = data.recommender || [];
  const discovery = data.discoveryHero || {};
  const dx = data.dx || {};
  const agentic = data.agentic || {};

  return (
    <div className="meet-page">
      <p className="kicker">Meeting Mode · {audience}</p>
      <h1>
        <span>{(depths[depth] || {}).label || "3-MINUTE EXECUTIVE"}</span>
      </h1>
      <p className="lede statement">{data.productStatement}</p>
      <p className="tiny honesty">{data.honesty}</p>

      <div className="tabs">
        {["enterprise", "operator", "aggregator"].map((id) => (
          <a key={id} href={href(`/meet/${id}/${depth}`)}>
            <button className={audience === id ? "on" : ""} type="button">
              {id}
            </button>
          </a>
        ))}
        {["exec", "sales", "tech"].map((id) => (
          <a key={id} href={href(`/meet/${audience}/${id}`)}>
            <button className={depth === id ? "on" : ""} type="button">
              {(depths[id] || {}).label}
            </button>
          </a>
        ))}
      </div>
      <p className="tiny">{(depths[depth] || {}).note}</p>

      <p className="lede">{path.opening}</p>
      {path.beats ? <Flow items={path.beats} /> : null}

      {audience === "enterprise" && depth === "exec" ? (
        <DxAxSplit dxAx={dx} />
      ) : null}
      {audience === "enterprise" && depth === "sales" ? (
        <>
          <AxBrain />
          <DiscoveryFunnel summary={discovery} catalogFamilies={13} />
        </>
      ) : null}
      {audience === "operator" ? <OperatorLadder records={coverage?.records} /> : null}
      {audience === "aggregator" ? (
        <TopologyVisual
          topology={{
            question: "How does this Intent reach network supply?",
            regions: ["Canada", "Germany", "Singapore"],
            hybrid: "One Intent can use different routes by region/provider.",
            note: "Aggregator A does not own operator APIs. Routed through / normalized through / available via.",
            examples: (coverage?.records || [])
              .filter((r) => ["CA", "DE", "SG"].includes(r.region) && ["DIRECT", "AGGREGATED"].includes(r.route))
              .map((r) => ({
                region: r.region,
                regionLabel: r.regionLabel,
                provider: r.providerLabel,
                via: r.route === "AGGREGATED" ? r.routeProviderLabel : null,
                route: r.route,
                language: r.route === "AGGREGATED" ? "ROUTED THROUGH" : "DIRECT",
                status: r.fulfillmentStatus,
              })),
          }}
        />
      ) : null}
      {depth === "tech" ? (
        <>
          <ConfigVsRuntime
            data={
              data.configuredVsRuntime || {
                configured: ["ENTERPRISE", "APPLICATION", "AGENT", "ALLOWED INTENTS", "PURPOSE", "POLICY", "AGREEMENT / DPA", "CONSENT", "SUBSCRIPTION", "ENTITLEMENT", "REGION", "AUTONOMY"],
                runtime: ["SUBJECT", "BUSINESS CONTEXT", "ACCESS CONTEXT", "SERVING NETWORK", "AVAILABLE NETWORK APIs", "OPERATOR READINESS", "PROVIDER / ROUTE", "EXISTING EVIDENCE", "CURRENT OBJECTIVE STATE"],
              }
            }
            technical
          />
          <AgenticLoopVisual agentic={agentic} />
        </>
      ) : null}

      <ol className="meet-steps">
        {(path.steps || []).map((step, idx) => (
          <li key={`${step.href}-${idx}`}>
            <span className="kicker">
              {idx + 1} · {step.stage}
            </span>
            <a href={href(step.href)}>{step.label}</a>
          </li>
        ))}
      </ol>
      <p className="lede">{path.close}</p>

      <section className="section">
        <p className="kicker">What should I show?</p>
        <div className="stake-grid">
          {recs.map((row) => (
            <a key={row.id} className="stake-card" href={href(row.href)}>
              <strong>{row.audience}</strong>
              <span>{row.show}</span>
              {row.optional ? <em>Optional · {row.optional}</em> : null}
            </a>
          ))}
        </div>
      </section>

      {depth === "tech" ? (
        <section className="panel section">
          <h3>How NetAware knows what to do</h3>
          <p className="tiny">Capability discovery</p>
          <Flow items={discovery.widen} />
          <Flow items={discovery.narrow} />
          <Flow items={discovery.runtime} />
          <Flow items={discovery.act} />
        </section>
      ) : (
        <section className="panel section">
          <h3>How NetAware knows what to do</h3>
          <Flow items={["APPLICATION / INTENT", "POTENTIALLY RELEVANT", "GOVERNANCE", "RUNTIME FEASIBILITY", "CALL / REUSE / SKIP / FILTER / UNAVAILABLE"]} />
        </section>
      )}
      <p>
        <a href={href("/map")}>Use Case ↔ API Map</a>
        {" · "}
        <a href={href("/map/matrix")}>Matrix</a>
        {" · "}
        <a href={href("/map/ax")}>Static mapping → AX</a>
      </p>

      <FlywheelClose close={close} />

      {depth !== "exec" ? (
        <section className="grid-2 section">
          <article className="panel">
            <h3>DX → AX</h3>
            <p className="tiny">{dx.note}</p>
            <p>
              <strong>DX.</strong> {(dx.dx || []).join(" → ")}
            </p>
            <p>
              <strong>AX.</strong> {(dx.ax || []).join(" → ")}
            </p>
          </article>
          <article className="panel">
            <h3>Why is this AX?</h3>
            <Flow items={agentic.chain} />
            <p className="tiny">{(agentic.proofs || []).join(" · ")}</p>
            <p className="tiny">{agentic.note}</p>
          </article>
        </section>
      ) : null}

      <p>
        <button
          type="button"
          onClick={() => {
            const next = !cuesHidden;
            setCuesHidden(next);
            writeCuesHidden(next);
          }}
        >
          {cuesHidden ? "Show presenter cues" : "Hide presenter cues"}
        </button>
      </p>
      {cuesHidden ? null : (
        <section className="panel section">
          <h3>Presenter cues</h3>
          {(data.cues || []).map((cue) => (
            <p key={cue.id} className="tiny">
              SAY {cue.say} ASK {cue.ask} POINT OUT {cue.point} CLOSE {cue.close}
            </p>
          ))}
          <h3>If asked</h3>
          {(data.faq || []).map((row) => (
            <p key={row.q}>
              <strong>{row.q}</strong> {row.a}
            </p>
          ))}
        </section>
      )}
    </div>
  );
}
