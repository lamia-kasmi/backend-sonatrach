const DepartementActivite = require('../models/DepartementActivite');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    const filter = req.query.directionActivite
      ? { directionActivite: req.query.directionActivite }
      : {};
    const deps = await DepartementActivite.find(filter)
      .populate('directionActivite', 'code nom')
      .sort('code');
    send(res, 200, { success: true, count: deps.length, data: deps });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const dep = await DepartementActivite.findById(req.params.id)
      .populate('directionActivite', 'code nom');
    if (!dep) return send(res, 404, { success: false, message: 'Département non trouvé' });
    send(res, 200, { success: true, data: dep });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const dep = await DepartementActivite.create(req.body);
    send(res, 201, { success: true, data: dep });
  } catch (err) {
    const status = err.code === 11000 ? 409 : 400;
    send(res, status, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const dep = await DepartementActivite.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!dep) return send(res, 404, { success: false, message: 'Département non trouvé' });
    send(res, 200, { success: true, data: dep });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const dep = await DepartementActivite.findByIdAndDelete(req.params.id);
    if (!dep) return send(res, 404, { success: false, message: 'Département non trouvé' });
    send(res, 200, { success: true, message: 'Département supprimé' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};