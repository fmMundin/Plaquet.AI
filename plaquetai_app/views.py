from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Clinica, Paciente
from .serializers import ClinicaSerializer, PacienteSerializer

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
