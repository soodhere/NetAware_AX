import { useEffect, useMemo, useState } from "react";
import { api, apiVersionMaturityTone, formatList, href } from "../api.js";

const NAV_GROUPS = [
  {
    label: "Business",
    items: [
      ["domains", "Domains"],
      ["use-cases", "Use cases"],
      ["intents", "Intents"],
    ],
  },
  {
    label: "Governance",
    items: [
      ["agents", "Agents"],
      ["my-context", "My Context"],
      ["purposes", "Purposes"],
      ["policies", "Policies"],
      ["autonomy", "Autonomy"],
    ],
  },
  {
    label: "Network",
    items: [
      ["capabilities", "Capabilities"],
      ["catalog", "API Catalog"],
      ["providers", "Providers / Routes"],
    ],
  },
];

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function GradeBadge({ grade }) {
  if (!grade?.raw) return null;
  const tone = grade.raw === "SOURCE_BACKED" ? "ok" : grade.raw === "INFERRED" ? "warn" : "";
  return (
    <Pill tone={tone}>
      {grade.short || grade.raw}
      {grade.raw === "INFERRED" ? " · hypothesis" : ""}
    </Pill>
  );
}

function LiveDemoLink({ live }) {
  if (!live?.enterpriseId || !live?.useCaseId) return null;
  return (
    <a className="chip" href={href(`/demo/${live.enterpriseId}/${live.useCaseId}/run`)}>
      Live: {live.label || "Run demo"}
    </a>
  );
}

function Side({ section }) {
  return (
    <nav className="side">
      <a className={`nav-link${!section || section === "home" ? " on" : ""}`} href={href("/explore")}>
        Overview
      </a>
      {NAV_GROUPS.map((group) => (
        <div key={group.label} className="nav-group">
          <span className="nav-group-label">{group.label}</span>
          {group.items.map(([id, label]) => (
            <a key={id} className={`nav-link${section === id ? " on" : ""}`} href={href(`/explore/${id}`)}>
              {label}
            </a>
          ))}
        </div>
      ))}
    </nav>
  );
}

function FilterBar({ query, onQuery, placeholder }) {
  return (
    <input
      className="filter-input section"
      type="search"
      placeholder={placeholder || "Filter…"}
      value={query}
      onChange={(e) => onQuery(e.target.value)}
    />
  );
}

function Links({ items, to, labelKey = "label", idKey = "id" }) {
  if (!items?.length) return <p className="tiny">None mapped in the active catalog.</p>;
  return (
    <div className="chips">
      {items.filter(Boolean).map((item) => (
        <a key={item[idKey]} className="chip" href={href(`${to}/${item[idKey]}`)}>
          {item[labelKey] || item[idKey]}
        </a>
      ))}
    </div>
  );
}

function NetworkRolePill({ role }) {
  if (!role) return null;
  const tone = role === "ACT" ? "ok" : role === "VERIFY" ? "warn" : "muted";
  return <Pill tone={tone}>{role}</Pill>;
}

function CamaraPrimaryChips({ row, fam }) {
  const apiRow = fam || row?.api || row || {};
  const version = formatList(row?.camaraApiVersion || apiRow.camaraApiVersion);
  const maturity = formatList(row?.apiVersionMaturity || apiRow.apiVersionMaturity);
  const status = (row?.netawareBusinessStatus || apiRow.netawareBusinessStatus || apiRow.businessStatus || "")
    .replaceAll("_", " ");
  return (
    <>
      <NetworkRolePill role={apiRow.networkRole} />
      {status ? <Pill tone="ok">NetAware {status}</Pill> : null}
      {version ? <Pill>CAMARA API {version}</Pill> : null}
      {maturity ? (
        <Pill tone={apiVersionMaturityTone(maturity)}>API version {maturity}</Pill>
      ) : null}
    </>
  );
}

function CamaraTechnicalMeta({ lifecycle }) {
  const value = formatList(lifecycle);
  if (!value) return null;
  return (
    <div className="chips section">
      <Pill tone="muted">CAMARA project lifecycle {value}</Pill>
    </div>
  );
}

function FamilyCard({ fam, reverse }) {
  const apiRow = reverse?.api || fam;
  return (
    <a className="panel family-card" href={href(`/explore/catalog/${apiRow.id}`)}>
      <p className="kicker">{apiRow.familyGroup?.replaceAll("_", " ")}</p>
      <h2>{apiRow.label}</h2>
      <div className="chips" style={{ margin: "8px 0" }}>
        <CamaraPrimaryChips row={reverse} fam={apiRow} />
      </div>
      {apiRow.applicationValue ? <p className="tiny">{apiRow.applicationValue}</p> : null}
      <p className="tiny">
        {(reverse?.capabilities || []).map((c) => c.label).join(" · ") || (apiRow.capabilities || []).join(" · ")}
      </p>
    </a>
  );
}

function ExploreHome({ summary }) {
  return (
    <div>
      <p className="kicker">Explorer</p>
      <h1>
        <span>Product knowledge model</span>
      </h1>
      <p className="lede">
        Small practical catalog. Many business outcomes. Walk forward from domain to API, or reverse from operation to
        industry.
      </p>
      <div className="grid-4 section">
        <article className="inset">
          <span className="tiny">Business families</span>
          <strong style={{ fontSize: 28 }}>{summary?.businessFamilies ?? "—"}</strong>
        </article>
        <article className="inset">
          <span className="tiny">Domains</span>
          <strong style={{ fontSize: 28 }}>{summary?.domains ?? "—"}</strong>
        </article>
        <article className="inset">
          <span className="tiny">Intents</span>
          <strong style={{ fontSize: 28 }}>{summary?.intents ?? "—"}</strong>
        </article>
        <article className="inset">
          <span className="tiny">Agents</span>
          <strong style={{ fontSize: 28 }}>{summary?.agents ?? "—"}</strong>
        </article>
      </div>
      <p className="tiny">{summary?.note}</p>
    </div>
  );
}

function DomainList() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => {
    api("/domains").then(setData);
  }, []);
  const rows = useMemo(
    () => (data?.domains || []).filter((d) => !q || d.label?.toLowerCase().includes(q.toLowerCase())),
    [data, q]
  );
  return (
    <div>
      <h1>
        <span>Domains</span>
      </h1>
      <FilterBar query={q} onQuery={setQ} placeholder="Filter domains…" />
      <section className="grid-3 section">
        {rows.map((d) => (
          <a key={d.id} className="card-btn" href={href(`/explore/domains/${d.id}`)}>
            <h2>{d.label}</h2>
            <p className="tiny">{d.description}</p>
          </a>
        ))}
      </section>
    </div>
  );
}

function DomainDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/domains/${id}`).then(setData);
  }, [id]);
  const domain = data?.domain || {};
  return (
    <div>
      <p className="kicker">Domain</p>
      <h1>
        <span>{domain.label}</span>
      </h1>
      <p className="lede">{domain.description}</p>
      {data?.exampleEnterprise ? (
        <p className="tiny">
          Example enterprise · <strong>{data.exampleEnterprise.label}</strong>
        </p>
      ) : null}
      {data?.liveDemo ? (
        <div className="section">
          <LiveDemoLink live={data.liveDemo} />
        </div>
      ) : null}
      <section className="section">
        <h3>Network API families in this domain</h3>
        <Links items={data?.networkFamilies} to="/explore/catalog" />
      </section>
      <section className="section">
        {(data?.useCaseRows || data?.useCases || []).map((row) => {
          const uc = row.useCase || row;
          return (
            <article key={uc.id} className="panel" style={{ marginBottom: 10 }}>
              <h2>
                <a href={href(`/explore/use-cases/${uc.id}`)}>{uc.label}</a>
              </h2>
              {row.networkFamilies?.length ? (
                <p className="tiny">Families: {row.networkFamilies.join(" · ")}</p>
              ) : null}
              <Links items={(row.intents || []).map((i) => i.intent).filter(Boolean)} to="/explore/intents" />
            </article>
          );
        })}
      </section>
    </div>
  );
}

function UseCaseList() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => {
    api("/use-cases").then(setData);
  }, []);
  const rows = useMemo(
    () => (data?.useCases || []).filter((uc) => !q || uc.label?.toLowerCase().includes(q.toLowerCase())),
    [data, q]
  );
  return (
    <div>
      <h1>
        <span>Use cases</span>
      </h1>
      <p className="lede">Use case = business job. Intent = runtime outcome request.</p>
      <FilterBar query={q} onQuery={setQ} placeholder="Filter use cases…" />
      <ul className="list section">
        {rows.map((uc) => (
          <li key={uc.id}>
            <a href={href(`/explore/use-cases/${uc.id}`)}>{uc.label}</a>
            <span className="tiny"> · {uc.domainId}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function UseCaseDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/use-cases/${id}`).then(setData);
  }, [id]);
  const uc = data?.useCase || {};
  return (
    <div>
      <p className="kicker">Use case</p>
      <h1>
        <span>{uc.label}</span>
      </h1>
      <p className="tiny">
        Domain · <a href={href(`/explore/domains/${data?.domain?.id}`)}>{data?.domain?.label}</a>
      </p>
      <p className="lede">{data?.businessProblem || uc.networkComplement}</p>
      <div className="banner warn">{data?.intentVsUseCase}</div>
      {data?.liveDemo ? (
        <div className="section">
          <LiveDemoLink live={data.liveDemo} />
        </div>
      ) : null}
      <section className="grid-2 section">
        <article className="panel">
          <h3>Existing systems / APIs</h3>
          <ul className="list">
            {(data?.existingSystems || []).map((s) => (
              <li key={s}>{s}</li>
            ))}
            {(data?.existingApis || uc.existingApis || []).map((item) => (
              <li key={`${item.kind}-${item.name}`}>
                {item.name} <span className="tiny">· {item.kind}</span>
              </li>
            ))}
          </ul>
          <h3 style={{ marginTop: 16 }}>Purpose</h3>
          <p>{data?.purpose?.audienceLabel || data?.purpose?.label || "—"}</p>
        </article>
        <article className="panel">
          <h3>Intents</h3>
          <Links items={(data?.intents || []).map((i) => i.intent).filter(Boolean)} to="/explore/intents" />
          <h3 style={{ marginTop: 16 }}>Network API families</h3>
          <p className="tiny">{(data?.networkFamilies || []).join(" · ") || "—"}</p>
          <h3 style={{ marginTop: 16 }}>Capabilities</h3>
          {(data?.capabilitiesSummary || []).map((cap) => (
            <div key={cap.id} className="op-row">
              <a href={href(`/explore/capabilities/${cap.id}`)}>{cap.label}</a>
              <GradeBadge grade={cap.evidenceGrade} />
            </div>
          ))}
        </article>
      </section>
    </div>
  );
}

function IntentList() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => {
    api("/intents").then(setData);
  }, []);
  const rows = useMemo(
    () => (data?.intents || []).filter((i) => !q || i.label?.toLowerCase().includes(q.toLowerCase()) || i.id?.includes(q)),
    [data, q]
  );
  return (
    <div>
      <h1>
        <span>Intents</span>
      </h1>
      <FilterBar query={q} onQuery={setQ} placeholder="Filter intents…" />
      <ul className="list section">
        {rows.map((intent) => (
          <li key={intent.id}>
            <a href={href(`/explore/intents/${intent.id}`)}>{intent.label}</a>
            <code className="tiny"> {intent.id}</code>
          </li>
        ))}
      </ul>
    </div>
  );
}

function IntentDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/intents/${id}`).then(setData);
  }, [id]);
  const intent = data?.intent || {};
  return (
    <div>
      <p className="kicker">Intent</p>
      <h1>
        <span>{intent.label}</span>
      </h1>
      <p className="tiny">
        <a href={href(`/explore/domains/${data?.domain?.id}`)}>{data?.domain?.label}</a>
        {" → "}
        <a href={href(`/explore/use-cases/${data?.useCase?.id}`)}>{data?.useCase?.label}</a>
      </p>
      {data?.executable ? <Pill tone="ok">Executable</Pill> : data?.explorerOnly ? <Pill>Explorer only</Pill> : null}
      {data?.liveDemo ? (
        <div className="section">
          <LiveDemoLink live={data.liveDemo} />
        </div>
      ) : null}
      <section className="grid-2 section">
        <article className="panel">
          <h3>{data?.knownFromConfiguration?.source || "What NetAware already knows"}</h3>
          <p className="tiny">{data?.knownFromConfiguration?.note}</p>
          <ul className="list">
            {(data?.knownFromConfiguration?.rows || []).map((r) => (
              <li key={r.label}>
                {r.label}: <strong>{r.value}</strong>
              </li>
            ))}
          </ul>
          <h3 style={{ marginTop: 16 }}>Agents</h3>
          <Links items={data?.agents} to="/explore/agents" />
          <h3 style={{ marginTop: 16 }}>Policies</h3>
          <Links items={data?.policies} to="/explore/policies" />
        </article>
        <article className="panel">
          <h3>What the caller sends at runtime</h3>
          <p className="tiny">{data?.runtimeRequestNote}</p>
          <pre className="code-block">{JSON.stringify(data?.runtimeRequest || {}, null, 2)}</pre>
        </article>
      </section>
      <section className="section">
        {(data?.capabilities || []).map((block) => {
          const cap = block.capability || {};
          return (
            <article key={cap.id} className="panel" style={{ marginBottom: 10 }}>
              <h2>
                <a href={href(`/explore/capabilities/${cap.id}`)}>{cap.label}</a>
              </h2>
              <p className="tiny">
                {block.role} · <GradeBadge grade={block.evidenceGrade} />
              </p>
              {(block.liveBehavior || []).map((lb) => (
                <p key={lb.scenario} className="tiny">
                  Live: {lb.scenario} → {lb.state}
                </p>
              ))}
              {(block.operations || []).map((op) => (
                <div className="op-row" key={`${op.operationId}-${op.source}`}>
                  <a href={href(`/explore/operations/${op.operationId}`)}>
                    <code>{op.operationId}</code>
                  </a>
                </div>
              ))}
            </article>
          );
        })}
      </section>
    </div>
  );
}

function AgentList() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/agents").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>Agents</span>
      </h1>
      <p className="banner warn">Identity / delegation model: SIMULATED FOR PROTOTYPE</p>
      <ul className="list section">
        {(data?.agents || []).map((row) => (
          <li key={row.agent?.id}>
            <a href={href(`/explore/agents/${row.agent.id}`)}>{row.agent.label}</a>
            <span className="tiny">
              {" "}
              · {row.enterprise?.label} · acts for {row.application?.label}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AgentDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/explore/agents/${id}`).then(setData);
  }, [id]);
  return (
    <div>
      <p className="kicker">Agent</p>
      <h1>
        <span>{data?.agent?.label}</span>
      </h1>
      <div className="banner warn">{data?.identityModel} — {data?.identityNote}</div>
      <section className="grid-2 section">
        <article className="panel">
          <h3>Enterprise / application</h3>
          <p>
            {data?.enterprise?.label} · {data?.application?.label}
          </p>
          <h3 style={{ marginTop: 16 }}>Allowed intents</h3>
          <Links items={data?.allowedIntents} to="/explore/intents" />
        </article>
        <article className="panel">
          <h3>Policies & autonomy</h3>
          <Links items={data?.policies} to="/explore/policies" />
          <ul className="list" style={{ marginTop: 12 }}>
            {(data?.autonomyRules || []).map((r) => (
              <li key={r.id}>
                {r.action}: <strong>{r.level}</strong>
              </li>
            ))}
          </ul>
        </article>
      </section>
      <div className="chips section">
        {(data?.liveIntents || []).filter(Boolean).map((live) => (
          <LiveDemoLink key={live.useCaseId} live={live} />
        ))}
      </div>
    </div>
  );
}

function MyContextList() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/my-context").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>My Context</span>
      </h1>
      <p className="lede">NetAware reuses configured knowledge. Applications send minimal runtime requests.</p>
      <ul className="list section">
        {(data?.enterprises || []).map((e) => (
          <li key={e.id}>
            <a href={href(`/explore/my-context/${e.id}`)}>{e.label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MyContextDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/explore/my-context/${id}`).then(setData);
  }, [id]);
  return (
    <div>
      <p className="kicker">My Context</p>
      <h1>
        <span>{data?.enterprise?.label}</span>
      </h1>
      <section className="grid-2 section">
        <article className="panel">
          <h3>{data?.knownFromConfiguration?.source}</h3>
          <p className="tiny">{data?.knownFromConfiguration?.note}</p>
          <ul className="list">
            <li>Purposes: {(data?.purposes || []).map((p) => p?.label).join(" · ") || "—"}</li>
            <li>Agents: {(data?.agents || []).map((a) => a.label).join(" · ")}</li>
            <li>Policies: {(data?.policies || []).length} configured</li>
            <li>Subscriptions / entitlements: configured</li>
          </ul>
        </article>
        <article className="panel">
          <h3>{data?.runtimeRequestSource}</h3>
          <pre className="code-block">{JSON.stringify(data?.runtimeRequestExample || {}, null, 2)}</pre>
        </article>
      </section>
    </div>
  );
}

function PurposeList() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/purposes").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>Purposes</span>
      </h1>
      <ul className="list section">
        {(data?.purposes || []).map((p) => (
          <li key={p.id}>
            <a href={href(`/explore/purposes/${p.id}`)}>{p.audienceLabel || p.label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PurposeDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/explore/purposes/${id}`).then(setData);
  }, [id]);
  const p = data?.purpose || {};
  return (
    <div>
      <p className="kicker">Purpose</p>
      <h1>
        <span>{p.audienceLabel || p.label}</span>
      </h1>
      <div className="banner warn">{data?.legalNote}</div>
      <section className="grid-2 section">
        <article className="panel">
          <h3>Intents using this purpose</h3>
          <Links items={data?.intents} to="/explore/intents" />
        </article>
        <article className="panel">
          <h3>Policies</h3>
          <Links items={data?.policies} to="/explore/policies" />
        </article>
      </section>
    </div>
  );
}

function PolicyList() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/policies").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>Policies</span>
      </h1>
      <ul className="list section">
        {(data?.policies || []).map((p) => (
          <li key={p.id}>
            <a href={href(`/explore/policies/${p.id}`)}>{p.label}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PolicyDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/explore/policies/${id}`).then(setData);
  }, [id]);
  return (
    <div>
      <p className="kicker">Policy</p>
      <h1>
        <span>{data?.policy?.label}</span>
      </h1>
      <div className="banner warn">{data?.source} — not a universal legal requirement.</div>
      {data?.liveScenario ? (
        <div className="section">
          <LiveDemoLink live={data.liveScenario} />
        </div>
      ) : null}
      <section className="section">
        <h3>Exercised in live scenarios</h3>
        <ul className="list">
          {(data?.exercisedEffects || []).map((e) => (
            <li key={e}>{e}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function AutonomyView() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/autonomy").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>Autonomy</span>
      </h1>
      <p className="lede">{data?.tagline}</p>
      <div className="chips section">
        {(data?.model || []).map((l) => (
          <Pill key={l}>{l}</Pill>
        ))}
      </div>
      <section className="section">
        {(data?.examples || []).map((ex) => (
          <article key={ex.enterprise} className="panel" style={{ marginBottom: 10 }}>
            <h2>{ex.enterprise}</h2>
            <ul className="list">
              {ex.rows.map(([action, level]) => (
                <li key={action}>
                  {action}: <strong>{level}</strong>
                </li>
              ))}
            </ul>
            {ex.intentId ? (
              <a className="tiny" href={href(`/explore/intents/${ex.intentId}`)}>
                View intent
              </a>
            ) : null}
          </article>
        ))}
      </section>
    </div>
  );
}

function CapabilityList() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => {
    api("/capabilities").then(setData);
  }, []);
  const rows = useMemo(
    () =>
      (data?.capabilities || []).filter(
        (cap) => !q || cap.label?.toLowerCase().includes(q.toLowerCase()) || cap.family?.includes(q)
      ),
    [data, q]
  );
  return (
    <div>
      <h1>
        <span>Capabilities</span>
      </h1>
      <FilterBar query={q} onQuery={setQ} placeholder="Filter by name or family…" />
      <ul className="list section">
        {rows.map((cap) => (
          <li key={cap.id}>
            <a href={href(`/explore/capabilities/${cap.id}`)}>{cap.label}</a>
            <span className="tiny"> · {cap.family}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CapabilityDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/capabilities/${id}`).then(setData);
  }, [id]);
  const cap = data?.capability || {};
  return (
    <div>
      <p className="kicker">Capability</p>
      <h1>
        <span>{cap.label}</span>
      </h1>
      {(data?.liveBehavior || []).map((lb) => (
        <p key={lb.scenario} className="tiny">
          {lb.scenario}: <strong>{lb.state}</strong>
          {lb.intentId ? (
            <>
              {" "}
              · <a href={href(`/explore/intents/${lb.intentId}`)}>{lb.intentId}</a>
            </>
          ) : null}
        </p>
      ))}
      <section className="grid-2 section">
        <article className="panel">
          <h3>API catalog families</h3>
          <Links items={data?.catalogFamilies} to="/explore/catalog" />
          <h3 style={{ marginTop: 16 }}>Technical operations</h3>
          {(data?.operations || []).map((op) => (
            <div className="op-row" key={`${op.operationId}-${op.source}`}>
              <a href={href(`/explore/operations/${op.operationId}`)}>
                <code>{op.operationId}</code>
              </a>
            </div>
          ))}
        </article>
        <article className="panel">
          <h3>Intents / use cases / domains</h3>
          <Links items={data?.intents} to="/explore/intents" />
          <Links items={data?.useCases} to="/explore/use-cases" />
          <Links items={data?.domains} to="/explore/domains" />
        </article>
      </section>
    </div>
  );
}

function CatalogList() {
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");
  useEffect(() => {
    api("/catalog/apis").then(setData);
  }, []);
  const apis = data?.apis || [];
  const rows = useMemo(
    () => apis.filter((row) => !q || row.api?.label?.toLowerCase().includes(q.toLowerCase())),
    [apis, q]
  );
  return (
    <div>
      <p className="kicker">AX active catalog</p>
      <h1>
        <span>Small practical catalog</span>
      </h1>
      <p className="lede plus-line">
        {apis.length} current-focus Network API families → many capabilities → many business outcomes.
      </p>
      <p className="tiny">
        Each family is labelled <strong>Observe</strong>, <strong>Verify</strong>, or <strong>Act</strong> — what it
        gives the application, not just a technical API name.
      </p>
      <div className="chips section">
        <Pill tone="muted">Observe · network information</Pill>
        <Pill tone="warn">Verify · independent assertions</Pill>
        <Pill tone="ok">Act · network actions</Pill>
      </div>
      <FilterBar query={q} onQuery={setQ} placeholder="Filter API families…" />
      <section className="grid-2 section">
        {rows.map((row) => (
          <FamilyCard key={row.api?.id} fam={row.api} reverse={row} />
        ))}
      </section>
    </div>
  );
}

function CatalogDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/catalog/apis/${id}`).then(setData);
  }, [id]);
  const fam = data?.api || {};
  return (
    <div>
      <p className="kicker">Business API family</p>
      <h1>
        <span>{fam.label}</span>
      </h1>
      <div className="chips section">
        <CamaraPrimaryChips row={data} fam={fam} />
      </div>
      {fam.applicationValue ? (
        <article className="panel section">
          <h3>What this gives the application</h3>
          <p>{fam.applicationValue}</p>
        </article>
      ) : null}
      {(data?.liveReferences || []).length ? (
        <div className="chips section">
          {data.liveReferences.map((live) => (
            <LiveDemoLink key={live.useCaseId} live={live} />
          ))}
        </div>
      ) : null}
      <section className="grid-2 section">
        <article className="panel">
          <h3>Capabilities</h3>
          <Links items={data?.capabilities} to="/explore/capabilities" />
          <h3 style={{ marginTop: 16 }}>Operations</h3>
          {(data?.operations || []).map((op) => (
            <div className="op-row" key={op.operation_id}>
              <a href={href(`/explore/operations/${op.operation_id}`)}>
                <code>{op.operation_id}</code>
              </a>
              {op.liveHint ? <span className="tiny"> · {op.liveHint}</span> : null}
            </div>
          ))}
          {(fam.technicalSpecs || []).length ? (
            <>
              <h3 style={{ marginTop: 16 }}>Technical specs</h3>
              {(fam.technicalSpecs || []).map((spec) => (
                <p className="tiny" key={`${spec.source}-${spec.version}`}>
                  {spec.api_name} · CAMARA API {spec.camaraApiVersion || spec.version}
                  {spec.apiVersionMaturity ? ` · API version ${spec.apiVersionMaturity}` : ""}
                  {spec.camaraProjectLifecycle ? ` · CAMARA project lifecycle ${spec.camaraProjectLifecycle}` : ""}
                </p>
              ))}
            </>
          ) : null}
        </article>
        <article className="panel">
          <h3>Reverse traversal</h3>
          <Links items={data?.intents} to="/explore/intents" />
          <Links items={data?.useCases} to="/explore/use-cases" />
          <Links items={data?.domains} to="/explore/domains" />
        </article>
      </section>
    </div>
  );
}

function OperationDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/catalog/${id}`).then(setData);
  }, [id]);
  const variant = (data?.catalogVariants || [])[0] || {};
  return (
    <div>
      <p className="kicker">Technical operation</p>
      <h1>
        <span>
          <code>{data?.operationId}</code>
        </span>
      </h1>
      {data?.liveHint ? <p className="lede">{data.liveHint}</p> : null}
      <div className="chips section">
        <Pill tone="ok">NetAware {(data?.netawareBusinessStatus || variant.business_status || "").replaceAll("_", " ")}</Pill>
        {variant.camaraApiVersion ? <Pill>CAMARA API {variant.camaraApiVersion}</Pill> : null}
        {variant.apiVersionMaturity ? (
          <Pill tone={apiVersionMaturityTone(variant.apiVersionMaturity)}>API version {variant.apiVersionMaturity}</Pill>
        ) : null}
      </div>
      <CamaraTechnicalMeta lifecycle={variant.camaraProjectLifecycle} />
      <section className="grid-2 section">
        <article className="panel">
          <h3>Capabilities → intents</h3>
          <Links items={data?.capabilities} to="/explore/capabilities" />
          <Links items={data?.intents} to="/explore/intents" />
        </article>
        <article className="panel">
          <h3>Use cases / domains</h3>
          <Links items={data?.useCases} to="/explore/use-cases" />
          <Links items={data?.domains} to="/explore/domains" />
        </article>
      </section>
    </div>
  );
}

function ProvidersView() {
  const [data, setData] = useState(null);
  useEffect(() => {
    api("/explore/providers").then(setData);
  }, []);
  return (
    <div>
      <h1>
        <span>Providers / Routes</span>
      </h1>
      <p className="lede">Generic topology-neutral names. Not a hosting model claim.</p>
      <section className="grid-2 section">
        <article className="panel">
          <h3>Providers</h3>
          <ul className="list">
            {(data?.providers || []).map((p) => (
              <li key={p.id}>
                <a href={href(`/explore/providers/${p.id}`)}>{p.audienceLabel || p.label}</a>
                <span className="tiny"> · {p.kind}</span>
              </li>
            ))}
          </ul>
        </article>
        <article className="panel">
          <h3>Configured routes</h3>
          <ul className="list">
            {(data?.routes || []).map((r) => (
              <li key={r.id}>
                <code>{r.operationId}</code> → {r.provider?.audienceLabel || r.providerId}{" "}
                <strong>{r.routeType}</strong>
                {r.enterpriseId ? <span className="tiny"> · {r.enterpriseId}</span> : null}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}

function ProviderDetail({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    api(`/explore/providers/${id}`).then(setData);
  }, [id]);
  return (
    <div>
      <p className="kicker">Provider</p>
      <h1>
        <span>{data?.provider?.audienceLabel || data?.provider?.label}</span>
      </h1>
      <section className="section">
        <h3>Operations available</h3>
        <ul className="list">
          {(data?.operations || []).map((op) => (
            <li key={op.operationId}>
              <a href={href(`/explore/operations/${op.operationId}`)}>
                <code>{op.operationId}</code>
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default function Explore({ parts }) {
  const [summary, setSummary] = useState(null);
  const [section, id] = parts;
  const view = section || "";

  useEffect(() => {
    api("/explore").then(setSummary);
  }, []);

  let body = <ExploreHome summary={summary} />;
  if (view === "domains" && !id) body = <DomainList />;
  else if (view === "domains" && id) body = <DomainDetail id={id} />;
  else if (view === "use-cases" && !id) body = <UseCaseList />;
  else if (view === "use-cases" && id) body = <UseCaseDetail id={id} />;
  else if (view === "intents" && !id) body = <IntentList />;
  else if (view === "intents" && id) body = <IntentDetail id={id} />;
  else if (view === "agents" && !id) body = <AgentList />;
  else if (view === "agents" && id) body = <AgentDetail id={id} />;
  else if (view === "my-context" && !id) body = <MyContextList />;
  else if (view === "my-context" && id) body = <MyContextDetail id={id} />;
  else if (view === "purposes" && !id) body = <PurposeList />;
  else if (view === "purposes" && id) body = <PurposeDetail id={id} />;
  else if (view === "policies" && !id) body = <PolicyList />;
  else if (view === "policies" && id) body = <PolicyDetail id={id} />;
  else if (view === "autonomy") body = <AutonomyView />;
  else if (view === "capabilities" && !id) body = <CapabilityList />;
  else if (view === "capabilities" && id) body = <CapabilityDetail id={id} />;
  else if (view === "catalog" && !id) body = <CatalogList />;
  else if (view === "catalog" && id) body = <CatalogDetail id={id} />;
  else if (view === "providers" && !id) body = <ProvidersView />;
  else if (view === "providers" && id) body = <ProviderDetail id={id} />;
  else if (view === "operations" && id) body = <OperationDetail id={id} />;
  else if (view === "sim-swap") body = <CatalogDetail id="sim-swap" />;

  return (
    <div className="explore-layout">
      <Side section={view || "home"} />
      <div>{body}</div>
    </div>
  );
}
