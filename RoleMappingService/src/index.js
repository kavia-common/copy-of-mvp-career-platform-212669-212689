'use strict';

const express = require('express');
const adjacencyRoutes = require('./routes/adjacencyRoutes');

const app = express();

// Parse JSON bodies
app.use(express.json());

// Health endpoint (unauthenticated)
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Mount adjacency routes (these enforce internal auth)
app.use('/', adjacencyRoutes);

// Start server
const PORT = parseInt(process.env.PORT, 10) || 4001;
app.listen(PORT, () => {
  console.log(`RoleMappingService listening on port ${PORT}`);
});
