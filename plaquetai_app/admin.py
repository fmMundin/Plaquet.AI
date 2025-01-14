from django.contrib import admin

# Register your models here.
from .models import Clinica, Paciente

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'blood_type', 'clinica')
