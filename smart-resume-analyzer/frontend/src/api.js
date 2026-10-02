// Thin wrapper around the backend REST API. The API key lives in sessionStorage,
// so it is cleared when the browser tab closes.
const KEY = "sra_api_key";

export const getKey = () => {
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
};
export const setKey = (k) => {
  try {
    k ? sessionStorage.setItem(KEY, k) : sessionStorage.removeItem(KEY);
  } catch {
    /* storage unavailable: key lives only in memory for this page */
  }
};

async function request(path, { method = "GET", json, form, raw } = {}) {
  const headers = {};
  const key = getKey();
  if (key) headers["X-API-Key"] = key;
  let body;
  if (json) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form) {
    body = form;
  }
  const res = await fetch(`/api${path}`, { method, headers, body });
  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      const d = data.detail;
      if (typeof d === "string") message = d;
      else if (d?.message) message = d.message;
      else if (Array.isArray(d)) message = d.map((e) => e.msg).join("; ");
    } catch {
      /* non-JSON error body */
    }
    throw new Error(message);
  }
  if (raw) return res;
  return res.status === 204 ? null : res.json();
}

export const api = {
  config: () => request("/config"),
  register: (email) => request("/users", { method: "POST", json: { email } }),
  deleteAccount: () => request("/users/me", { method: "DELETE" }),
  uploadResume: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/resumes", { method: "POST", form });
  },
  createJob: (title, company, description) =>
    request("/jobs", { method: "POST", json: { title, company: company || null, description } }),
  analyze: (resume_id, job_id) => request("/analyses", { method: "POST", json: { resume_id, job_id } }),
  async downloadReport(id, format) {
    const res = await request(`/analyses/${id}/report?format=${format}`, { raw: true });
    const url = URL.createObjectURL(await res.blob());
    const a = Object.assign(document.createElement("a"), { href: url, download: `resume-analysis.${format}` });
    document.body.appendChild(a); // Firefox needs the link in the DOM
    a.click();
    a.remove();
    // Revoking synchronously can cancel the download in browsers that start it on a later task.
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },
};
