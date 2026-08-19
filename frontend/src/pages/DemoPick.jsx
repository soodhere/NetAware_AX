import { useEffect, useMemo, useState } from "react";
import { api, href } from "../api.js";
import { HeroDemoCard } from "../components/AxLoop.jsx";

const MATURITY_TONE = { LIVE: "ok", GUIDED: "warn", EXPLORE: "muted" };

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function ScenarioCard({ row }) {
  const entId = row.enterpriseId || row.enterprise?.id;
  const ucId = row.useCaseId || row.useCase?.id;
  const to = href(`/demo/${entId}/${ucId}`);
  const coverage = row.coverageHref || `/coverage/enterprise/${entId}/use-case/${ucId}`;
  return (
    <article className="portfolio-card">
      <a href={to} className="portfolio-card-main">
        <div className="chips">
          <Pill tone={MATURITY_TONE[row.scenarioMaturity]}>{row.scenarioMaturity}</Pill>
          <Pill>{row.scenarioComplexity}</Pill>
        </div>
        <p className="kicker">
          {row.enterprise?.label} · {row.industryLabel || row.industry}
        </p>
        <h3>{row.application?.label}</h3>
        <p className="tiny">{row.useCase?.label}</p>
        <p>{row.businessProblem}</p>
        <div className="portfolio-gap">
          <span>Decision gap</span>
          <strong>{row.decisionGap}</strong>
        </div>
        <p className="tiny">Network adds · {row.networkContribution}</p>
      </a>
      <a className="coverage-link" href={href(coverage)}>
        See Fulfillment Coverage
      </a>
      <a className="coverage-link" href={href(row.demandHref || `/demand/enterprise/${entId}`)}>
        See Demand
      </a>
    </article>
  );
}

export default function DemoPick({ enterpriseId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [industry, setIndustry] = useState("");
  const [motion, setMotion] = useState("");
  const [view, setView] = useState("portfolio");

  useEffect(() => {
    const path = enterpriseId ? `/demo/${enterpriseId}` : "/demo";
    api(path)
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, [enterpriseId]);

  const portfolio = data?.portfolio || {};
  const scenarios = portfolio.scenarios || [];
  const filtered = useMemo(() => {
    return scenarios.filter((row) => {
      if (industry && row.industry !== industry) return false;
      if (motion && !(row.commercialMotion || []).includes(motion)) return false;
      return true;
    });
  }, [scenarios, industry, motion]);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  if (!enterpriseId) {
    const reverse = portfolio.whereCouldISellThis || {};
    const reverseKeys = [
      ["device_reachability", "Device Reachability"],
      ["sim_continuity", "SIM Swap / continuity"],
      ["quality_on_demand", "Quality on Demand"],
    ];
    return (
      <div>
        <p className="kicker">Sales portfolio</p>
        <h1>
          <span>What can I show?</span>
        </h1>
        <p className="lede">
          Application first. Network APIs close a Decision Gap the enterprise cannot see itself.
        </p>

        <div className="tabs">
          {[
            ["portfolio", "Portfolio"],
            ["industry", "By industry"],
            ["motion", "By motion"],
            ["capability", "Where could I sell this?"],
          ].map(([id, label]) => (
            <button key={id} className={view === id ? "on" : ""} type="button" onClick={() => setView(id)}>
              {label}
            </button>
          ))}
        </div>

        {view === "portfolio" ? (
          <>
            <section className="leverage-strip section">
              <article>
                <span>{portfolio.leverage?.catalogFamilies || 13} API families</span>
                <strong>→ many intents</strong>
              </article>
              <article>
                <span>{portfolio.count} use cases</span>
                <strong>→ multiple industries</strong>
              </article>
              <p className="tiny">{portfolio.leverage?.headline}</p>
            </section>
            <p>
              <a className="coverage-link" href={href("/map")}>
                See Use Case / API map
              </a>
            </p>
            <div className="filter-row">
              <label>
                Industry
                <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
                  <option value="">All</option>
                  {(portfolio.industries || []).map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Business motion
                <select value={motion} onChange={(e) => setMotion(e.target.value)}>
                  <option value="">All</option>
                  {(portfolio.motions || []).map((row) => (
                    <option key={row.id} value={row.id}>
                      {row.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <section className="portfolio-grid section">
              {filtered.map((row) => (
                <ScenarioCard key={`${row.enterpriseId}-${row.useCaseId}`} row={row} />
              ))}
            </section>
            <section className="section">
              <p className="kicker">Live heroes</p>
              <p className="tiny">Recommended live order still starts with Number Verification / passwordless mobile sign-in.</p>
              <div className="grid-2 hero-grid">
                {(data.featured || []).map((row) => (
                  <HeroDemoCard key={row.storyId || row.heroUseCaseId || row.enterprise?.id} row={row} hrefFn={href} />
                ))}
              </div>
            </section>
          </>
        ) : null}

        {view === "industry" ? (
          <section className="section">
            {(portfolio.industries || []).map((ind) => {
              const rows = portfolio.byIndustry?.[ind.id] || [];
              if (!rows.length) return null;
              return (
                <article key={ind.id} className="panel industry-block">
                  <h2>{ind.label}</h2>
                  <ol className="industry-chain">
                    {rows.map((row) => (
                      <li key={row.useCaseId}>
                        <a href={href(`/demo/${row.enterpriseId}/${row.useCaseId}`)}>
                          <strong>{row.application?.label}</strong>
                          <span>{row.useCase?.label}</span>
                          <em>{row.decisionGap}</em>
                          <small>{row.networkContribution}</small>
                          <Pill tone={MATURITY_TONE[row.scenarioMaturity]}>{row.scenarioMaturity}</Pill>
                        </a>
                      </li>
                    ))}
                  </ol>
                </article>
              );
            })}
          </section>
        ) : null}

        {view === "motion" ? (
          <section className="section">
            {(portfolio.motions || []).map((m) => {
              const rows = portfolio.byMotion?.[m.id] || [];
              if (!rows.length) return null;
              return (
                <article key={m.id} className="panel">
                  <h2>{m.label}</h2>
                  <div className="chips">
                    {rows.map((row) => (
                      <a key={row.useCaseId} className="chip" href={href(`/demo/${row.enterpriseId}/${row.useCaseId}`)}>
                        {row.enterprise?.label} · {row.application?.label}
                      </a>
                    ))}
                  </div>
                </article>
              );
            })}
          </section>
        ) : null}

        {view === "capability" ? (
          <section className="section">
            <p className="tiny">A small practical catalog. Not hundreds of APIs.</p>
            {reverseKeys.map(([id, label]) => (
              <article key={id} className="panel" style={{ marginBottom: 12 }}>
                <h3>{label}</h3>
                <ul className="list compact">
                  {(reverse[id] || []).map((hit) => (
                    <li key={`${hit.enterprise}-${hit.useCaseId}`}>
                      <a href={href(`/demo/${scenarios.find((s) => s.useCaseId === hit.useCaseId)?.enterpriseId}/${hit.useCaseId}`)}>
                        {hit.enterprise} · {hit.application}
                      </a>
                      <Pill tone={MATURITY_TONE[hit.maturity]}>{hit.maturity}</Pill>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </section>
        ) : null}
      </div>
    );
  }

  const ent = data.enterprise || {};
  const heroId = data.heroUseCaseId;
  const hero = (data.useCases || []).find((uc) => uc.id === heroId) || (data.useCases || [])[0];
  const extra = data.portfolio || [];
  return (
    <div>
      <p className="kicker">{data.domainAudienceLabel}</p>
      <h1>
        <span>{ent.label}</span>
      </h1>
      {hero ? (
        <section className="section">
          <a className="hero-demo-card single" href={href(`/demo/${ent.id}/${hero.id}`)}>
            <p className="kicker">Hero scenario</p>
            <h2>{hero.label}</h2>
            <p className="tiny">{hero.networkComplement}</p>
          </a>
        </section>
      ) : null}
      {(data.useCases || []).filter((uc) => uc.id !== heroId).length || extra.length ? (
        <section className="section">
          <h3>Configured use cases</h3>
          <div className="chips">
            {(data.useCases || [])
              .filter((uc) => uc.id !== heroId)
              .map((uc) => (
                <a key={uc.id} className="chip" href={href(`/demo/${ent.id}/${uc.id}`)}>
                  {uc.label}
                </a>
              ))}
            {Array.isArray(extra)
              ? extra
                  .filter((row) => row.useCaseId !== heroId)
                  .map((row) => (
                    <a key={row.useCaseId} className="chip" href={href(`/demo/${ent.id}/${row.useCaseId}`)}>
                      {row.useCase?.label || row.useCaseId}
                    </a>
                  ))
              : null}
          </div>
        </section>
      ) : null}
    </div>
  );
}
