from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

#descrição/glossário: blank=true e null=true -> campo não obrigatório


# Modelo para Clínicas
class Clinica(models.Model):
    name = models.CharField(max_length=100)  
    email = models.EmailField(unique=True) 
    password = models.CharField(max_length=100)  
    phone = models.CharField(max_length=20, blank=True, null=True)  
    address = models.TextField(blank=True, null=True)  
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True)  

    def __str__(self):
        return self.name

# Modelo para Pacientes
class Paciente(models.Model):
    name = models.CharField(max_length=100)  
    age = models.PositiveIntegerField() 
    birth_date = models.DateField(blank=True, null=True)  
    blood_type = models.CharField(
        max_length=3, 
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], 
        blank=True, 
        null=True) 
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='pacientes') 
    medical_history = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.name
