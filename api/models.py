from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=120, verbose_name='Name of the Student')
    age = models.PositiveIntegerField()
    grade = models.CharField(max_length=120)