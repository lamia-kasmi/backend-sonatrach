const DirectionActivite = require('../models/DirectionActivite');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    const filter = req.query.activite ? { activite: req.query.activite } : {};
    const dirs = await DirectionActivite.find(filter)
      .populate('activite', 'code nom')
      .sort('code');
    send(res, 200, { success: true, count: dirs.length, data: dirs });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const dir = await DirectionActivite.findById(req.params.id)
      .populate('activite', 'code nom')
      .populate('departements');
    if (!dir) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, data: dir });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const dir = await DirectionActivite.create(req.body);
    send(res, 201, { success: true, data: dir });
  } catch (err) {
    const status = err.code === 11000 ? 409 : 400;
    send(res, status, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const dir = await DirectionActivite.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!dir) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, data: dir });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const dir = await DirectionActivite.findByIdAndDelete(req.params.id);
    if (!dir) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, message: 'Direction supprimée' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};