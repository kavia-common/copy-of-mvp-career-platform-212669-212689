'use strict';

const express = require('express');
const controller = require('../controllers/adjacencyController');

const router = express.Router();

// Simple internal auth middleware using X-Internal-Token header
function internalAuth(req, res, next) {
  const configuredToken = process.env.INTERNAL_TOKEN;
  if (!configuredToken) {
    return res.status(500).json({ error: 'INTERNAL_TOKEN is not configured on the service' });
  }
  const headerToken = req.header('X-Internal-Token') || req.header('x-internal-token');
  if (!headerToken || headerToken !== configuredToken) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  return next();
}

// POST /adjacency/suggest
router.post('/adjacency/suggest', internalAuth, controller.suggest);

module.exports = router;
