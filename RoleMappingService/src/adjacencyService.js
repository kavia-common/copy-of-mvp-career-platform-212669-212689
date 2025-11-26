'use strict';

const fs = require('fs');
const path = require('path');

// Load precomputed adjacency data at startup
const dataPath = path.join(__dirname, '..', 'data', 'role_adjacency.json');
let adjacency = [];
try {
  const raw = fs.readFileSync(dataPath, 'utf8');
  const parsed = JSON.parse(raw);
  if (Array.isArray(parsed)) {
    adjacency = parsed;
  } else if (parsed && Array.isArray(parsed.adjacency)) {
    adjacency = parsed.adjacency;
  }
} catch (e) {
  // Fall back to empty adjacency on any error
  adjacency = [];
}

/**
 * Suggest target roles for a given currentRoleId from preloaded adjacency.
 * @param {string} currentRoleId
 * @param {number|undefined} topN
 * @returns {Array<{targetRoleId: string, weight: number, rationale?: string}>}
 */
function suggestTargetsFor(currentRoleId, topN) {
  const filtered = adjacency
    .filter(x => x && x.source_role_id === currentRoleId)
    .map(x => ({
      targetRoleId: String(x.target_role_id),
      weight: typeof x.weight === 'number' ? x.weight : Number(x.weight || 0),
      rationale: x.rationale || null,
    }))
    .sort((a, b) => (b.weight - a.weight));

  if (typeof topN === 'number' && Number.isFinite(topN) && topN > 0) {
    return filtered.slice(0, topN);
  }
  return filtered;
}

module.exports = {
  suggestTargetsFor,
};
