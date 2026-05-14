const express = require('express');
const router  = express.Router();
const ctrl    = require('../controllers/structureController');
const { authMiddleware, checkRole } = require('../middleware/auth');

// ?division=<id>&type=direction|departement
router.get('/',       authMiddleware,                     ctrl.getAll);
router.get('/:id',    authMiddleware,                     ctrl.getOne);
router.post('/',      authMiddleware, checkRole('admin'), ctrl.create);
router.put('/:id',    authMiddleware, checkRole('admin'), ctrl.update);
router.delete('/:id', authMiddleware, checkRole('admin'), ctrl.remove);

module.exports = router;