# Generated by Django 4.1.12 on 2024-03-26 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_admin_escola'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_escola',
            name='ID_Escola',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.escola'),
        ),
    ]