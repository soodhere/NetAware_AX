import { href } from "../api.js";
import AxLoop from "../components/AxLoop.jsx";

export default function Close() {
  return (
    <div>
      <p className="kicker">Product reveal</p>
      <h1>
        <span>Your application stays</span>
        <span>in its domain</span>
      </h1>
      <p className="lede">
        Network APIs add information, verification and actions your application does not have itself. NetAware AX
        decides when they can help achieve the Intent.
      </p>

      <section className="eq section" aria-label="Complementarity equation">
        <article className="domain-lane">
          <span>Domain context</span>
          <strong>Your applications & APIs</strong>
        </article>
        <i>+</i>
        <article className="network-lane">
          <span>Network capabilities</span>
          <strong>Observe · Verify · Act</strong>
        </article>
        <i>+</i>
        <article className="ax-lane">
          <span>Governed AX</span>
          <strong>Intent + policy + autonomy</strong>
        </article>
        <i>=</i>
        <article className="result">
          <span>Business outcome</span>
          <strong>Returned to the application</strong>
        </article>
      </section>

      <p className="plus-line">
        Network APIs do not replace enterprise or domain APIs. They complement them when they can materially help.
      </p>

      <AxLoop />

      <section className="grid-2 section">
        <article className="panel">
          <h3>What NetAware does</h3>
          <ul className="list">
            <li>Understands context already configured at onboarding</li>
            <li>Applies governance — purpose, policy, consent, autonomy</li>
            <li>Discovers capabilities and routes across providers</li>
            <li>Plans minimum sufficient network evidence or action</li>
            <li>Acts, replans, and verifies when needed</li>
          </ul>
        </article>
        <article className="panel">
          <h3>Network capability roles</h3>
          <ul className="list">
            <li>
              <strong>Observe</strong> — information the application does not independently have
            </li>
            <li>
              <strong>Verify</strong> — independent network or operator assertions
            </li>
            <li>
              <strong>Act</strong> — network actions that can change conditions
            </li>
          </ul>
        </article>
      </section>

      <section className="grid-2 section">
        <article className="panel">
          <h3>Coexistence</h3>
          <p className="tiny">Intent does not replace direct APIs.</p>
          <ul className="list">
            <li>
              <strong>Direct API</strong> — call a known operation
            </li>
            <li>
              <strong>Authored / composed API</strong> — your orchestration
            </li>
            <li>
              <strong>Network Intent / AX</strong> — express outcome; NetAware handles network complexity
            </li>
          </ul>
        </article>
        <article className="panel">
          <h3>Prototype honesty</h3>
          <p className="tiny">
            Simulated enterprises · configured demo policy · topology-neutral · PRODUCT / AX PROTOTYPE only
          </p>
        </article>
      </section>

      <section className="eq section" aria-label="Catalog leverage">
        <article>
          <span>13 families</span>
          <strong>Current-focus catalog</strong>
        </article>
        <i>→</i>
        <article>
          <span>Many capabilities</span>
          <strong>16 mapped</strong>
        </article>
        <i>→</i>
        <article className="result">
          <span>Many outcomes</span>
          <strong>Many domains</strong>
        </article>
      </section>
      <p className="plus-line">Small practical catalog. Many business outcomes.</p>

      <div className="hero-actions">
        <a href={href("/explore/catalog")}>
          <button className="primary" type="button">
            Explore catalog
          </button>
        </a>
        <a href={href("/demo")}>
          <button type="button">Run another scenario</button>
        </a>
      </div>
    </div>
  );
}
