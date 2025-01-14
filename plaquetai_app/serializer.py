from rest_framework import serializers
from .models import Clinica, Paciente, Consulta

class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = '__all__'  # Inclui todos os campos do modelo

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
