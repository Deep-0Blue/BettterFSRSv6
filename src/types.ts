export interface BenchmarkSnapshot {
  logLoss: number | null;
  rmseBins: number | null;
  nItems: number | null;
  nRevlog: number | null;
}

export interface LogEntry {
  at: string;
  message: string;
}
