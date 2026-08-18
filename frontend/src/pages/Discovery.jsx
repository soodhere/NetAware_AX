import { href } from "../api.js";
import { NetworkOpportunity, NvFinderStrip, NvHonesty, NvPathVisual, NvPathVsOperation } from "./NvPath.jsx";

function Pill({ children, tone }) {
  return <span className={`pill ${tone || ""}`.trim()}>{children}</span>;
}

function resultTone(code) {
  if (["SELECTED", "EVIDENCE_REUSED"].includes(code)) return "ok";
  if (["CONSENT_MISSING", "AGREEMENT_GAP", "NOT_ENTITLED", "NOT_SUBSCRIBED", "ACCESS_TYPE_INCOMPATIBLE", "ENTITLEMENT_SERVER_UNAVAILABLE"].includes(code)) return "warn";
  return "muted";
}

function SourceBadge({ source }) {
  if (!source) return null;
  return <span className="source-badge">{source}</span>;
}

export default function DiscoveryView({ trace, lens, onOpenAdvanced }) {
  const basic = lens !== "ADVANCED";
  const summary = trace?.discoverySummary || {};
  const matrix = trace?.discoveryMatrix || {};
  const pipeline = summary.pipeline || [];
  const finders = summary.finders || {};

  if (!trace?.discovery?.length) {
    return <p className="tiny">Discovery appears when the run completes.</p>;
  }

  return (
    <section className="section discovery-view">
      <p className="tiny">
        NetAware is narrowing the possible network capabilities for this application, Intent and context.
        Same engine and outcome in both lenses.
      </p>

      {basic ? (
        summary.nvStory ? (
          <NvBasicDiscovery trace={trace} summary={summary} pipeline={pipeline} onOpenAdvanced={onOpenAdvanced} />
        ) : (
          <BasicPipeline trace={trace} summary={summary} pipeline={pipeline} onOpenAdvanced={onOpenAdvanced} />
        )
      ) : (
        <AdvancedDiscovery
          trace={trace}
          summary={summary}
          matrix={matrix}
          finders={finders}
        />
      )}
          summary={summary}
          matrix={matrix}
          finders={finders}
        />
      )}
    </section>
  );
}

function NvBasicDiscovery({ trace, summary, pipeline, onOpenAdvanced }) {
  const outcome = trace.outcome || {};
  const selected = summary.selected || [];
  const filtered = (summary.filtered || []).filter((row) =>
    ["ACCESS_TYPE_INCOMPATIBLE", "ENTITLEMENT_SERVER_UNAVAILABLE", "NOT_REQUIRED"].includes(row.reasonCode)
  );
  return (
    <div>
      <NvPathVisual trace={trace} />
      <NvHonesty trace={trace} />
      <ol className="discovery-pipeline nv-basic-pipe">
        {(pipeline || []).map((step, idx) => (
          <li key={step.label}>
            {idx ? (
              <div className="pipeline-arrow" aria-hidden="true">
                ↓
              </div>
            ) : null}
            <div className="pipeline-step">
              <span>{step.label}</span>
            </div>
          </li>
        ))}
      </ol>
      <NvFinderStrip trace={trace} />
      <div className="grid-2 section">
        <article className="panel">
          <h3>What was filtered</h3>
          {filtered.length ? (
            <ul className="list compact">
              {filtered.map((row) => (
                <li key={`${row.label}-${row.reasonCode}`}>
                  <strong>{row.label}</strong>
                  <span className="tiny"> — {row.humanReason}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tiny">NV1 not required on cellular — simplest feasible path selected.</p>
          )}
        </article>
        <article className="panel">
          <h3>What NetAware selected</h3>
          {selected.length ? (
            <ul className="list compact">
              {selected.map((row) => (
                <li key={`${row.label}-${row.action}`}>
                  <strong>{row.label}</strong>
                  <span className="tiny"> · {row.operationId || row.label}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tiny">No feasible Number Verification path — capability unavailable.</p>
          )}
        </article>
      </div>
      <article className={`panel outcome ${outcome.outcome === "VERIFIED" ? "ready" : "gap"}`}>
        <h3>Number Verification outcome</h3>
        <p className="kicker">{outcome.outcome}</p>
        <p className="plus-line">{outcome.summary}</p>
      </article>
      <NetworkOpportunity trace={trace} />
      {onOpenAdvanced ? (
        <p className="tiny section">
          <button type="button" className="nav-link" onClick={onOpenAdvanced}>
            Path vs operation and candidate matrix (Advanced)
          </button>
        </p>
      ) : null}
    </div>
  );
}

function BasicPipeline({ trace, summary, pipeline, onOpenAdvanced }) {
  const purpose = trace.purpose || {};
  const request = summary.request || trace.request || {};
  const known = summary.knownFromConfiguration || trace.knownFromConfiguration || {};
  const filtered = summary.filtered || [];
  const selected = summary.selected || [];
  const outcome = summary.outcome || trace.outcome || {};
  const dynamic = summary.dynamicUsefulness;

  return (
    <div>
      <article className="panel">
        <h3>1 · Your application</h3>
        <dl className="dl">
          <dt>Enterprise</dt>
          <dd>{summary.enterprise}</dd>
          <dt>Application</dt>
          <dd>{summary.application}</dd>
          <dt>Business problem</dt>
          <dd>{known.rows ? "Keep existing systems. Ask for a business outcome." : "Configured onboarding context."}</dd>
          <dt>Intent sent</dt>
          <dd>{request.intent}</dd>
          <dt>Purpose</dt>
          <dd>{summary.purposeLabel || purpose.audienceLabel || purpose.label}</dd>
        </dl>
        {(known.rows || []).length ? (
          <ul className="list compact" style={{ marginTop: 10 }}>
            {known.rows
              .filter((row) => ["Enterprise", "Application", "Purpose", "Policy"].includes(row.label))
              .map((row) => (
                <li key={row.label}>
                  {row.label}: <strong>{row.value}</strong>
                </li>
              ))}
          </ul>
        ) : null}
      </article>

      <article className="panel" style={{ marginTop: 10 }}>
        <h3>2–5 · How NetAware narrowed the options</h3>
        <ol className="discovery-pipeline">
          {pipeline.map((step, idx) => (
            <li key={step.label}>
              {idx ? <div className="pipeline-arrow" aria-hidden="true">↓</div> : null}
              <div className="pipeline-step">
                <strong>{step.count}</strong>
                <span>{step.label}</span>
              </div>
            </li>
          ))}
        </ol>
        {(summary.layers || [])[1]?.items?.length ? (
          <p className="tiny" style={{ marginTop: 10 }}>
            Could help: {(summary.layers[1].items || []).join(" · ")}
          </p>
        ) : null}
      </article>

      {dynamic ? (
        <article className="panel" style={{ marginTop: 10 }}>
          <h3>Usefulness changed at runtime</h3>
          <p>
            {dynamic.capability}: initially <Pill tone="muted">{dynamic.initial.replaceAll("_", " ")}</Pill>
            {" → "}
            after breach <Pill tone="ok">{dynamic.afterBreach.replaceAll("_", " ")}</Pill>
          </p>
          <p className="tiny">{dynamic.note}</p>
        </article>
      ) : null}

      <div className="grid-2 section">
        <article className="panel">
          <h3>What was filtered</h3>
          {filtered.length ? (
            <ul className="list compact">
              {filtered.map((row) => (
                <li key={`${row.label}-${row.reasonCode}`}>
                  <strong>{row.label}</strong>
                  <span className="tiny"> — {row.humanReason}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tiny">Nothing filtered for this run.</p>
          )}
        </article>
        <article className="panel">
          <h3>What NetAware selected</h3>
          {selected.length ? (
            <ul className="list compact">
              {selected.map((row) => (
                <li key={`${row.label}-${row.action}`}>
                  <strong>{row.label}</strong>
                  <span className="tiny">
                    {" "}
                    · {row.action === "REUSE" ? "reused" : row.action === "CALL" ? "invoked" : row.action.toLowerCase()}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tiny">No network capability selected.</p>
          )}
        </article>
      </div>

      <article className="panel outcome ready">
        <h3>Business outcome</h3>
        <p className="kicker">{outcome.outcome}</p>
        <p className="plus-line">{outcome.summary}</p>
        <p className="tiny">
          {outcome.decisionOwner ? `Decision owner: ${outcome.decisionOwner}. ` : ""}
          NetAware invoked only what survived Discovery.
        </p>
      </article>

      {onOpenAdvanced ? (
        <p className="tiny section">
          <button type="button" className="nav-link" onClick={onOpenAdvanced}>
            Technical live flow and candidate matrix (Advanced)
          </button>
        </p>
      ) : null}
    </div>
  );
}

function AdvancedDiscovery({ trace, summary, matrix, finders }) {
  const purpose = trace.purpose || {};
  const dpv = purpose.dpv || {};
  const rows = matrix.rows || [];
  const columns = (matrix.columns || []).filter((col) => columnHasSignal(col.id, rows));
  const groups = matrix.columnGroups || [];

  return (
    <div>
      <section className="grid-2">
        <article className="panel">
          <h3>
            Configured / onboarding <SourceBadge source="ONBOARDING" />
          </h3>
          <dl className="dl">
            <dt>Enterprise</dt>
            <dd>{summary.enterprise}</dd>
            <dt>Application</dt>
            <dd>{summary.application}</dd>
            <dt>Agent</dt>
            <dd>{summary.agent}</dd>
            <dt>Intent</dt>
            <dd>
              <code>{summary.intent}</code>
            </dd>
            <dt>Purpose</dt>
            <dd>{summary.purposeLabel}</dd>
            <dt>DPV</dt>
            <dd>
              <code>{dpv.id || summary.purposeDpv}</code>
            </dd>
            <dt>Context</dt>
            <dd className="tiny">{dpv.context || summary.purposeContext}</dd>
          </dl>
        </article>
        <article className="panel">
          <h3>
            Runtime discovered / evaluated <SourceBadge source="RUNTIME" />
          </h3>
          <div className="finder-stack">
            <FinderBlock title="Telco Finder" source="RUNTIME" body={finders.telcoFinder} />
            <FinderBlock title="API Finder" source="RUNTIME" body={finders.apiFinder} />
            <FinderBlock title="Provider / route" source="RUNTIME" body={finders.providerRoute} />
          </div>
        </article>
      </section>

      <NvPathVsOperation trace={trace} lens="ADVANCED" />
      <article className="panel section">
        <h3>Candidate matrix</h3>
        <p className="tiny">Same trace as Basic. Subscription and entitlement are separate checks.</p>
        <div className="matrix-wrap">
          <table className="discovery-matrix">
            <thead>
              <tr>
                <th>Candidate</th>
                {columns.map((col) => (
                  <th key={col.id} title={groups.find((g) => g.id === col.group)?.label || col.group}>
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <strong>{row.label}</strong>
                    {row.moment ? <div className="tiny">{row.moment.replaceAll("_", " ")}</div> : null}
                    {row.operationId ? (
                      <div className="tiny">
                        <code>{row.operationId}</code>
                      </div>
                    ) : null}
                  </td>
                  {columns.map((col) => (
                    <td key={col.id}>
                      <MatrixCell column={col.id} row={row} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <div className="grid-2 section">
        <article className="panel">
          <h3>Filtered / skipped</h3>
          <ul className="list compact">
            {(summary.filtered || []).map((row) => (
              <li key={`${row.label}-${row.reasonCode}`}>
                <Pill tone={resultTone(row.reasonCode)}>{row.reasonCode}</Pill> {row.label}
                <div className="tiny">{row.humanReason}</div>
              </li>
            ))}
          </ul>
        </article>
        <article className="panel">
          <h3>Selected — where invoked or reused</h3>
          <ul className="list compact">
            {(summary.selected || []).map((row) => (
              <li key={`${row.label}-${row.action}`}>
                <Pill tone="ok">{row.reasonCode}</Pill> {row.label}
                <div className="tiny">
                  {row.action} · {row.operationId || "no invocation"} · {row.route || row.provider}
                </div>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </div>
  );
}

function FinderBlock({ title, source, body }) {
  if (!body) return null;
  return (
    <div className="finder-block">
      <div className="chips">
        <strong>{title}</strong>
        <SourceBadge source={source} />
      </div>
      <p className="tiny">{body.role}</p>
      {body.result ? <p>{body.result}</p> : null}
      {body.display ? <p>{body.display}</p> : null}
      {body.network && !body.result ? <p>{body.network}</p> : null}
      {body.type ? <p className="tiny">Route type · {body.type}</p> : null}
      {(body.results || []).length ? (
        <p className="tiny">{body.results.length} candidate operations evaluated</p>
      ) : null}
    </div>
  );
}

function columnHasSignal(id, rows) {
  if (["relevance", "subscription", "entitlement", "result", "telcoFinder", "apiFinder", "provider", "route"].includes(id)) {
    return true;
  }
  if (["accessType", "operatorNv1", "operatorNv2", "entitlementServer", "ts43Client", "simAvailable", "tokenPath", "pathResult", "operationResult"].includes(id)) {
    return rows.some((row) => {
      const value = cellValue(id, row);
      return value && value !== "—";
    });
  }
  return rows.some((row) => {
    const value = cellValue(id, row);
    return value && value !== "—" && value !== "ALLOWED" && value !== "NOT_REQUIRED";
  });
}

function cellValue(id, row) {
  if (id === "result") return row.reasonCode;
  if (id === "subscription") return row.subscription || row.checks?.subscription;
  if (id === "entitlement") return row.entitlement || row.checks?.entitlement;
  if (id === "consent") return row.consent || row.checks?.consent;
  return row.checks?.[id];
}

function MatrixCell({ column, row }) {
  const value = cellValue(column, row);
  if (column === "result") {
    return <Pill tone={resultTone(value)}>{String(value || "").replaceAll("_", " ")}</Pill>;
  }
  if (column === "subscription" || column === "entitlement") {
    return <span className={value === "NO" ? "warn-text" : ""}>{value || "—"}</span>;
  }
  if (column === "consent" && value === "MISSING") {
    return <span className="warn-text">MISSING</span>;
  }
  return <span>{value || "—"}</span>;
}

export function OutcomeView({ trace }) {
  const outcome = trace?.outcome || {};
  const summary = trace?.discoverySummary || {};
  return (
    <article className={`panel outcome ${outcome.outcome ? "ready" : ""}`}>
      <h3>Business outcome</h3>
      <p className="kicker">{outcome.outcome}</p>
      <p className="plus-line">{outcome.summary}</p>
      <p className="tiny">{outcome.decisionOwner ? `Decision owner: ${outcome.decisionOwner}` : ""}</p>
      {(summary.selected || []).length ? (
        <p className="tiny" style={{ marginTop: 8 }}>
          Selected: {summary.selected.map((r) => r.label).join(" · ")}
        </p>
      ) : null}
    </article>
  );
}

export function DiscoveryLink({ link }) {
  if (!link?.enterpriseId || !link?.useCaseId) return null;
  return (
    <a className="chip" href={href(`/demo/${link.enterpriseId}/${link.useCaseId}/run`)}>
      {link.label || "See Discovery"}
    </a>
  );
}
