'use strict';

const service = require('../adjacencyService');

async function suggest(req, res) {
  try {
    const { currentRoleId, topN } = req.body || {};
    if (!currentRoleId || typeof currentRoleId !== 'string' || currentRoleId.trim().length === 0) {
      return res.status(400).json({ error: 'currentRoleId is required and must be a non-empty string' });
    }
    const n = Number.isFinite(topN) ? Number(topN) : undefined;
    const suggestions = service.suggestTargetsFor(currentRoleId, n);
    return res.json({
      currentRoleId,
      suggestions
    });
  } catch (err) {
    // Avoid leaking internals
    return res.status(500).json({ error: 'Internal server error' });
  }
}

module.exports = {
  suggest,
};
