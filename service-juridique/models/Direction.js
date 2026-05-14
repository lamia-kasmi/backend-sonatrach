// const mongoose = require('mongoose');

// const directionSchema = new mongoose.Schema(
//   {
//     code: {
//       type:      String,
//       required:  [true, 'Le code est obligatoire'],
//       unique:    true,
//       uppercase: true,
//       trim:      true,
//     },
//     nom: {
//       type:     String,
//       required: [true, 'Le nom est obligatoire'],
//       trim:     true,
//     },
//     description: {
//       type: String,
//       trim: true,
//     },
//     actif: {
//       type:    Boolean,
//       default: true,
//     },
//   },
//   {
//     timestamps: true,
//     toJSON:   { virtuals: true },
//     toObject: { virtuals: true },
//   }
// );

// // Virtual: tous les départements de cette direction
// directionSchema.virtual('departements', {
//   ref:          'Departement',
//   localField:   '_id',
//   foreignField: 'direction',
// });

// module.exports = mongoose.model('Direction', directionSchema);
const mongoose = require('mongoose');

const directionSchema = new mongoose.Schema(
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
    // ← nouveau : lien vers la direction centrale parente
    directionCentrale: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'DirectionCentrale',
      required: [true, 'La direction centrale parente est obligatoire'],
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

// Virtual : tous les départements de cette direction
directionSchema.virtual('departements', {
  ref:          'Departement',
  localField:   '_id',
  foreignField: 'direction',
});

module.exports = mongoose.model('Direction', directionSchema);