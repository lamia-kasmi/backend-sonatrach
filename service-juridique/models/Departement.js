const mongoose = require('mongoose');

const departementSchema = new mongoose.Schema(
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
    direction: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'Direction',
      required: [true, 'La direction parente est obligatoire'],
    },
    actif: {
      type:    Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Departement', departementSchema);