from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Tabela Escola
class Escola(models.Model):
    ID_Escola = models.BigAutoField(primary_key=True)
    Nome = models.CharField(max_length = 150)
    Agrupamento = models.CharField(max_length = 150)
    Localizacao = models.CharField(max_length = 100)

    def __str__(self):
        return str(self.ID_Escola)

# Tabela Curso
class Curso(models.Model):
    ID_Curso = models.BigAutoField(primary_key=True)
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    Nome = models.CharField(max_length=100)

    def __str__(self):
        return str(self.ID_Curso)

# Tabela Turma
class Turma(models.Model):
    ID_Turma = models.BigAutoField(primary_key=True)
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    Nome = models.CharField(max_length=100)
    Numero_Alunos = models.IntegerField(default=0)
    ID_Curso = models.ForeignKey(Curso, models.CASCADE)

    def __str__(self):
        return str(self.ID_Turma)

# Tabela Aluno
class Aluno(models.Model):
    ID_Aluno = models.BigAutoField(primary_key=True)
    ID_Turma_FK = models.ForeignKey(Turma, on_delete=models.CASCADE)
    ID_Turma = models.IntegerField()
    Nome = models.CharField(max_length=100)
    Numero_Turma = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs): # Transformam ID_Turma para int
        if self.ID_Turma_FK:
            self.ID_Turma = self.ID_Turma_FK.pk
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.ID_Aluno)
    
# Tabela Professor
class Professor(models.Model):
     ID_Professor = models.BigAutoField(primary_key=True)
     ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
     Nome = models.CharField(max_length=100)

# Tabela Sala
class Sala(models.Model):
    ID_Sala = models.BigAutoField(primary_key=True)
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    Nome_Sala = models.CharField(max_length=100)

# Tabela Horário
class Horario(models.Model):
    ID_Horario = models.BigAutoField(primary_key=True)
    ID_Sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    ID_Turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    ID_Professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    Hora_inicio = models.TimeField()
    Hora_fim = models.TimeField()
    Dia_semana = models.IntegerField()
    Disciplina = models.CharField(max_length=100)

    def __str__(self):
        return str(self.ID_Turma)

# Tabela Falta
class Falta(models.Model):
    ID_Falta = models.BigAutoField(primary_key=True)
    ID_Aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    ID_Horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

# Utilizador
class My_User(models.Model):
    ID_Utilizador = models.BigAutoField(primary_key=True)
    ID_Professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    Nome_Utilizador = models.CharField(max_length=100)
    Email = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)

class Admin_Escola(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True) 
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)

class Professor_User(models.Model):
    professor = models.OneToOneField(User, on_delete=models.CASCADE)
    ID_Professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

class tipo_horario(models.Model):
    ID_Tipo = models.BigAutoField(primary_key=True)
    ID_Escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    Hora_inicio = models.TimeField()
    Hora_fim = models.TimeField()
    Formato_Horas = models.CharField(max_length=200)