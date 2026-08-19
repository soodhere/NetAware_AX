import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import { readCuesHidden, writeCuesHidden, writeMeetDepth } from "../meeting.js";
import { writeStakeholder } from "../stakeholder.js";

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

  useEffect(() => {
    writeStakeholder(audience);
    writeMeetDepth(depth);
  }, [audience, depth]);

  useEffect(() => {
    api("/meet")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
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

      <section className="eq section close-market" aria-label="Demand and supply">
        <article className="domain-lane">
          <span>{close.left?.title}</span>
          <strong>{(close.left?.items || []).join(" · ")}</strong>
        </article>
        <i>→</i>
        <article className="ax-lane">
          <span>{close.center?.title}</span>
          <strong>{(close.center?.items || []).join(" · ")}</strong>
        </article>
        <i>→</i>
        <article className="network-lane">
          <span>{close.right?.title}</span>
          <strong>{(close.right?.items || []).join(" · ")}</strong>
        </article>
        <i>=</i>
        <article className="result">
          <span>{close.outcome}</span>
          <strong>{close.line}</strong>
        </article>
      </section>

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
