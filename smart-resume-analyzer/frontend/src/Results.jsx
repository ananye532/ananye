import { useState } from "react";
import { api } from "./api.js";

const pct = (v) => (v === null || v === undefined ? "n/a" : `${Math.round(v * 100)}%`);

function Metric({ label, value, detail, definition }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {detail && <div className="muted">{detail}</div>}
      <p className="definition">{definition}</p>
    </div>
  );
}

function Chips({ items, kind }) {
  if (!items.length) return <p className="muted">None</p>;
  return (
    <ul className="chips">
      {items.map((s) => (
        <li key={s} className={`chip ${kind}`}>
          {s}
        </li>
      ))}
    </ul>
  );
}

export default function Results({ analysis, resume }) {
  const r = analysis.result;
  const m = r.metrics;
  const [error, setError] = useState(null);

  const download = (fmt) => api.downloadReport(analysis.id, fmt).catch((e) => setError(e.message));

  return (
    <>
      <section className="card notice" role="note">
        <strong>How to read this:</strong> {r.disclaimer}
      </section>

      <section className="card">
        <h2>Metrics</h2>
        <p className="muted">
          Shown separately on purpose. Each measures something different, and none of them is a hiring score.
        </p>
        <div className="metrics">
          <Metric
            label="Skill coverage"
            value={pct(m.skill_coverage.value)}
            detail={`${m.skill_coverage.matched_count} of ${m.skill_coverage.required_count} JD skills`}
            definition={m.skill_coverage.definition}
          />
          <Metric
            label="Keyword coverage"
            value={pct(m.keyword_coverage.value)}
            detail={`${m.keyword_coverage.present_count} of ${m.keyword_coverage.total} top JD terms`}
            definition={m.keyword_coverage.definition}
          />
          <Metric
            label="TF-IDF cosine similarity"
            value={m.cosine_similarity.value.toFixed(2)}
            definition={m.cosine_similarity.definition}
          />
        </div>
      </section>

      <section className="card">
        <h2>Skills</h2>
        <h3>Missing from your resume</h3>
        {Object.keys(r.skills.missing_by_category).length ? (
          Object.entries(r.skills.missing_by_category)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([cat, names]) => (
            <div key={cat}>
              <div className="muted small">{cat}</div>
              <Chips items={names} kind="missing" />
            </div>
          ))
        ) : (
          <p className="muted">None</p>
        )}
        <h3>Matched</h3>
        <Chips items={r.skills.matched} kind="matched" />
        <h3>In your resume but not in the job description</h3>
        <Chips items={r.skills.resume_only} kind="neutral" />
      </section>

      <section className="card">
        <h2>Suggestions</h2>
        {r.suggestions.length ? (
          <ul className="suggestions">
            {r.suggestions.map((s, i) => (
              <li key={i} className={`sev-${s.severity}`}>
                <span className="badge">{s.severity}</span> {s.message} <span className="muted small">rule: {s.rule}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No rule-based suggestions.</p>
        )}
      </section>

      <section className="card">
        <h2>Top job-description keywords</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Term</th>
                <th>TF-IDF weight</th>
                <th>In resume</th>
              </tr>
            </thead>
            <tbody>
              {r.keywords.job_top.map((k) => (
                <tr key={k.term}>
                  <td>{k.term}</td>
                  <td>
                    <span className="bar" style={{ width: `${Math.round(k.weight * 120)}px` }} /> {k.weight.toFixed(2)}
                  </td>
                  <td>{k.in_resume ? "yes" : "no"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h2>Resume structure</h2>
        <p>
          {resume.filename}: {resume.page_count} page(s), {resume.word_count} words extracted.
        </p>
        <ul>
          {r.sections.detected.map((s) => (
            <li key={s.name}>
              <strong>{s.name}</strong> <span className="muted">(“{s.heading}”, {s.word_count} words)</span>
            </li>
          ))}
        </ul>
        {r.sections.missing_recommended.length > 0 && (
          <p className="warn">Not detected: {r.sections.missing_recommended.join(", ")}</p>
        )}
        <p className="muted small">
          Contact fields found:{" "}
          {Object.entries(r.sections.contact)
            .map(([k, v]) => `${k} ${v ? "✓" : "✗"}`)
            .join(" · ")}
        </p>
        <details>
          <summary>Named entities (informational, may be mislabelled)</summary>
          {Object.entries(r.entities).map(([k, v]) => (
            <p key={k}>
              <strong>{k}:</strong> {v.join(", ") || "none"}
            </p>
          ))}
        </details>
        <details>
          <summary>Extracted text preview</summary>
          <pre>{resume.text_preview}</pre>
        </details>
      </section>

      <section className="card">
        <h2>Limitations</h2>
        <ul>
          {r.limitations.map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
      </section>

      <section className="card row">
        <button onClick={() => download("md")}>Download report (Markdown)</button>
        <button className="secondary" onClick={() => download("json")}>
          Download report (JSON)
        </button>
        {error && <p className="error">{error}</p>}
      </section>
    </>
  );
}
