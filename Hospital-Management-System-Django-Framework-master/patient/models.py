from django.db import models
from userSystem.models import CustomUser
# Create your models here.

class Patient(models.Model):
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    patient_uhid = models.BigIntegerField()
    
    
    def __str__(self):
     return f'{self.patient_uhid} {self.userID}'
    


from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['userID', 'patient_uhid']

    