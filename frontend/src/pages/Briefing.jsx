import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import AxLoop from "../components/AxLoop.jsx";

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function NetworkRolePill({ role, rolesMeta }) {
  if (!role) return null;
  const meta = rolesMeta?.[role] || {};
  return (
    <Pill tone={role === "ACT" ? "ok" : role === "VERIFY" ? "warn" : "muted"}>
      {meta.label || role}
    </Pill>
  );
}

const RUNNABLE = new Set([
  "rocket-bank/high-value-payment-protection",
  "rocket-bank/passwordless-mobile-sign-in",
  "high-flight-airlines/baggage-connection",
  "acme-manufacturing/critical-inspection-camera",
  "citycare-health/pharmacy-age-gate",
  "rocket-bank/account-recovery-anomaly",
]);

export default function Briefing({ enterpriseId, useCaseId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/demo/${enterpriseId}/${useCaseId}`)
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, [enterpriseId, useCaseId]);

  if (error) return <p className="err">{error}</p>;
  if (!data) return <p className="tiny">Loading…</p>;

  const intent = data.intent || {};
  const agent = data.agent || {};
  const known = data.knownFromOnboarding || {};
  const policy = data.policyPreview || {};
  const autonomy = data.autonomyPreview || {};
  const vc = data.valueClarity || {};
  const framing = data.networkValueFraming || {};
  const rolesMeta = data.networkRoles || {};
  const key = `${enterpriseId}/${useCaseId}`;
  const runnable = RUNNABLE.has(key);
  const isSecondary = data.secondaryDemo;

  return (
    <div>
      <p className="kicker">{data.domainAudienceLabel}</p>
      <h1>
        <span>{data.enterprise?.label}</span>
      </h1>
      <p className="tiny">Use case · {data.useCase?.label}</p>

      <div className="banner intent-def">
        {framing.intentLine ||
          intent.explainer ||
          "Intent is the outcome the application or agent wants — without specifying which Network APIs should be called."}
      </div>
      {vc.headline ? <p className="lede value-headline">{vc.headline}</p> : null}
      {vc.zeroContextAnswer ? (
        <p className="tiny zero-context">
          <strong>Network adds:</strong> {vc.zeroContextAnswer}
        </p>
      ) : null}

      <section className="section value-framing">
        <h3>How domain and network complement</h3>
        <div className="value-ladder">
          <article className="panel domain-lane">
            <p className="kicker">My world</p>
            <p className="tiny">{framing.applicationLayer}</p>
          </article>
          <article className="panel network-lane">
            <p className="kicker">Network adds</p>
            <p className="tiny">{framing.networkLayer}</p>
          </article>
          <article className="panel ax-lane">
            <p className="kicker">NetAware AX</p>
            <p className="tiny">{framing.axLayer}</p>
          </article>
        </div>
      </section>

      {vc.myWorld ? (
        <section className="section" id="my-world">
          <h3>1 · {vc.myWorld.title || "My world"}</h3>
          <article className="panel">
            <ul className="list">
              {(vc.myWorld.items || []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            {(data.existingSystems || []).length ? (
              <>
                <p className="kicker" style={{ marginTop: 12 }}>
                  Existing systems
                </p>
                <ul className="list compact">
                  {(data.existingSystems || []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </>
            ) : null}
          </article>
        </section>
      ) : null}

      {vc.networkAdds ? (
        <section className="section" id="network-adds">
          <h3>2 · {vc.networkAdds.title || "Network adds"}</h3>
          <article className="panel network">
            <div className="chips" style={{ marginBottom: 10 }}>
              {(vc.networkAdds.roles || []).map((role) => (
                <NetworkRolePill key={role} role={role} rolesMeta={rolesMeta} />
              ))}
            </div>
            <ul className="list">
              {(vc.networkAdds.items || []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            {(data.capabilities || []).length ? (
              <>
                <p className="kicker" style={{ marginTop: 12 }}>
                  Mapped capabilities
                </p>
                <ul className="list compact">
                  {(data.capabilities || []).map((cap) => (
                    <li key={cap.id}>
                      <a href={href(`/explore/capabilities/${cap.id}`)}>{cap.label}</a>
                      {cap.networkRole ? (
                        <>
                          {" "}
                          <NetworkRolePill role={cap.networkRole} rolesMeta={rolesMeta} />
                        </>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
          </article>
        </section>
      ) : null}

      {vc.netawareAx ? (
        <section className="section" id="netaware-ax">
          <h3>3 · {vc.netawareAx.title || "NetAware AX"}</h3>
          <article className="panel">
            <ul className="list">
              {(vc.netawareAx.items || []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          {vc.openingHeroNote ? <p className="tiny banner warn">{vc.openingHeroNote}</p> : null}
        </section>
      ) : null}

      <section className="section" id="my-intent">
        <h3>4 · My intent</h3>
        <div className="panel">
          <p className="kicker">Outcome</p>
          <h2>“{intent.plain}”</h2>
          <p className="tiny">
            <code>{intent.id}</code>
          </p>
        </div>
      </section>

      <section className="section" id="what-i-send">
        <h3>5 · What I send vs what NetAware already knows</h3>
        <div className="split-know">
          <article className="panel">
            <p className="kicker">{known.source}</p>
            <p className="tiny">{known.note}</p>
            <dl className="dl" style={{ marginTop: 12 }}>
              {(known.rows || []).map((row) => (
                <div key={row.label} style={{ display: "contents" }}>
                  <dt>{row.label}</dt>
                  <dd>{row.value}</dd>
                </div>
              ))}
            </dl>
          </article>
          <article className="panel">
            <p className="kicker">{data.runtimeRequest?.source}</p>
            <p className="tiny">{data.runtimeRequest?.note}</p>
            <pre className="code-block">{JSON.stringify(data.runtimeRequest?.body, null, 2)}</pre>
          </article>
        </div>
      </section>

      <section className="section" id="my-agent">
        <h3>6 · My agent</h3>
        <div className="panel">
          <div className="chips" style={{ marginBottom: 10 }}>
            <Pill tone="ok">Authorized agent</Pill>
            <Pill>Simulated identity</Pill>
          </div>
          <h2>{agent.label}</h2>
          <dl className="dl">
            <dt>Acts for</dt>
            <dd>{agent.actsForLabel}</dd>
            <dt>Allowed intents</dt>
            <dd>
              {(agent.allowedIntents || []).map((id) => (
                <a key={id} href={href(`/explore/intents/${id}`)} style={{ marginRight: 10 }}>
                  {id}
                </a>
              ))}
            </dd>
          </dl>
          <p className="tiny">{agent.identityNote}</p>
        </div>
      </section>

      <section className="section grid-2" id="policy-autonomy">
        <article className="panel">
          <h3>7 · My policy</h3>
          <p className="tiny">{policy.label}</p>
          <Pill>{policy.source || "CONFIGURED DEMO POLICY"}</Pill>
          <dl className="dl" style={{ marginTop: 10 }}>
            <dt>Purpose</dt>
            <dd>{policy.purpose}</dd>
            <dt>Consent</dt>
            <dd>{policy.consent}</dd>
            <dt>Agreement / DPA</dt>
            <dd>{policy.agreement}</dd>
          </dl>
        </article>
        <article className="panel">
          <h3>8 · My autonomy</h3>
          <p className="tiny">{autonomy.label}</p>
          <dl className="dl" style={{ marginTop: 10 }}>
            <dt>Observe / Act</dt>
            <dd>{autonomy.summary?.observe}</dd>
            <dt>Recommend</dt>
            <dd>{autonomy.summary?.recommend}</dd>
            <dt>Act with approval</dt>
            <dd>{autonomy.summary?.actWithApproval}</dd>
          </dl>
        </article>
      </section>

      <AxLoop compact />

      <section className="section" id="run">
        <h3>9 · Run</h3>
        {isSecondary ? (
          <div className="panel">
            <p className="kicker">Secondary · evidence reuse</p>
            <p className="tiny">{data.secondaryNote}</p>
            <div className="hero-actions">
              <a href={href(`/demo/${enterpriseId}/${useCaseId}/run`)}>
                <button className="primary" type="button">
                  Run evidence reuse
                </button>
              </a>
              <a href={href("/explore/intents/assess_recovery_continuity")}>
                <button type="button">Explorer</button>
              </a>
            </div>
          </div>
        ) : runnable ? (
          <div className="hero-actions">
            <a href={href(`/demo/${enterpriseId}/${useCaseId}/run`)}>
              <button className="primary" type="button">
                Run Intent
              </button>
            </a>
            {enterpriseId === "rocket-bank" && useCaseId === "high-value-payment-protection" ? (
              <a href={href("/demo/rocket-bank/account-recovery-anomaly")}>
                <button type="button">See evidence reuse</button>
              </a>
            ) : null}
          </div>
        ) : (
          <p className="tiny">Configuration only — explore mapping in Explorer.</p>
        )}
      </section>
    </div>
  );
}
