from django.db import models
from datetime import datetime

class Habitacion(models.Model):
    numero = models.CharField(max_length=10, unique=True)  
    disponible = models.BooleanField(default=True) 
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Habitación"  
        verbose_name_plural = "Habitaciones"   

    def __str__(self):
        return f'Habitación {self.numero} - {"Disponible" if self.disponible else "Ocupada"}'
    
class Huesped(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.SET_NULL, null=True)
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    fecha_check_in = models.DateTimeField(auto_now_add=True)  # Fecha y hora de check-in
    fecha_check_out = models.DateTimeField(null=True, blank=True)  # Cambiado a DateTimeField

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    def save(self, *args, **kwargs):
        if not self.pk and self.habitacion:
            self.habitacion.disponible = False  
            self.habitacion.save()
        super().save(*args, **kwargs)

    def check_out(self):
        if self.habitacion:
            self.habitacion.disponible = True  
            self.habitacion.save()
            self.fecha_check_out = datetime.now()  
            self.save()

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

