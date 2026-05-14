const express = require('express');
const router  = express.Router();
const ctrl    = require('../controllers/departementController');
const { authMiddleware, checkRole } = require('../middleware/auth');

router.get('/',                        authMiddleware, ctrl.getAll);
router.get('/direction/:directionId',  authMiddleware, ctrl.getByDirection);
router.get('/:id',                     authMiddleware, ctrl.getOne);
router.post('/',                       authMiddleware, checkRole('admin'), ctrl.create);
router.put('/:id',                     authMiddleware, checkRole('admin'), ctrl.update);
router.delete('/:id',                  authMiddleware, checkRole('admin'), ctrl.remove);

module.exports = router;