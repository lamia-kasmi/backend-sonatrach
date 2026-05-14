const Activite = require('../models/Activite');

// GET /api/activites
exports.getAll = async (req, res) => {
  try {
    const data = await Activite.find().sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: data.length, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};

// GET /api/activites/:id
exports.getOne = async (req, res) => {
  try {
    const data = await Activite.findById(req.params.id);
    if (!data) return res.status(404).json({ success: false, message: 'Activité non trouvée' });
    res.status(200).json({ success: true, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};

// POST /api/activites
exports.create = async (req, res) => {
  try {
    const data = await Activite.create(req.body);
    res.status(201).json({ success: true, data });
  } catch (err) {
    if (err.code === 11000)
      return res.status(400).json({ success: false, message: 'Ce code existe déjà' });
    res.status(400).json({ success: false, message: err.message });
  }
};

// PUT /api/activites/:id
exports.update = async (req, res) => {
  try {
    const data = await Activite.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!data) return res.status(404).json({ success: false, message: 'Activité non trouvée' });
    res.status(200).json({ success: true, data });
  } catch (err) {
    if (err.code === 11000)
      return res.status(400).json({ success: false, message: 'Ce code existe déjà' });
    res.status(400).json({ success: false, message: err.message });
  }
};

// DELETE /api/activites/:id
exports.remove = async (req, res) => {
  try {
    const data = await Activite.findByIdAndDelete(req.params.id);
    if (!data) return res.status(404).json({ success: false, message: 'Activité non trouvée' });
    res.status(200).json({ success: true, message: 'Activité supprimée avec succès' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};