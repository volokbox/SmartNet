# Generated by Django 4.1.12 on 2024-02-25 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_aluno_id_turma_fk_alter_aluno_id_turma'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='Numero_Turma',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='turma',
            name='Numero_Alunos',
            field=models.IntegerField(default=0),
        ),
    ]
