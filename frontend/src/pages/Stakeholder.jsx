import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import { startHref, writeStakeholder } from "../stakeholder.js";

function Chain({ items, className }) {
  return (
    <ol className={className || "cov-chain"}>
      {(items || []).map((step) => (
        <li key={typeof step === "string" ? step : step.id}>{typeof step === "string" ? step : step.label}</li>
      ))}
    </ol>
  );
}

function Story({ story }) {
  if (!story) return null;
  return (
    <article className="panel story-card">
      <p className="kicker">Recommended story</p>
      <h3>{story.title}</h3>
      <ol className="story-beats">
        {(story.beats || []).map((row) => (
          <li key={row.beat}>
            <strong>{row.beat}</strong>
            <span>{row.line}</span>
          </li>
        ))}
      </ol>
      {(story.optional || []).length ? (
        <p className="tiny">
          Optional drill-downs
          {(story.optional || []).map((row) => (
            <span key={row.href}>
              {" · "}
              <a href={href(row.href)}>{row.label}</a>
            </span>
          ))}
        </p>
      ) : null}
    </article>
  );
}

export function Welcome() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/start")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  const choose = (id) => writeStakeholder(id);

  return (
    <div className="welcome-page">
      <p className="kicker">{data.fromLine}</p>
      <h1>
        <span>Welcome to NetAware AX</span>
      </h1>
      <p className="lede statement">{data.productStatement}</p>
      <p className="tiny honesty">{data.honesty}</p>

      <p className="kicker" style={{ marginTop: 28 }}>
        {data.question}
      </p>
      <div className="stake-grid">
        {["enterprise", "operator", "aggregator"].map((id) => {
          const a = data.audiences?.[id] || {};
          return (
            <a key={id} className="stake-card" href={href(startHref(id))} onClick={() => choose(id)}>
              <strong>{a.label}</strong>
              <span>{a.blurb}</span>
            </a>
          );
        })}
      </div>
      <p className="hero-actions">
        <a href={href("/home")} onClick={() => choose("explore")}>
          <button type="button">Explore the product</button>
        </a>
      </p>

      <section className="panel section why-na">
        <h3>How NetAware AX fits together</h3>
        <Chain items={data.productMap} />
        <p className="tiny">
          {data.productMapSides?.explorer} {data.productMapSides?.demand}
        </p>
      </section>

      <section className="grid-2 section">
        <article className="panel">
          <h3>DX → AX</h3>
          <p>
            <strong>DX.</strong> {data.dxAx?.dx}
          </p>
          <p>
            <strong>AX.</strong> {data.dxAx?.ax}
          </p>
          <p className="tiny">{data.dxAx?.complement}</p>
          <p className="tiny">{data.dxAx?.consumers}</p>
        </article>
        <article className="panel">
          <h3>Agentic Experience</h3>
          <Chain items={data.agentic} />
        </article>
      </section>
    </div>
  );
}

export default function Start({ audience }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/start")
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  const a = data.audiences?.[audience] || data.audiences?.enterprise;
  const stories = (data.stories || []).filter((s) => s.audience === audience);
  const recommended = stories.find((s) => s.core) || stories[0];
  const three = data.threePerspectives || {};
  const why = data.why || {};

  return (
    <div className="start-page">
      <p className="kicker">{a.label} perspective</p>
      <h1>
        <span>{a.headline}</span>
      </h1>
      <p className="lede">{a.blurb}</p>
      <p className="tiny">Presentation context only. Same product, same data, same Intents. Not a tenant login.</p>

      <div className="hero-actions">
        <a href={href(`/meet/${audience}/exec`)}>
          <button className="primary" type="button">
            Start meeting
          </button>
        </a>
        <a href={href(a.recommendedHref)}>
          <button type="button">{a.cta}</button>
        </a>
        <a href={href(a.exploreMoreHref || "/demo")}>
          <button type="button">Explore more</button>
        </a>
      </div>
      <div className="chips" style={{ marginBottom: 16 }}>
        <a className="chip" href={href(`/meet/${audience}/exec`)}>
          3-minute executive
        </a>
        <a className="chip" href={href(`/meet/${audience}/sales`)}>
          7-minute sales
        </a>
        <a className="chip" href={href(`/meet/${audience}/tech`)}>
          Technical deep dive
        </a>
      </div>

      {audience === "enterprise" ? (
        <section className="section stake-grid">
          {(a.cards || []).map((card) => (
            <a key={card.kicker} className="stake-card" href={href(card.href)}>
              <strong>{card.kicker}</strong>
              <span>{card.question}</span>
              <em>See how NetAware resolves this</em>
            </a>
          ))}
        </section>
      ) : null}

      {audience === "operator" ? (
        <>
          <section className="section grid-3">
            {(a.questions || []).map((q) => (
              <article key={q} className="panel">
                <h3>{q}</h3>
              </article>
            ))}
          </section>
          <div className="stake-grid">
            {(a.tiles || []).map((tile) => (
              <a key={tile.label} className="stake-card" href={href(tile.href)}>
                <strong>{tile.label}</strong>
              </a>
            ))}
          </div>
        </>
      ) : null}

      {audience === "aggregator" ? (
        <section className="panel section">
          <p className="kicker">{a.wording}</p>
          <Chain
            items={["REGIONS", "NETWORK PROVIDERS", "CAPABILITIES", "ROUTES", "ENTERPRISE INTENTS ENABLED"]}
          />
          <p className="tiny">Aggregator A does not own the underlying operator APIs.</p>
          <p>
            Example: Aggregator A → Germany → Network Provider B → Device Reachability → aggregated route → configured
            applications including Northstar Claims.
          </p>
        </section>
      ) : null}

      <section className="section">
        <p className="kicker">Start recommended story</p>
        <p>
          <a href={href(a.recommendedHref)}>{a.recommendedLabel}</a>
          {" · "}
          <a href={href("/demo")}>Explore more use cases</a>
        </p>
        <Story story={recommended} />
        {stories.filter((s) => s !== recommended).length ? (
          <p className="tiny">
            Other core stories
            {stories
              .filter((s) => s !== recommended)
              .map((s) => (
                <span key={s.title}>
                  {" · "}
                  {s.title}
                </span>
              ))}
          </p>
        ) : null}
      </section>

      <section className="panel section">
        <h3>Same problem, three perspectives</h3>
        <p>{three.need}</p>
        <div className="grid-2">
          <p>
            <strong>Enterprise.</strong> {three.enterprise}
          </p>
          <p>
            <strong>NetAware.</strong> {three.netaware}
          </p>
          <p>
            <strong>Operator.</strong> {three.operator}
          </p>
          <p>
            <strong>Aggregator.</strong> {three.aggregator}
          </p>
        </div>
        <p className="lede">{three.close}</p>
      </section>

      <section className="panel section">
        <h3>Capability discovery</h3>
        <Chain items={data.discovery} />
        <p className="tiny">Business View summarizes this. Technical View shows every field. Same engine.</p>
      </section>

      <section className="panel section why-na">
        <h3>Why NetAware?</h3>
        <p className="lede">{why[audience] || why.close}</p>
        <Chain items={why.shared} className="cov-funnel why-flow" />
        <p className="lede">{why.close}</p>
      </section>

      <p className="tiny">
        Business View uses human purpose. Technical View can show DPV and TMF931-aligned onboarding context where the
        existing mapping supports it. Not a full TMF931 compliance claim. Same trace. Lens switch does not rerun.
      </p>

      <section className="section">
        <h3>Shared Explorer</h3>
        <div className="hero-actions">
          {(a.explorer || []).map((link) => (
            <a key={link.href + link.label} href={href(link.href)}>
              <button type="button">{link.label}</button>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
