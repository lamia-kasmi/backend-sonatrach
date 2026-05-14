const DirectionCentrale = require('../models/DirectionCentrale');
const Direction         = require('../models/Direction');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    const items = await DirectionCentrale.find().sort('code');
    send(res, 200, { success: true, count: items.length, data: items });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const item = await DirectionCentrale.findById(req.params.id)
      .populate({
        path:     'directions',
        match:    { actif: true },
        populate: { path: 'departements', match: { actif: true } },
      });
    if (!item) return send(res, 404, { success: false, message: 'Direction centrale non trouvée' });
    send(res, 200, { success: true, data: item });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

// Organigramme complet d'une direction centrale
exports.getOrganigramme = async (req, res) => {
  try {
    const item = await DirectionCentrale.findById(req.params.id);
    if (!item) return send(res, 404, { success: false, message: 'Direction centrale non trouvée' });

    const directions = await Direction.find({ directionCentrale: item._id, actif: true })
      .populate({ path: 'departements', match: { actif: true } })
      .sort('code');

    send(res, 200, { success: true, data: { directionCentrale: item, directions } });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const item = await DirectionCentrale.create(req.body);
    send(res, 201, { success: true, data: item });
  } catch (err) {
    send(res, err.code === 11000 ? 409 : 400, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const item = await DirectionCentrale.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!item) return send(res, 404, { success: false, message: 'Direction centrale non trouvée' });
    send(res, 200, { success: true, data: item });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const item = await DirectionCentrale.findByIdAndDelete(req.params.id);
    if (!item) return send(res, 404, { success: false, message: 'Direction centrale non trouvée' });
    send(res, 200, { success: true, message: 'Direction centrale supprimée' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};