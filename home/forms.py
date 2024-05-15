from django import forms
from .models import Turma, Aluno, Curso, Professor, Sala, Horario, Falta, Escola, My_User, tipo_horario
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    class Meta: 
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class tipo_horarioForm(forms.ModelForm):
    class Meta: 
        model = tipo_horario
        fields = ['Hora_inicio', 'Hora_fim']

        def clean(self):
            cleaned_data = super().clean()
            hora_inicio = cleaned_data.get('Hora_inicio')
            hora_fim = cleaned_data.get('Hora_fim')

            if hora_inicio and hora_fim:
                # Add custom validation logic here if needed
                if hora_inicio >= hora_fim:
                    raise forms.ValidationError("Hora de início deve ser anterior à hora de término.")

            return cleaned_data

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['Nome', 'ID_Curso']
        

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['ID_Turma_FK' , 'Nome', 'Numero_Turma']

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['Nome']

class UserForm(forms.ModelForm):
    class Meta:
        model = My_User
        fields = ['Nome_Utilizador','Email','Password', 'ID_Professor']

# Form Escola
class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['ID_Escola', 'Nome', 'Agrupamento', 'Localizacao']

# Form Professor
class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['Nome']

# Form Sala
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['Nome_Sala']

    
class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['ID_Sala', 'ID_Turma', 'ID_Professor', 'Hora_inicio', 'Hora_fim', 'Dia_semana', 'Disciplina']
    
class FaltaForm(forms.ModelForm):
    class Meta:
        model = Falta
        fields = ['ID_Falta', 'ID_Aluno', 'ID_Horario']
    
