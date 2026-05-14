const mongoose = require('mongoose');

const directionCentraleSchema = new mongoose.Schema(
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

// Virtual : toutes les directions de cette direction centrale
directionCentraleSchema.virtual('directions', {
  ref:          'Direction',
  localField:   '_id',
  foreignField: 'directionCentrale',
});

module.exports = mongoose.model('DirectionCentrale', directionCentraleSchema);