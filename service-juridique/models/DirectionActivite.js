const mongoose = require('mongoose');

const directionActiviteSchema = new mongoose.Schema(
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
    activite: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'Activite',
      required: [true, "L'activité parente est obligatoire"],
    },
    actif: {
      type:    Boolean,
      default: true,
    },
  },
  {
    timestamps: true,
    toJSON:   { virtuals: true },
    toObject: { virtuals: true },
  }
);

directionActiviteSchema.virtual('departements', {
  ref:          'DepartementActivite',
  localField:   '_id',
  foreignField: 'directionActivite',
});

module.exports = mongoose.model('DirectionActivite', directionActiviteSchema);