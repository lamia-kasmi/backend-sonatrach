// const express = require('express');
// const router  = express.Router();
// const ctrl    = require('../controllers/directionController');
// const { authMiddleware, checkRole } = require('../middleware/auth');

// router.get('/organigramme', authMiddleware, ctrl.getOrganigramme);
// router.get('/',             authMiddleware, ctrl.getAll);
// router.get('/:id',          authMiddleware, ctrl.getOne);
// router.post('/',            authMiddleware, checkRole('admin'), ctrl.create);
// router.put('/:id',          authMiddleware, checkRole('admin'), ctrl.update);
// router.delete('/:id',       authMiddleware, checkRole('admin'), ctrl.remove);

// module.exports = router;
const express = require('express');
const router  = express.Router();
const ctrl    = require('../controllers/directionController');
const { authMiddleware, checkRole } = require('../middleware/auth');

// ?directionCentrale=<id> pour filtrer
router.get('/',       authMiddleware,                     ctrl.getAll);
router.get('/:id',    authMiddleware,                     ctrl.getOne);
router.post('/',      authMiddleware, checkRole('admin'), ctrl.create);
router.put('/:id',    authMiddleware, checkRole('admin'), ctrl.update);
router.delete('/:id', authMiddleware, checkRole('admin'), ctrl.remove);

module.exports = router;