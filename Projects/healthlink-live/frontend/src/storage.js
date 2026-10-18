// UI convenience only. PostgreSQL remains the source of truth.
export function read(key, fallback = null) {
  try { return JSON.parse(sessionStorage.getItem(key)) ?? fallback; }
  catch { return fallback; }
}
export function write(key, value) {
  try { sessionStorage.setItem(key, JSON.stringify(value)); return true; }
  catch { return false; }
}
export const proposalKey = id => `healthlink.proposal.${id}`;
