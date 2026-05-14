const express = require('express');
const router  = express.Router();
const ctrl    = require('../controllers/directionActiviteController');
const { authMiddleware, checkRole } = require('../middleware/auth');

// ?activite=<id> pour filtrer par activité
router.get('/',       authMiddleware,                     ctrl.getAll);
router.get('/:id',    authMiddleware,                     ctrl.getOne);
router.post('/',      authMiddleware, checkRole('admin'), ctrl.create);
router.put('/:id',    authMiddleware, checkRole('admin'), ctrl.update);
router.delete('/:id', authMiddleware, checkRole('admin'), ctrl.remove);

module.exports = router;