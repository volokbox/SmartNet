# Generated by Django 4.1.12 on 2024-02-20 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='ID_Turma_FK',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='home.turma'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='aluno',
            name='ID_Turma',
            field=models.IntegerField(),
        ),
    ]