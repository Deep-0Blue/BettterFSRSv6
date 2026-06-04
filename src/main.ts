import type { BenchmarkSnapshot, LogEntry } from "./types";

const root = document.querySelector<HTMLDivElement>("#app");
if (!root) throw new Error("Missing #app root");
const app: HTMLDivElement = root;

const state: {
  collectionName: string | null;
  metrics: BenchmarkSnapshot;
  logs: LogEntry[];
} = {
  collectionName: null,
  metrics: {
    logLoss: null,
    rmseBins: null,
    nItems: null,
    nRevlog: null,
  },
  logs: [{ at: nowLabel(), message: "Dashboard ready on localhost." }],
};

function nowLabel(): string {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addLog(message: string): void {
  state.logs.unshift({ at: nowLabel(), message });
  if (state.logs.length > 12) state.logs.pop();
  render();
}

function formatMetric(value: number | null, digits = 4): string {
  return value === null ? "—" : value.toFixed(digits);
}

function render(): void {
  const { metrics, collectionName, logs } = state;

  app.innerHTML = `
    <header class="dashboard-header clay-panel">
      <h1>BettterFSRS</h1>
      <p class="subtitle">Clay studio for FSRS-6 benchmarks</p>
      <span class="status-pill">localhost · port 5173</span>
    </header>

    <section class="metrics-grid" aria-label="Metrics">
      ${metricCard("log loss", formatMetric(metrics.logLoss), "recency-weighted BCE")}
      ${metricCard("rmse bins", formatMetric(metrics.rmseBins), "calibration curve")}
      ${metricCard("fsrs items", metrics.nItems?.toLocaleString() ?? "—", "training rows")}
      ${metricCard("revlog rows", metrics.nRevlog?.toLocaleString() ?? "—", "parsed reviews")}
    </section>

    <div class="workspace">
      <section class="clay-panel">
        <h2 class="section-title">Collection</h2>
        <div class="clay-inset upload-zone" id="drop-zone" tabindex="0" role="button" aria-label="Upload Anki collection">
          <strong>Drop collection.anki21</strong>
          <p>or click to browse</p>
          <div class="filename">${collectionName ?? "No file selected"}</div>
        </div>
        <input type="file" id="file-input" accept=".anki21,.anki2,.db" hidden />
        <div class="actions">
          <button type="button" class="clay-button" data-action="benchmark">Run baseline</button>
          <button type="button" class="clay-button clay-button--ghost" data-action="fit">Fit BetterFSRS</button>
        </div>
      </section>

      <section class="clay-panel">
        <h2 class="section-title">Activity</h2>
        <ul class="clay-inset log-feed" id="log-feed">
          ${logs.map((e) => `<li><span class="time">${e.at}</span>${escapeHtml(e.message)}</li>`).join("")}
        </ul>
      </section>
    </div>

    <footer class="dashboard-footer">
      Times New Roman · warm clay UI · wire to Python CLI when ready
    </footer>
  `;

  bindEvents();
}

function metricCard(label: string, value: string, hint: string): string {
  return `
    <article class="clay-panel metric-card">
      <span class="label">${label}</span>
      <span class="value">${value}</span>
      <span class="hint">${hint}</span>
    </article>
  `;
}

function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function bindEvents(): void {
  const dropZone = document.querySelector<HTMLDivElement>("#drop-zone");
  const fileInput = document.querySelector<HTMLInputElement>("#file-input");

  dropZone?.addEventListener("click", () => fileInput?.click());

  dropZone?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput?.click();
    }
  });

  fileInput?.addEventListener("change", () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    state.collectionName = file.name;
    state.metrics = { logLoss: null, rmseBins: null, nItems: null, nRevlog: null };
    addLog(`Loaded “${file.name}” (${(file.size / 1024).toFixed(1)} KB).`);
  });

  dropZone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone?.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

  dropZone?.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer?.files[0];
    if (!file) return;
    state.collectionName = file.name;
    addLog(`Dropped “${file.name}”.`);
  });

  document.querySelectorAll<HTMLButtonElement>("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action;
      if (!state.collectionName) {
        addLog("Select a collection file first.");
        return;
      }
      if (action === "benchmark") simulateBenchmark();
      if (action === "fit") simulateFit();
    });
  });
}

/** Placeholder until API bridge to Python benchmark exists. */
function simulateBenchmark(): void {
  addLog("Running baseline FSRS-6 (demo values)…");
  const nRevlog = 12_400 + Math.floor(Math.random() * 2000);
  const nItems = Math.floor(nRevlog * 0.58);
  state.metrics = {
    logLoss: 0.198 + Math.random() * 0.02,
    rmseBins: 0.026 + Math.random() * 0.008,
    nItems,
    nRevlog,
  };
  addLog(`Baseline done — ${nItems.toLocaleString()} FSRS items.`);
}

function simulateFit(): void {
  if (state.metrics.logLoss === null) {
    addLog("Run baseline before fitting BetterFSRS6.");
    return;
  }
  addLog("Fitting personalized weights (demo)…");
  state.metrics = {
    ...state.metrics,
    logLoss: Math.max(0.17, state.metrics.logLoss - 0.012 - Math.random() * 0.01),
    rmseBins: Math.max(0.02, (state.metrics.rmseBins ?? 0.03) - 0.004),
  };
  addLog("BetterFSRS6 fit complete (demo).");
}

render();
