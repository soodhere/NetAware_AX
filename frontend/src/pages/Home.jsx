import { useEffect, useState } from "react";
import { api, href } from "../api.js";
import AxLoop, { HeroDemoCard } from "../components/AxLoop.jsx";

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
      <p className="lede">{product.support}</p>

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
      <AxLoop steps={product.axLoop} compact />

      <div className="hero-actions">
        <a href={href("/demo")}>
          <button className="primary" type="button">
            Start Demo
          </button>
        </a>
        <a href={href("/explore")}>
          <button type="button">Explore</button>
        </a>
      </div>

      {error ? <p className="err">{error}</p> : null}

      <section className="section">
        <h3>Four live scenarios</h3>
        <p className="tiny">Fictional enterprises. Configured demo policy. No live operator coverage claimed.</p>
        <div className="grid-2 hero-grid">
          {featured.map((row) => (
            <HeroDemoCard key={row.enterprise?.id || row.id} row={row} hrefFn={href} />
          ))}
        </div>
      </section>
    </div>
  );
}
