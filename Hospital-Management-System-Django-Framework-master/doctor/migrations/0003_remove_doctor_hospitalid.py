# Generated by Django 4.1.1 on 2022-10-19 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_doctor_hospitalid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='hospitalID',
        ),
    ]