// const Direction   = require('../models/Direction');
// const Departement = require('../models/Departement');

// // GET /juridique/directions
// exports.getAll = async (req, res) => {
//   try {
//     const data = await Direction.find({ actif: true }).populate({
//       path:  'departements',
//       match: { actif: true },
//     });
//     res.status(200).json({ success: true, count: data.length, data });
//   } catch (err) {
//     res.status(500).json({ success: false, message: err.message });
//   }
// };

// // GET /juridique/directions/:id
// exports.getOne = async (req, res) => {
//   try {
//     const data = await Direction.findById(req.params.id).populate({
//       path:  'departements',
//       match: { actif: true },
//     });
//     if (!data) return res.status(404).json({ success: false, message: 'Direction non trouvée' });
//     res.status(200).json({ success: true, data });
//   } catch (err) {
//     res.status(500).json({ success: false, message: err.message });
//   }
// };

// // POST /juridique/directions
// exports.create = async (req, res) => {
//   try {
//     const data = await Direction.create(req.body);
//     res.status(201).json({ success: true, data });
//   } catch (err) {
//     if (err.code === 11000)
//       return res.status(400).json({ success: false, message: 'Ce code existe déjà' });
//     res.status(400).json({ success: false, message: err.message });
//   }
// };

// // PUT /juridique/directions/:id
// exports.update = async (req, res) => {
//   try {
//     const data = await Direction.findByIdAndUpdate(req.params.id, req.body, {
//       new: true, runValidators: true,
//     });
//     if (!data) return res.status(404).json({ success: false, message: 'Direction non trouvée' });
//     res.status(200).json({ success: true, data });
//   } catch (err) {
//     res.status(400).json({ success: false, message: err.message });
//   }
// };

// // DELETE /juridique/directions/:id  (soft delete)
// exports.remove = async (req, res) => {
//   try {
//     const data = await Direction.findByIdAndUpdate(
//       req.params.id, { actif: false }, { new: true }
//     );
//     if (!data) return res.status(404).json({ success: false, message: 'Direction non trouvée' });
//     res.status(200).json({ success: true, message: 'Direction désactivée' });
//   } catch (err) {
//     res.status(500).json({ success: false, message: err.message });
//   }
// };

// // GET /juridique/organigramme
// exports.getOrganigramme = async (req, res) => {
//   try {
//     const directions = await Direction.find({ actif: true }).populate({
//       path:  'departements',
//       match: { actif: true },
//     });

//     res.status(200).json({
//       success: true,
//       data: {
//         nom:        'Direction Centrale Juridique',
//         directions,
//       },
//     });
//   } catch (err) {
//     res.status(500).json({ success: false, message: err.message });
//   }
// };
const Direction = require('../models/Direction');

const send = (res, status, data) => res.status(status).json(data);

exports.getAll = async (req, res) => {
  try {
    // ?directionCentrale=<id>  pour filtrer
    const filter = req.query.directionCentrale
      ? { directionCentrale: req.query.directionCentrale }
      : {};
    const items = await Direction.find(filter)
      .populate('directionCentrale', 'code nom')
      .sort('code');
    send(res, 200, { success: true, count: items.length, data: items });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.getOne = async (req, res) => {
  try {
    const item = await Direction.findById(req.params.id)
      .populate('directionCentrale', 'code nom')
      .populate({ path: 'departements', match: { actif: true } });
    if (!item) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, data: item });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};

exports.create = async (req, res) => {
  try {
    const item = await Direction.create(req.body);
    send(res, 201, { success: true, data: item });
  } catch (err) {
    send(res, err.code === 11000 ? 409 : 400, { success: false, message: err.message });
  }
};

exports.update = async (req, res) => {
  try {
    const item = await Direction.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    });
    if (!item) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, data: item });
  } catch (err) {
    send(res, 400, { success: false, message: err.message });
  }
};

exports.remove = async (req, res) => {
  try {
    const item = await Direction.findByIdAndDelete(req.params.id);
    if (!item) return send(res, 404, { success: false, message: 'Direction non trouvée' });
    send(res, 200, { success: true, message: 'Direction supprimée' });
  } catch (err) {
    send(res, 500, { success: false, message: err.message });
  }
};