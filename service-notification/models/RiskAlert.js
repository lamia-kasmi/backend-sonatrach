// models/RiskAlert.js
const mongoose = require('mongoose');

/**
 * Collection des alertes risque retard émises par le service CLM.
 * Chaque document correspond à une occurrence d'un risque (code R-xx)
 * sur un contrat donné.
 *
 * La logique d'escalade est calculée à la lecture via occurrence_count :
 *   1ère occurrence → warning    → notifier chef département
 *   2ème occurrence → alert      → notifier directeur direction
 *   3ème+           → escalade   → notifier directeur activité
 */
const RiskAlertSchema = new mongoose.Schema(
    {
        contrat_id: {
            type:     Number,
            required: true,
            index:    true,
        },

        code: {
            type:     String,
            required: true,
            trim:     true,
            // ex: 'R-07', 'R-08'
        },

        type: {
            type:    String,
            enum:    ['retard', 'imprecision', 'different'],
            default: 'retard',
            index:   true,
        },

        description: {
            type:     String,
            required: true,
        },

        severite: {
            type: String,
            enum: ['faible', 'moyen', 'eleve', 'critique'],
        },

        article_ref: {
            type:    String,
            default: '',
        },

        suggestion: {
            type:    String,
            default: '',
        },

        // Utilisateur Django qui a déclenché l'analyse
        created_by_id: {
            type:    String,
            default: null,
        },

        created_by_name: {
            type:    String,
            default: null,
        },

        // Statut de traitement de l'alerte
        statut: {
            type:    String,
            enum:    ['nouveau', 'en_cours', 'resolu', 'ignore'],
            default: 'nouveau',
            index:   true,
        },

        // Commentaire de résolution
        resolution_note: {
            type:    String,
            default: '',
        },

        resolved_at: {
            type:    Date,
            default: null,
        },
    },
    {
        timestamps: true,  // createdAt, updatedAt automatiques
        collection:  'risk_alerts',
    }
);

// Index composé pour recherche rapide par contrat + code
RiskAlertSchema.index({ contrat_id: 1, code: 1 });

// Index pour triage chronologique
RiskAlertSchema.index({ createdAt: -1 });


/**
 * Méthode statique : compte le nombre d'occurrences d'un code risque
 * sur un contrat donné (pour la logique d'escalade).
 */
RiskAlertSchema.statics.countOccurrences = async function (contrat_id, code) {
    return this.countDocuments({ contrat_id, code });
};


/**
 * Méthode statique : retourne les alertes actives (non résolues)
 * d'un contrat, triées par sévérité puis date.
 */
RiskAlertSchema.statics.getActiveAlerts = async function (contrat_id) {
    const severiteOrder = { critique: 0, eleve: 1, moyen: 2, faible: 3 };

    const alerts = await this.find({
        contrat_id,
        statut: { $in: ['nouveau', 'en_cours'] },
    }).sort({ createdAt: -1 });

    return alerts.sort(
        (a, b) => (severiteOrder[a.severite] ?? 99) - (severiteOrder[b.severite] ?? 99)
    );
};


module.exports = mongoose.model('RiskAlert', RiskAlertSchema);