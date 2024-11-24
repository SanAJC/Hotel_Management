from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError

class Habitacion(models.Model):
    numero = models.CharField(max_length=10, unique=True)  
    disponible = models.BooleanField(default=True) 
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiene_aire = models.BooleanField(default=False, verbose_name="Aire Acondicionado")

    class Meta:
        verbose_name = "Habitación"  
        verbose_name_plural = "Habitaciones"   

    def __str__(self):
        aire_status = "Con Aire" if self.tiene_aire else "Sin Aire"
        disponible_status = "Disponible" if self.disponible else "Ocupada"
        return f'Habitación {self.numero} - {aire_status} - {disponible_status}'
    
class Huesped(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.SET_NULL, null=True)
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    fecha_check_in = models.DateTimeField(auto_now_add=True)  
    fecha_check_out = models.DateTimeField(null=True, blank=True)  

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
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
    
    def tiene_suficiente_stock(self, cantidad_solicitada):
        return self.cantidad >= cantidad_solicitada
    
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    huesped = models.ForeignKey(Huesped, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Actualizar el stock del producto
        if not self.pk:  # Solo si es una nueva venta
            if self.producto.cantidad >= self.cantidad:
                self.producto.cantidad -= self.cantidad
                self.producto.save()
                # Calcular el total
                self.total = self.cantidad * self.producto.precio
                super().save(*args, **kwargs)
            else:
                raise ValidationError(f'No hay suficiente stock. Stock disponible: {self.producto.cantidad}')
    
    def __str__(self):
        return f'Venta de {self.producto.nombre} - Cantidad: {self.cantidad} - Total: ${self.total}'

