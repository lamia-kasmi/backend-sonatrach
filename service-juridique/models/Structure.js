const mongoose = require('mongoose');

const structureSchema = new mongoose.Schema(
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
    type: {
      type:     String,
      enum:     ['direction', 'departement'],
      required: [true, 'Le type est obligatoire'],
    },
    division: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'Division',
      required: [true, 'La division parente est obligatoire'],
    },
    actif: {
      type:    Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Structure', structureSchema);