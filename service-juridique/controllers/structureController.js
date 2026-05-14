const Structure = require('../models/Structure');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    const filter = {};
    if (req.query.division) filter.division = req.query.division;
    if (req.query.type)     filter.type     = req.query.type;      // 'direction' | 'departement'

    const structs = await Structure.find(filter)
      .populate('division', 'code nom')
      .sort('code');
    send(res, 200, { success: true, count: structs.length, data: structs });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const struct = await Structure.findById(req.params.id)
      .populate('division', 'code nom');
    if (!struct) return send(res, 404, { success: false, message: 'Structure non trouvée' });
    send(res, 200, { success: true, data: struct });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const struct = await Structure.create(req.body);
    send(res, 201, { success: true, data: struct });
  } catch (err) {
    const status = err.code === 11000 ? 409 : 400;
    send(res, status, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const struct = await Structure.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!struct) return send(res, 404, { success: false, message: 'Structure non trouvée' });
    send(res, 200, { success: true, data: struct });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const struct = await Structure.findByIdAndDelete(req.params.id);
    if (!struct) return send(res, 404, { success: false, message: 'Structure non trouvée' });
    send(res, 200, { success: true, message: 'Structure supprimée' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};