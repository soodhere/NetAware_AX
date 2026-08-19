import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import AxLoop, { HeroDemoCard } from "../components/AxLoop.jsx";
import { AxBrain, DxAxSplit } from "../visuals/VisualKit.jsx";

export default function Home() {
  const [demo, setDemo] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/demo")
      .then(setDemo)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  const product = demo?.product || {};
  const featured = demo?.featured || [];

  return (
    <div>
      <p className="kicker">From Developer Experience to Agentic Experience</p>
      <h1>
        <span>Keep your application.</span>
        <span>Express the outcome.</span>
      </h1>
      <p className="lede">
        {product.tagline ||
          "A simpler way for applications and agents to consume network capabilities."}
      </p>
      <p className="lede statement">NetAware connects enterprise demand to network supply.</p>
      <AxBrain compact />
      {product.discoveryLine ? <p className="lede">{product.discoveryLine}</p> : (
        <p className="lede">
          NetAware determines which network capabilities are relevant, allowed, available and useful — then invokes only what is needed.
        </p>
      )}
      <p className="lede">{product.support}</p>

      {(demo?.networkValueFraming?.headline || product.intentDefinition) && (
        <div className="banner intent-def">
          {demo?.networkValueFraming?.headline ||
            "Your application stays in its domain. Network APIs add what it cannot see, verify, or act on itself."}
        </div>
      )}

      <section className="section value-framing compact-home">
        <div className="value-ladder">
          <article className="panel domain-lane">
            <p className="kicker">My world</p>
            <p className="tiny">
              {demo?.networkValueFraming?.applicationLayer ||
                "Your application / domain APIs tell NetAware what is happening in the business."}
            </p>
          </article>
          <article className="panel network-lane">
            <p className="kicker">Network adds</p>
            <p className="tiny">
              {demo?.networkValueFraming?.networkLayer ||
                "Network APIs provide information, verification or actions the application does not have."}
            </p>
          </article>
          <article className="panel ax-lane">
            <p className="kicker">NetAware AX</p>
            <p className="tiny">
              {demo?.networkValueFraming?.axLayer ||
                "NetAware decides when complementary network capabilities can materially help achieve the Intent."}
            </p>
          </article>
        </div>
      </section>

      <section className="eq" aria-label="Product equation">
        <article>
          <span>Your world</span>
          <strong>Your applications & domain APIs</strong>
        </article>
        <i>+</i>
        <article>
          <span>Network capabilities</span>
          <strong>Complement, not replace</strong>
        </article>
        <i>+</i>
        <article>
          <span>Intent</span>
          <strong>The outcome you want</strong>
        </article>
        <i>=</i>
        <article className="result">
          <span>Agentic Experience</span>
          <strong>Business outcome returned</strong>
        </article>
      </section>

      <p className="tiny ax-principle">Simple outside. Sophisticated and fully traceable inside.</p>
      <DxAxSplit
        dxAx={{
          dx: [
            "Application developer",
            "discover APIs",
            "choose API",
            "understand operator differences",
            "implement flow",
            "handle availability",
            "invoke API",
          ],
          ax: [
            "Application / authorized agent",
            "express Intent",
            "NetAware discovers capabilities",
            "governs",
            "resolves operator / provider",
            "selects fulfillment",
            "CALL / REUSE / SKIP / FILTER",
            "business outcome",
          ],
          footer: "AX BUILDS ON NETWORK API DX. IT DOES NOT REPLACE IT.",
        }}
      />
      <AxLoop steps={product.axLoop} compact />

      <div className="hero-actions">
        <a href={href("/")}>
          <button className="primary" type="button">
            Start as Enterprise / Operator / Aggregator
          </button>
        </a>
        <a href={href("/demo")}>
          <button type="button">Start Demo</button>
        </a>
        <a href={href("/explore")}>
          <button type="button">Explore</button>
        </a>
      </div>

      {error ? <p className="err">{error}</p> : null}

      <section className="section">
        <h3>Live scenarios</h3>
        <p className="tiny">Fictional enterprises. Configured demo policy. No live operator coverage claimed.</p>
        <div className="grid-2 hero-grid">
          {featured.map((row) => (
            <HeroDemoCard key={row.storyId || row.heroUseCaseId || row.enterprise?.id} row={row} hrefFn={href} />
          ))}
        </div>
      </section>
    </div>
  );
}
