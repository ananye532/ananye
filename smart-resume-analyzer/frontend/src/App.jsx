import { useState } from "react";
import { api, getKey, setKey } from "./api.js";
import Results from "./Results.jsx";

const MAX_MB = 5;

function Register({ onDone }) {
  const [email, setEmail] = useState("");
  const [key, setNewKey] = useState(null);
  const [error, setError] = useState(null);
  const [existing, setExisting] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const user = await api.register(email);
      setNewKey(user.api_key);
    } catch (err) {
      setError(err.message);
    }
  }

  if (key)
    return (
      <section className="card">
        <h2>Your API key</h2>
        <p>Copy it now. Only a hash is stored on the server, so it can't be shown again.</p>
        <code className="key">{key}</code>
        <button onClick={() => (setKey(key), onDone())}>Continue</button>
      </section>
    );

  return (
    <section className="card">
      <h2>Get started</h2>
      <form onSubmit={submit} className="row">
        <label className="grow">
          Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <button type="submit">Create key</button>
      </form>
      <form onSubmit={(e) => (e.preventDefault(), setKey(existing.trim()), onDone())} className="row">
        <label className="grow">
          Already have a key?
          <input value={existing} onChange={(e) => setExisting(e.target.value)} autoComplete="off" />
        </label>
        <button type="submit" className="secondary" disabled={!existing.trim()}>
          Use key
        </button>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}

function AnalyzeForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  function pickFile(f) {
    setError(null);
    if (f && (!f.name.toLowerCase().endsWith(".pdf") || f.size > MAX_MB * 1024 * 1024)) {
      setError(`Please choose a PDF under ${MAX_MB} MB.`);
      return setFile(null);
    }
    setFile(f);
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const resume = await api.uploadResume(file);
      const job = await api.createJob(title, company, description);
      const analysis = await api.analyze(resume.id, job.id);
      onResult({ analysis, resume, job });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>1. Resume</h2>
      <label>
        PDF file (max {MAX_MB} MB, text-based, not scanned)
        <input type="file" accept="application/pdf,.pdf" required onChange={(e) => pickFile(e.target.files[0])} />
      </label>

      <h2>2. Job description</h2>
      <div className="row">
        <label className="grow">
          Job title
          <input required maxLength={200} value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label className="grow">
          Company (optional)
          <input maxLength={200} value={company} onChange={(e) => setCompany(e.target.value)} />
        </label>
      </div>
      <label>
        Paste the full job description
        <textarea
          required
          minLength={50}
          maxLength={20000}
          rows={10}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </label>
      <button type="submit" disabled={busy || !file}>
        {busy ? "Analyzing…" : "Analyze"}
      </button>
      {error && <p className="error" role="alert">{error}</p>}
    </form>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(Boolean(getKey()));
  const [result, setResult] = useState(null);

  async function deleteAll() {
    if (!confirm("Permanently delete your account and all uploaded resumes, jobs and analyses?")) return;
    try {
      await api.deleteAccount();
    } finally {
      setKey(null);
      setResult(null);
      setAuthed(false);
    }
  }

  return (
    <main>
      <header>
        <h1>Smart Resume Analyzer</h1>
        <p className="muted">
          A transparent comparison of your resume against a job description. The numbers measure text overlap. They
          do not predict whether you will be hired.
        </p>
        {authed && (
          <nav className="row">
            {result && (
              <button className="secondary" onClick={() => setResult(null)}>
                New analysis
              </button>
            )}
            <button className="secondary" onClick={() => (setKey(null), setAuthed(false), setResult(null))}>
              Sign out
            </button>
            <button className="danger" onClick={deleteAll}>
              Delete my data
            </button>
          </nav>
        )}
      </header>
      {!authed ? (
        <Register onDone={() => setAuthed(true)} />
      ) : result ? (
        <Results {...result} />
      ) : (
        <AnalyzeForm onResult={setResult} />
      )}
    </main>
  );
}
