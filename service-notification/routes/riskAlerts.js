// routes/riskAlerts.js  ← REMPLACER l'ancien fichier par celui-ci
const express = require('express');
const router  = express.Router();
const { authMiddleware } = require('../middleware/auth');
const ctrl = require('../controllers/riskAlertController');

// Debug : loggue chaque requête reçue sur ce router
router.use((req, res, next) => {
    console.log(`[riskAlerts] ${req.method} ${req.originalUrl} | params:`, req.params, '| query:', req.query);
    next();
});

// Auth JWT (propagé depuis Django)
router.use(authMiddleware);

// ── IMPORTANT : /summary/:contrat_id AVANT /:id ──────────────
// POST   /                          ← CLM envoie une alerte
router.post('/', ctrl.createRiskAlert);

// GET    /                          ← liste filtrée
router.get('/', ctrl.getRiskAlerts);

// GET    /summary/:contrat_id       ← résumé contrat (DOIT être avant /:id)
router.get('/summary/:contrat_id', ctrl.getRiskAlertSummary);

// GET    /:id                       ← détail alerte
router.get('/:id', ctrl.getRiskAlert);

// PATCH  /:id                       ← changer statut
router.patch('/:id', ctrl.updateRiskAlertStatus);

module.exports = router;