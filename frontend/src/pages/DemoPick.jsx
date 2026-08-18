import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import { HeroDemoCard } from "../components/AxLoop.jsx";

export default function DemoPick({ enterpriseId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const path = enterpriseId ? `/demo/${enterpriseId}` : "/demo";
    api(path)
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, [enterpriseId]);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  if (!enterpriseId) {
    return (
      <div>
        <p className="kicker">Start Demo</p>
        <h1>
          <span>Choose a scenario</span>
        </h1>
        <p className="lede">
          Each scenario keeps your enterprise systems. NetAware adds complementary Network APIs under governance.
        </p>
        <section className="grid-2 section hero-grid">
          {(data.featured || []).map((row) => (
            <HeroDemoCard key={row.enterprise?.id || row.id} row={row} hrefFn={href} />
          ))}
        </section>
        <p className="tiny">Recommended order: High Flight → Rocket Bank → Acme → CityCare.</p>
      </div>
    );
  }

  const ent = data.enterprise || {};
  const heroId = data.heroUseCaseId;
  const hero = (data.useCases || []).find((uc) => uc.id === heroId) || (data.useCases || [])[0];
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
      {(data.useCases || []).filter((uc) => uc.id !== heroId).length ? (
        <section className="section">
          <h3>Other configured use cases</h3>
          <div className="chips">
            {(data.useCases || [])
              .filter((uc) => uc.id !== heroId)
              .map((uc) => (
                <a key={uc.id} className="chip" href={href(`/demo/${ent.id}/${uc.id}`)}>
                  {uc.label}
                </a>
              ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
