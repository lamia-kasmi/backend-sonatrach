const mongoose = require('mongoose');

const departementActiviteSchema = new mongoose.Schema(
  {
    code: {
      type:      String,
      required:  [true, 'Le code est obligatoire'],
      unique:    true,
      uppercase: true,
      trim:      true,
    },
    nom: {
      type:     String,
      required: [true, 'Le nom est obligatoire'],
      trim:     true,
    },
    description: {
      type: String,
      trim: true,
    },
    directionActivite: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'DirectionActivite',
      required: [true, 'La direction activité parente est obligatoire'],
    },
    actif: {
      type:    Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('DepartementActivite', departementActiviteSchema);