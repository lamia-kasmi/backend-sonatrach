# clm_service/serializers.py
from rest_framework import serializers
from .models import Contrat


class ContratSerializer(serializers.ModelSerializer):
    """Serializer for reading contract data"""
    
    class Meta:
        model = Contrat
        fields = '__all__'


class ContratCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating contracts"""
    
    class Meta:
        model = Contrat
        fields = [
            'numero_contrat', 'titre', 'type_contrat',
            'cree_par_id', 'cree_par_role', 'departement_id',
            'direction_id', 'direction_centrale_id', 'partie_a_nom',
            'partie_b_nom', 'pays_partie_b', 'objet', 'date_signature',
            'date_debut', 'date_fin', 'montant', 'devise',
            'conditions_paiement', 'statut'
        ]
    
    def validate_numero_contrat(self, value):
        """Check that contract number is unique"""
        if Contrat.objects.filter(numero_contrat=value).exists():
            raise serializers.ValidationError("Un contrat avec ce numéro existe déjà")
        return value
    
    def validate_dates(self, data):
        """Validate date logic"""
        if 'date_debut' in data and 'date_fin' in data:
            if data['date_debut'] and data['date_fin']:
                if data['date_debut'] > data['date_fin']:
                    raise serializers.ValidationError(
                        "La date de début doit être antérieure à la date de fin"
                    )
        return data
    
    def validate_montant(self, value):
        """Validate montant is positive"""
        if value < 0:
            raise serializers.ValidationError("Le montant doit être positif")
        return value