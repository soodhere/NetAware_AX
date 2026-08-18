export default function AxLoop({ steps, activeIndex = -1, compact = false }) {
  const items = steps || [
    "Understand",
    "Govern",
    "Discover",
    "Plan",
    "Execute",
    "Observe",
    "Replan",
    "Verify",
  ];
  return (
    <ol className={`ax-loop${compact ? " compact" : ""}`}>
      {items.map((label, idx) => (
        <li key={label} className={idx === activeIndex ? "on" : idx < activeIndex ? "done" : ""}>
          {label}
        </li>
      ))}
    </ol>
  );
}

export function HeroDemoCard({ row, hrefFn }) {
  const ent = row.enterprise || {};
  const hero = row.heroCard || {};
  const vc = row.valueClarity?.hero || row.valueClarity || {};
  const ucId = row.heroUseCaseId;
  const to = hrefFn ? hrefFn(`/demo/${ent.id}/${ucId}`) : `#/demo/${ent.id}/${ucId}`;
  return (
    <a className="hero-demo-card" href={to}>
      <p className="kicker">{row.domainAudienceLabel}</p>
      <h2>{hero.cardTitle || ent.label}</h2>
      <p className="hero-problem">{hero.businessProblem}</p>
      {vc.zeroContextAnswer ? <p className="tiny network-add-line">Network adds · {vc.zeroContextAnswer}</p> : null}
      <dl className="hero-meta">
        <dt>Intent</dt>
        <dd>
          <code>{hero.intentId}</code>
        </dd>
        <dt>Proves</dt>
        <dd>
          <ul className="proves">
            {(hero.proves || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </dd>
      </dl>
    </a>
  );
}
