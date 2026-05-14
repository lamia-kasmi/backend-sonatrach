const Division = require('../models/Division');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    const filter = req.query.activite ? { activite: req.query.activite } : {};
    const divs = await Division.find(filter)
      .populate('activite', 'code nom')
      .sort('code');
    send(res, 200, { success: true, count: divs.length, data: divs });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const div = await Division.findById(req.params.id)
      .populate('activite', 'code nom')
      .populate({ path: 'structures', match: { actif: true } });
    if (!div) return send(res, 404, { success: false, message: 'Division non trouvée' });
    send(res, 200, { success: true, data: div });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const div = await Division.create(req.body);
    send(res, 201, { success: true, data: div });
  } catch (err) {
    const status = err.code === 11000 ? 409 : 400;
    send(res, status, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const div = await Division.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!div) return send(res, 404, { success: false, message: 'Division non trouvée' });
    send(res, 200, { success: true, data: div });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const div = await Division.findByIdAndDelete(req.params.id);
    if (!div) return send(res, 404, { success: false, message: 'Division non trouvée' });
    send(res, 200, { success: true, message: 'Division supprimée' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};