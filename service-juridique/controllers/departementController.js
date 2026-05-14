const Departement = require('../models/Departement');
const Direction   = require('../models/Direction');

// GET /juridique/departements  (filtre ?direction=id)
exports.getAll = async (req, res) => {
  try {
    const filter = { actif: true };
    if (req.query.direction) filter.direction = req.query.direction;
    const data = await Departement.find(filter).populate('direction', 'nom code');
    res.status(200).json({ success: true, count: data.length, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};

// GET /juridique/departements/:id
exports.getOne = async (req, res) => {
  try {
    const data = await Departement.findById(req.params.id).populate('direction', 'nom code');
    if (!data) return res.status(404).json({ success: false, message: 'Département non trouvé' });
    res.status(200).json({ success: true, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};

// GET /juridique/departements/direction/:directionId
exports.getByDirection = async (req, res) => {
  try {
    const direction = await Direction.findById(req.params.directionId);
    if (!direction) return res.status(404).json({ success: false, message: 'Direction non trouvée' });

    const data = await Departement.find({ direction: req.params.directionId, actif: true });
    res.status(200).json({
      success: true,
      count:   data.length,
      direction: { id: direction._id, nom: direction.nom, code: direction.code },
      data,
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};

// POST /juridique/departements
exports.create = async (req, res) => {
  try {
    const direction = await Direction.findById(req.body.direction);
    if (!direction)
      return res.status(404).json({ success: false, message: 'Direction parente non trouvée' });

    const data = await Departement.create(req.body);
    res.status(201).json({ success: true, data });
  } catch (err) {
    if (err.code === 11000)
      return res.status(400).json({ success: false, message: 'Ce code existe déjà' });
    res.status(400).json({ success: false, message: err.message });
  }
};

// PUT /juridique/departements/:id
exports.update = async (req, res) => {
  try {
    const data = await Departement.findByIdAndUpdate(req.params.id, req.body, {
      new: true, runValidators: true,
    }).populate('direction', 'nom code');
    if (!data) return res.status(404).json({ success: false, message: 'Département non trouvé' });
    res.status(200).json({ success: true, data });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
};

// DELETE /juridique/departements/:id  (soft delete)
exports.remove = async (req, res) => {
  try {
    const data = await Departement.findByIdAndUpdate(
      req.params.id, { actif: false }, { new: true }
    );
    if (!data) return res.status(404).json({ success: false, message: 'Département non trouvé' });
    res.status(200).json({ success: true, message: 'Département désactivé' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
};