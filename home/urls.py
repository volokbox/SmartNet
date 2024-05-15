from django.urls import path
from .views import *


urlpatterns = [
    path('', bd, name='bd'),
    path('take-photos/', take_photos, name='take_photos'),
    path('face-recognition/', face_recognition, name='face_recognition'),
    path('professor/', professor, name='professor'),
    path('escola/', escola, name='escola'),
    path('aluno/', aluno, name='aluno'),
    path('curso/', curso, name='curso'),
    path('falta/', falta, name='falta'),
    path('horario/', horario, name='horario'),
    path('sala/', sala, name='sala'),
    path('turma/', turma, name='turma'),
    path('delete_turma/', delete_turma, name='delete_turma'),
    path('delete/<int:id>/', delete_aluno, name='delete_aluno'),
    path('delete_sala/', delete_sala, name='delete_sala'),
    path('delete_curso/', delete_curso, name='delete_curso'),
    path('delete_professor/', delete_professor, name='delete_professor'),
    path('delete_escola/', delete_escola, name='delete_escola'),
    path('timetable/', timetable, name='timetable'),
    path('delete_horario/', delete_horario, name='delete_horario'),
    path('bd/', bd, name="bd"),
    path('accounts/register/', registerPage, name="registerPage"),
    path('login/', loginPage, name="loginPage"),
    path('index/', indexx, name="indexx"),
    path('tipo_de_horario/', tipo_de_horario, name="tipo_de_horario"),
    path('eliminar_tipo_de_horario/', eliminar_tipo_de_horario, name="eliminar_tipo_de_horario"),
    path('sobre_nos/', sobre_nos, name="sobre_nos"),
    

]
