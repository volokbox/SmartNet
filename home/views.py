from django.shortcuts import redirect, render
from .models import Turma, Aluno, Curso
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse, HttpResponseServerError
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
import cv2
import os
from PIL import Image
import numpy as np
from .models import *
from .forms import TurmaForm, AlunoForm, CursoForm, ProfessorForm, SalaForm, HorarioForm, FaltaForm, EscolaForm, CreateUserForm, tipo_horarioForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now, localtime
from datetime import datetime
import shutil
from django.db import IntegrityError
import os
from collections import defaultdict
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User

# Pagina do sobre nos no index
def sobre_nos(request):
    return render(request, 'sobre_nos.html')

def indexx(request):
    return render(request, 'index.html')

def registerPage(request):
    # Cria-se uma instância da forma CreateUserForm.
    form = CreateUserForm()
    escolas = Escola.objects.all()

    # Verifica-se se o método de pedido é POST.
    if request.method == "POST":
        # Se for, cria-se uma nova instância da forma CreateUserForm
        # e preenche-se com dados da dictionary request.POST.
        form = CreateUserForm(request.POST)
        escola_id = request.POST.get("escola_select")

        # Se a forma for válida, guarda-se o novo utilizador no base de dados.
        if form.is_valid():
            user = form.save()
            escola = Escola.objects.get(ID_Escola=escola_id)

            user_admin = User.objects.get(username=user)
            user_admin.is_superuser = True
            user_admin.save()

            # Create or get Admin_Escola object for the user
            admin_escola, created = Admin_Escola.objects.get_or_create(admin=user, ID_Escola=escola)
            admin_escola.save()  # Save the Admin_Escola object

            # Exibe uma mensagem de sucesso e redireciona para o utilizador para a página de login.
            messages.success(request, 'Registo efetuado com sucesso')
            return redirect('login')
        


    # Cria-se um dicionário de contexto que contém a instância da forma.
    context = {'form': form, 'escolas': escolas}

    # Renderiza-se o modelo 'accounts/register.html', passando o dicionário de contexto.
    return render(request, 'accounts/register.html', context)

def loginPage(request):
    # Verifica se o método da requisição é POST
    if request.method == 'POST':
        # Obtém o nome de utilizador e a palavra-passe a partir dos dados da requisição POST
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentica o utilizador com o nome de utilizador e a palavra-passe fornecidos
        user = authenticate(request, username=username, password=password)

        # Se o utilizador não for None, significa que a autenticação foi bem-sucedida
        if user is not None:
            # Faz login no utilizador
            login(request, user)
            # redirecionar o utilizador para a vista 'aluno'
            return redirect('aluno')
        else:
            messages.success(request, ('Username ou palavra-pass errada!'))
            

    # Cria um dicionário de contexto vazio para ser usado no modelo
    context = {}
    # Renderiza o modelo 'accounts/login.html' com a requisição e o contexto
    return render(request, 'accounts/login.html')

def tipo_de_horario(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            info = Admin_Escola.objects.get(admin=user)
            escola_id = info.ID_Escola_id
        except:
            info = Professor_User.objects.get(professor=user)
            escola = Professor.objects.get(ID_Professor=info.ID_Professor_id)
            escola_id = escola.ID_Escola_id

        tipos = tipo_horario.objects.all()
        form = tipo_horarioForm()
        id_escola = tipo_horario.objects.values_list("ID_Escola", flat=True)

        nome_escola = Escola.objects.values_list("Nome", flat=True)
        Lista_nomes = {k: v for k, v in zip(id_escola, nome_escola)}# Obter todos os horários existentes do banco de dados
        # Obtain all entries from the tipo_horario table
        tipo_horario_entries = tipo_horario.objects.filter(ID_Escola=escola_id)

        # Extract the formato_horas for the specified school ID
        if tipo_horario_entries.exists():
            formato_horas = tipo_horario_entries[0].Formato_Horas
        else:
            formato_horas = ""  # Handle the case when no tipo_horario entry exists
        
        # Split the formato_horas into time slots
        time_slots_str = formato_horas
        
        # Split the time_slots_str into a list of time slots
        time_slots = time_slots_str.split(';') if time_slots_str else []
        
        # Obter todas as entradas de horário do banco de dados
        horario_entries = Horario.objects.all()

        # Inicializar um dicionário para armazenar os dados do horário agrupados por dia da semana
        horario_data = defaultdict(list)
        
        # Lista dos dias da semana
        weekdays = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
        
        # Agrupar as entradas por dia da semana
        for entry in horario_entries:
            id_escola = 2
            # Extrair o ID do professor a partir da representação em string
            professor_id = int(str(entry.ID_Professor).split()[-1][1:-1])
            
            # Obter o nome do dia da semana usando a lista de dias da semana
            dia_semana = weekdays[entry.Dia_semana]
            
            # Adicionar os dados da entrada ao dicionário de horário agrupados por dia da semana
            horario_data[dia_semana].append([
                entry.Hora_inicio.strftime('%H:%M'),
                entry.Hora_fim.strftime('%H:%M'),
                entry.Disciplina,
                professor_id  # Utilizar o ID extraído
            ])
        
        # Ordenar o dicionário de horário pelos dias da semana
        horario_data = dict(sorted(horario_data.items(), key=lambda x: weekdays.index(x[0])))
        if request.method == 'POST':
            form = tipo_horarioForm(request.POST)
            if form.is_valid():
                id_escola = escola_id
                hora_inicio = form.cleaned_data['Hora_inicio']
                hora_fim = form.cleaned_data['Hora_fim']
                
                # Check if there's an existing entry for this school ID
                try:
                    tipo_horario_obj = tipo_horario.objects.get(ID_Escola=id_escola)
                    formato_horas = tipo_horario_obj.Formato_Horas
                except tipo_horario.DoesNotExist:
                    tipo_horario_obj = None
                    formato_horas = ""

                # Update the time frame string if an existing entry is found
                if tipo_horario_obj:
                    if formato_horas:
                        formato_horas += f";{hora_inicio.strftime('%H:%M')} / {hora_fim.strftime('%H:%M')}"
                    else:
                        formato_horas = f"{hora_inicio.strftime('%H:%M')} / {hora_fim.strftime('%H:%M')}"

                    # Save the updated time frame string back to the database
                    tipo_horario_obj.Formato_Horas = formato_horas
                    tipo_horario_obj.save()
                else:
                    # Create a new entry if no existing entry is found
                    escola = Escola.objects.get(ID_Escola=id_escola)
                    formato_horas = f"{hora_inicio.strftime('%H:%M')} / {hora_fim.strftime('%H:%M')}"
                    tipo_horario.objects.create(ID_Escola=escola, Hora_inicio=hora_inicio, Hora_fim=hora_fim, Formato_Horas=formato_horas)

            return redirect('tipo_de_horario')
        
        return render(request, 'tipo_de_horario.html', {'form': form, 'tipos': tipos, 'Lista_nomes':Lista_nomes, 'horario_data': horario_data, 'time_slots': time_slots, 'weekdays':weekdays})
    else:
        return render(request, 'tipo_de_horario.html', {})

def eliminar_tipo_de_horario(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id
        # Cria um dicionário com IDs e nomes dos horários
        if request.method == "POST":
            # Elimina o registro do horário
            t_horario = tipo_horario.objects.get(ID_Escola=escola_id)
            t_horario.delete()
            # Redireciona para a página de horários
            return redirect('tipo_de_horario')        
        else:
            # Renderiza a página de horários
            return render(request, 'tipo_de_horario.html', {})
    else:
        return render(request, 'tipo_de_horario.html', {})

# Horario
def timetable(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            info = Admin_Escola.objects.get(admin=user)
            escola_id = info.ID_Escola_id
        except:
            info = Professor_User.objects.get(professor=user)
            prof_id = info.ID_Professor_id
            escola = Professor.objects.get(ID_Professor=info.ID_Professor_id)
            escola_id = escola.ID_Escola_id
    
        # Obtain all entries from the tipo_horario table
        tipo_horario_entries = tipo_horario.objects.filter(ID_Escola=escola_id)
        
        alunos = Aluno.objects.all()

        # Extract the formato_horas for the specified school ID
        if tipo_horario_entries.exists():
            formato_horas = tipo_horario_entries[0].Formato_Horas
        else:
            formato_horas = ""  # Handle the case when no tipo_horario entry exists
        
        # Split the formato_horas into time slots
        time_slots_str = formato_horas
        
        # Split the time_slots_str into a list of time slots
        time_slots = time_slots_str.split(';') if time_slots_str else []
        
        # Obter todas as entradas de horário do banco de dados
        horario_entries = Horario.objects.filter(ID_Professor=prof_id)

        # Inicializar um dicionário para armazenar os dados do horário agrupados por dia da semana
        horario_data = defaultdict(list)
        
        # Lista dos dias da semana
        weekdays = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
        
        # Agrupar as entradas por dia da semana
        for entry in horario_entries:
            # Extrair o ID do professor a partir da representação em string
            professor_id = int(str(entry.ID_Professor).split()[-1][1:-1])
            
            # Obter o nome do dia da semana usando a lista de dias da semana
            dia_semana = weekdays[entry.Dia_semana]
            horario_id = Horario.objects.get(ID_Professor=professor_id, Hora_inicio=entry.Hora_inicio, Dia_semana=entry.Dia_semana)
            turma = Turma.objects.get(ID_Turma=horario_id.ID_Turma_id)

            nome_turma = turma.Nome

            alunos_turma = Aluno.objects.filter(ID_Turma=turma.ID_Turma).values_list('Nome', flat=True)

            falta = Falta.objects.filter(ID_Horario=horario_id).values_list('ID_Aluno', flat=True)
            alunos_falta = []
            for i in falta:
                aluno_nome = Aluno.objects.get(ID_Aluno=i)
                alunos_falta.append(aluno_nome.Nome)

            # Adicionar os dados da entrada ao dicionário de horário agrupados por dia da semana
            horario_data[dia_semana].append([
                entry.Hora_inicio.strftime('%H:%M'),
                entry.Hora_fim.strftime('%H:%M'),
                entry.Disciplina,
                professor_id, # Utilizar o ID extraído
                horario_id.ID_Horario,
                nome_turma,
                alunos_falta, 
                alunos_turma
            ])
        
        # Ordenar o dicionário de horário pelos dias da semana
        horario_data = dict(sorted(horario_data.items(), key=lambda x: weekdays.index(x[0])))
        
        # Lista de intervalos de tempo para as colunas da tabela
        #time_slots_str = '08:15 / 09:00;09:00 / 09:45;10:00 / 10:45;10:45 / 11:30;11:45 / 12:30;12:30 / 13:15;13:30 / 14:15;14:15 / 15:00;15:15 / 16:00;16:00 / 16:45'

        #time_slots = time_slots_str.split(';')

        # Renderizar a página de horário do professor com os dados do horário
        return render(request, 'horario_professor.html', {'horario_data': horario_data, 'time_slots': time_slots, 'alunos':alunos, 'professor':escola})
    else:
        return render(request, 'horario_professor.html', {})

# Função para redireciona para a página inicial
def bd(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            info = Admin_Escola.objects.get(admin=user)
            escola_id = info.ID_Escola_id
        except:
            info = Professor_User.objects.get(professor=user)
            prof_id = info.ID_Professor_id
            escola = Professor.objects.get(ID_Professor=info.ID_Professor_id)
            escola_id = escola.ID_Escola_id
            return redirect('timetable')

        # Obtém todos os objetos da escola, professor, sala, curso, turma e aluno
        escola = Escola.objects.filter(ID_Escola=escola_id)
        turmas = Turma.objects.filter(ID_Escola=escola_id)
        professores = Professor.objects.filter(ID_Escola=escola_id)
        cursos = Curso.objects.filter(ID_Escola=escola_id)

        # Cria um dicionário com as variáveis a serem passadas para o template
        variables = {
            'escola': escola,
            'turmas': turmas,
            'professores': professores,
            'cursos': cursos
        }

        # Retorna a página inicial renderizada com as variáveis
        return render(request, 'home.html', variables)
    else:
        return render(request, 'home.html')
    
# Função `escola`: lida com pedidos HTTP relacionados com a gestão de escolas.
def escola(request):
    escolas = Escola.objects.all()

        # Obter os nomes e IDs dos cursos para associação posterior
    escolas_names = escolas.values_list('Nome', flat=True)
    escolas_id = escolas.values_list('ID_Escola', flat=True)
    escolas_join = {k: v for k, v in zip(escolas_id, escolas_names)}

    # Se o método do pedido for POST:
    if request.method == 'POST':
        # Cria um formulário com os dados do pedido POST ou None.
        form = EscolaForm(request.POST or None)

        # Se o formulário for válido:
        if form.is_valid():
            # Salva os dados do formulário no base de dados.
            form.save()

            # Exibe uma mensagem de sucesso.
            messages.success(request, 'Nova escola adicionada!')

            # Redireciona o utilizador para a página de gestão de escolas.
            return redirect('escola')

    # Se o método do pedido não for POST:
    else:
        # Renderiza o modelo 'escola.html' e retorna o HTML gerado.
        return render(request, 'escola.html', {'escolas_join':escolas_join})
    
# Função para adicionar um novo professor
def professor(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            info = Admin_Escola.objects.get(admin=user)
            escola_id = info.ID_Escola_id
        except:
            info = Professor_User.objects.get(professor=user)
            escola = Professor.objects.get(ID_Professor=info.ID_Professor_id)
            escola_id = escola.ID_Escola_id
          

        form = CreateUserForm()      
    
        # Obter todos os professores e seus IDs e nomes correspondentes
        professores = Professor.objects.filter(ID_Escola=escola_id)
        nomes_professor = professores.values_list('Nome', flat=True)
        id_professor = professores.values_list('ID_Professor', flat=True)
        professor_join = {k: v for k, v in zip(id_professor, nomes_professor)}
        professor_contas = Professor_User.objects.all()
        prof_conta_info = []

        for i in professor_contas:
            for j in id_professor:
                if i.ID_Professor_id == j:
                    dados = User.objects.get(id=i.professor_id)
                    prof_conta_info.append((i.ID_Professor_id, dados.username, dados.email))

        if request.method == 'POST':
            # Se o método da solicitação for POST, processar os dados do formulário
            form = ProfessorForm(request.POST or None)
            form_user = CreateUserForm(request.POST)

            if form.is_valid() and form_user.is_valid(): 
                # Salvar os novos dados do professor
                escola = Escola.objects.get(ID_Escola=escola_id)
                professor_novo = Professor.objects.create(ID_Escola=escola, Nome=form.cleaned_data['Nome'])
                professor_novo.save()

                user = form_user.save()

                # Create or get Admin_Escola object for the user
                user_professor, created = Professor_User.objects.get_or_create(professor=user, ID_Professor=professor_novo)
                user_professor.save() 

                messages.success(request, ('Novo Professor foi inserido!'))
            return redirect('professor')
        else:
            # Se o método da solicitação não for POST, redireciona para  o template do formulário do professor
            return render(request, 'professor.html', {'professores': professores, 'professor_join': professor_join, 'form':form, 'prof_conta_info':prof_conta_info})
    else:
        return render(request, 'professor.html', {})

# Função para gerir a página de salas
def sala(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id
        # Obter todas as salas do base de dados
        sala = Sala.objects.filter(ID_Escola=escola_id)

        # Obter os nomes das salas e seus respectivos IDs do base de dados
        sala_names = sala.values_list('Nome_Sala', flat=True)
        sala_id = sala.values_list('ID_Sala', flat=True)

        # Criar um dicionário com os IDs e nomes das salas
        sala_join = {k: v for k, v in zip(sala_id, sala_names)}

        # Verificar o método da requisição
        if request.method == 'POST':
            # Se o método for POST, tratar o formulário de submissão
            form = SalaForm(request.POST or None)

            # Verificar se o formulário é válido
            if form.is_valid():
                # Verificar se já existe uma sala com o mesmo nome
                if form.cleaned_data['Nome_Sala'] in sala_names:
                    messages.error(request, ('Uma sala com o mesmo nome já existe.'))
                else:
                    # Se o formulário for válido e não houver uma sala com o mesmo nome, salvar os dados no base de dados
                    escola = Escola.objects.get(ID_Escola=escola_id)
                    sala_nova = Sala.objects.create(ID_Escola=escola, Nome_Sala=form.cleaned_data['Nome_Sala'])
                    sala_nova.save()
                    messages.success(request, ('Nova Sala foi inserida!'))

                # Redirecionar para a página de salas
                return redirect('sala')
        else:
            # Se o método não for POST, redireciona para  a página de salas com as salas e o dicionário de IDs e nomes
            return render(request, 'sala.html', { 'sala': sala, 'sala_join': sala_join})    
    else:
        return render(request, 'sala.html', {})

# Função para adicionar um horário   
def horario(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id
        # Obter todos os horários existentes do banco de dados
        horario_bd = Horario.objects.filter(ID_Escola=escola_id)

        # Obter os nomes e IDs das salas, turmas e professores para associação posterior
        salas = Sala.objects.filter(ID_Escola=escola_id)
        sala_names = salas.values_list('Nome_Sala', flat=True)
        sala_id = salas.values_list('ID_Sala', flat=True)
        sala_join = {k: v for k, v in zip(sala_id, sala_names)}

        turmas = Turma.objects.filter(ID_Escola=escola_id)
        turma_names = turmas.values_list('Nome', flat=True)
        turma_id = turmas.values_list('ID_Turma', flat=True)
        turma_join = {k: v for k, v in zip(turma_id, turma_names)}

        professores = Professor.objects.filter(ID_Escola=escola_id)
        professor_names = professores.values_list('Nome', flat=True)
        professor_id = professores.values_list('ID_Professor', flat=True)
        professor_join = {k: v for k, v in zip(professor_id, professor_names)}

        for i in horario_bd:
            if i.Dia_semana == 0:
                i.Dia_semana = "Segunda-Feira"
            elif i.Dia_semana == 1:
                i.Dia_semana = "Terça-Feira"
            elif i.Dia_semana == 2:
                i.Dia_semana = "Quarta-Feira"
            elif i.Dia_semana == 3:
                i.Dia_semana = "Quinta-Feira"
            elif i.Dia_semana == 4:
                i.Dia_semana = "Sexta-Feira"
            elif i.Dia_semana == 5:
                i.Dia_semana = "Sábado"
            elif i.Dia_semana == 6:
                i.Dia_semana = "Domingo"

        # Verificar se a requisição é um POST (submissão de formulário)
        if request.method == "POST":
            # Criar um formulário com os dados recebidos da requisição POST
            form = HorarioForm(request.POST or None)
            # Verificar se o formulário é válido
            if form.is_valid():
                # Verificar se o professor já tem um horário agendado para essa hora
                existing_horario = Horario.objects.filter(
                    ID_Professor=form.cleaned_data['ID_Professor'],
                    Hora_inicio=form.cleaned_data['Hora_inicio'],
                    Hora_fim=form.cleaned_data['Hora_fim'],
                    Dia_semana=form.cleaned_data['Dia_semana']
                ).exists()
                if existing_horario:
                    # Se o professor já tem um horário nesse horário, exibir uma mensagem de erro
                    messages.error(request, "O professor já tem um horário agendado para essa hora.")
                else:
                    # Salvar os dados do formulário no banco de dados
                    escola = Escola.objects.get(ID_Escola=escola_id)
                    horario_novo = Horario.objects.create(ID_Sala=form.cleaned_data['ID_Sala'],
                                                            ID_Professor=form.cleaned_data['ID_Professor'],
                                                            ID_Turma=form.cleaned_data['ID_Turma'],
                                                            Hora_inicio=form.cleaned_data['Hora_inicio'],
                                                            Hora_fim=form.cleaned_data['Hora_fim'],
                                                            ID_Escola=escola,
                                                            Disciplina=form.cleaned_data['Disciplina'],
                                                            Dia_semana=form.cleaned_data['Dia_semana'])
                    horario_novo.save()
                    # Redirecionar o utilizador de volta à página de adição de horários
                    return redirect('horario')
            else:
                # Se o formulário não for válido, exibir os dados do POST para preencher o formulário novamente
                messages.error(request, "Erro ao criar o horário.")
                return render(request, 'horario.html', {'form': form})

        # Se a requisição não for um POST, renderizar a página de horário com os dados das salas, turmas, professores e horários existentes
        else:
            form = HorarioForm()
            return render(request, 'horario.html', {'form': form, 'sala_join': sala_join, 'turma_join': turma_join, 'professor_join': professor_join, 'horario':horario_bd})
        # Adicione um retorno padrão caso nenhum dos caminhos acima seja executado
        return render(request, 'horario.html', {'form': form, 'sala_join': sala_join, 'turma_join': turma_join, 'professor_join': professor_join, 'horario':horario_bd})
    else:
        return render(request, 'horario.html', {})

# Função para adicionar uma falta
def falta(request):

    # Obter todas as faltas, alunos e horários do base de dados
    faltas = Falta.objects.all()
    alunos = Aluno.objects.all()
    horarios = Horario.objects.all()

    # redireciona para  a página de faltas com as faltas, alunos e horários
    return render(request, 'falta.html', {'faltas': faltas, 'alunos':alunos, 'horarios':horarios})

# Função para adicionar uma turma
def turma(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id

        # Obter todas as turmas e alunos existentes no banco de dados
        turma = Turma.objects.filter(ID_Escola=escola_id)
        aluno = Aluno.objects.all()
        curso = Curso.objects.filter(ID_Escola=escola_id)

        # Obter os nomes e IDs das turmas e cursos para associação posterior
        turma_names = turma.values_list('Nome', flat=True)
        turma_id = turma.values_list('ID_Turma', flat=True)
        turma_join = {k: v for k, v in zip(turma_id, turma_names)}

        curso_names = curso.values_list('Nome', flat=True)
        curso_id = curso.values_list('ID_Curso', flat=True)
        curso_join = {k: v for k, v in zip(curso_id, curso_names)}

        # Verificar se a requisição é um POST (submissão de formulário)
        if request.method == "POST":
            # Criar um formulário para turma com os dados recebidos da requisição POST
            form_turma = TurmaForm(request.POST or None)
            
            # Verificar se o formulário é válido
            if form_turma.is_valid():
                try:
                    # Criar pasta específica para a turma
                    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images') 
                    path_new = str(escola_id) + '_' + request.POST['Nome']
                    path = os.path.join(image_path, path_new)

                    # Check if the directory already exists
                    if not os.path.exists(path):
                        os.mkdir(path)
                    else:
                        raise FileExistsError(f"A pasta '{path}' já existe.")
                    
                    # Salvar os dados do formulário na base de dados
                    escola = Escola.objects.get(ID_Escola=escola_id)
                    turma_nova = Turma.objects.create(ID_Escola=escola, Nome=form_turma.cleaned_data['Nome'], ID_Curso=form_turma.cleaned_data['ID_Curso'])
                    turma_nova.save()
                    
                    # Exibir mensagem de sucesso
                    messages.success(request, ('Nova Turma foi inserida!'))
                    
                    # Redirecionar o utilizador de volta à página de turmas
                    return redirect('turma')
                except IntegrityError:
                    # Exibir mensagem de erro se uma turma com o mesmo nome já existir
                    messages.error(request, 'Uma turma com o mesmo nome já existe.')
                except FileExistsError:
                    # Exibir mensagem de erro se a pasta já existe
                    messages.error(request, "Uma turma com o mesmo nome já existe.")
            else:
                # Se o formulário não for válido, exibir mensagem de erro
                messages.error(request, "Erro ao criar a turma.")

            # Redirecionar o utilizador de volta à página de turmas
            return redirect('turma')
        else:
            # Se a requisição não for um POST, renderizar a página de turmas com os dados das turmas, alunos, cursos e associações existentes
            return render(request, 'turma.html', { 'turma' : turma, 'aluno' : aluno, 'turma_join': turma_join, 'curso_join':curso_join })
    else:
        return render(request, 'turma.html', {})
      
# Função para adicionar um curso
def curso(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id
        # Obter todos os cursos existentes no banco de dados
        cursos = Curso.objects.filter(ID_Escola=escola_id)

        # Obter os nomes e IDs dos cursos para associação posterior
        curso_names = cursos.values_list('Nome', flat=True)
        curso_id = cursos.values_list('ID_Curso', flat=True)
        curso_join = {k: v for k, v in zip(curso_id, curso_names)}

        # Verificar se a requisição é um POST (submissão de formulário)
        if request.method == 'POST':
            # Criar um formulário com os dados recebidos da requisição POST
            form = CursoForm(request.POST or None)
            
            # Verificar se o formulário é válido
            if form.is_valid():
                # Salvar os dados do formulário no banco de dados
                escola = Escola.objects.get(ID_Escola=escola_id)
                curso_novo = Curso.objects.create(Nome=form.cleaned_data['Nome'], ID_Escola=escola)
                curso_novo.save()
                
                # Exibir mensagem de sucesso
                messages.success(request, ('Novo Curso foi inserido!'))
                
                # Redirecionar o utilizador de volta à página de cursos
                return redirect('curso')
        
        # Se a requisição não for um POST, renderizar a página de cursos com os dados dos cursos e associações existentes
        else:
            return render(request, 'curso.html', {'cursos': cursos, 'curso_join': curso_join})
    else:
        return render(request, 'curso.html', {})

# Função para adicionar um aluno
def aluno(request):
    if request.user.is_authenticated:
        # Obter os nomes e IDs das turmas para associação posterior
        turma_names = Turma.objects.values_list('Nome', flat=True)
        turma_id = Turma.objects.values_list('ID_Turma', flat=True)
        turma_join = {k: v for k, v in zip(turma_id, turma_names)}
        
        # Verificar se a requisição é um POST (submissão de formulário)
        if request.method == "POST":
            # Criar um formulário com os dados recebidos da requisição POST
            form = AlunoForm(request.POST or None)
            
            # Verificar se o formulário é válido
            if form.is_valid():
                # Obter o ID da turma associada ao aluno
                ID_Turma = request.POST.get('ID_Turma_FK')
                
                # Atualizar o número de alunos na turma
                turma = Turma.objects.get(pk=ID_Turma)
                turma.Numero_Alunos = turma.Numero_Alunos + 1
                turma.save()
                
                # Salvar os dados do formulário no banco de dados
                form.save()
                
                # Tirar fotos (função não definida aqui, deve ser implementada)
                take_photos(request, ID_Turma, request.POST['Numero_Turma'], request.POST['Nome'])
                
                # Exibir mensagem de sucesso
                messages.success(request, ('Aluno adicionado, e fotografias foram treinadas com sucesso!'))
                
                # Redirecionar o utilizador de volta à página de turmas
                return redirect('turma')
            else:
                # Se o formulário não for válido, obter o ID da turma e o nome do aluno para renderizar a página novamente
                ID_Turma = request.POST.get('ID_Turma')
                Nome = request.POST['Nome']
                
                # Exibir mensagem de erro
                messages.success(request, ("Ocorreu um erro, tente de novo!"))
                
                # Renderizar a página de turmas novamente com os dados do POST para preencher o formulário
                return render(request, 'turma.html', {'ID_Turma':ID_Turma, 'Nome':Nome})
        else:
            # Se a requisição não for um POST, renderizar a página de turmas com os dados das turmas existentes
            return render(request, 'turma.html', {'turma_join': turma_join})
    else:
        return render(request, 'turma.html', {})

# Eliminar turma
def delete_turma(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Obtém o ID da turma a ser eliminada
            ID_Turma_POST = request.POST.get('ID_Turma_FK')
            
            # Procura a turma na base de dados
            turma = Turma.objects.get(ID_Turma=ID_Turma_POST)

            # Procura a pasta com as fotografias referente à turma
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images') 
            path_old = str(turma.ID_Escola) + '_' + str(turma.Nome)
            path = os.path.join(image_path, path_old) 
            path_trained_file = os.path.join(image_path, str(turma.ID_Escola) + '_' + str(turma.Nome) + '_trainer.yml') 

            # Elimina a turma e a pasta da turma e o ficheiro treinado
            turma.delete()
            if os.path.exists(path_trained_file):
                os.remove(path_trained_file)
            
            if os.path.exists(path):
                shutil.rmtree(path)

            return redirect('turma')        
        else:
            # Renderiza a página de turmas
            return render(request, 'turma.html', {})
    else:
        return render(request, 'turma.html', {})
    
# Eliminar Horario
def delete_horario(request):
    # Cria um dicionário com IDs e nomes dos horários
    if request.method == "POST":
        # Obtém o ID do horário a ser eliminado
        ID_Horario_POST = request.POST.get('ID_Horario_FK')
        print(ID_Horario_POST)
        # Elimina o registro do horário
        horario = Horario.objects.get(ID_Horario=ID_Horario_POST)
        horario.delete()
        # Redireciona para a página de horários
        return redirect('horario')        
    else:
        # Renderiza a página de horários
        return render(request, 'horario.html', {})

# Eliminar Aluno
def delete_aluno(request, id):  
    # Obter o aluno a ser removido
    aluno = Aluno.objects.get(ID_Aluno=id)
    # Obter o ID da turma do aluno
    ID_Turma_Aluno = aluno.ID_Turma

    # Atualizar o número de alunos na turma
    turma = Turma.objects.get(ID_Turma=ID_Turma_Aluno)
    turma.Numero_Alunos -= 1 

    # Obter IDs e nomes da turma para manipulação de arquivos de imagem
    id_escola_turma = str(turma.ID_Escola)
    nome_turma = str(turma.Nome)
    pasta_path = "images/" + id_escola_turma + "_" + nome_turma
    nome_img_aluno = str(aluno.Numero_Turma) + "_" + str(aluno.Nome)
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pasta_path)

    # Remover as imagens associadas ao aluno
    for root, directories, files in os.walk(image_path):
        for file in files:
            file_name = file
            if file_name.startswith(nome_img_aluno):
                file_loc = os.path.join(root, file)
                os.remove(file_loc)    

    # Salvar as alterações na turma
    turma.save()
    # Remover o aluno
    aluno.delete()
    # Treinar novamente o reconhecimento facial após a remoção do aluno
    train_photos(request, turma.ID_Turma)

    # Redirecionar para a página da turma após a exclusão do aluno
    return redirect('turma')

# Eliminar Sala
def delete_sala(request):
    if request.user.is_authenticated:
        # Cria um dicionário com IDs e nomes das salas
        if request.method == "POST":
            # Obtém o ID da sala a ser eliminada
            ID_Sala_POST = request.POST.get('ID_Sala_FK')
            # Elimina o registro da sala
            sala = Sala.objects.get(ID_Sala=ID_Sala_POST)
            sala.delete()
            # Redireciona para a página de salas
            return redirect('sala')        
        else:
            # Renderiza a página de salas
            return render(request, 'sala.html', {})
    else:
        return render(request, 'sala.html', {})

# Eliminar Curso
def delete_curso(request):
    if request.user.is_authenticated:
        # Cria um dicionário com IDs e nomes das turmas
        if request.method == "POST":
            # Obtém o ID do curso a ser eliminado
            ID_Curso_POST = request.POST.get('ID_Curso_FK')
            # Elimina o registro do curso
            curso = Curso.objects.get(ID_Curso=ID_Curso_POST)
            nome_curso = curso.Nome
            curso.delete()
            
            messages.success(request, ('Curso ' + nome_curso + ' foi eliminado!'))

            # Redireciona para a página de cursos
            return redirect('curso')        
        else:
            # Renderiza a página de cursos
            return render(request, 'curso.html', {})
    else:
        return render(request, 'curso.html', {})

# Eliminar Escola
def delete_escola(request):
        # Cria um dicionário com IDs e nomes das turmas
        if request.method == "POST":
            # Obtém o ID do curso a ser eliminado
            ID_Escola_POST = request.POST.get('ID_Escola_FK')
            # Elimina o registro do curso
            escola = Escola.objects.get(ID_Escola=ID_Escola_POST)
            nome_escola = escola.Nome
            escola.delete()
            
            messages.success(request, ('Escola ' + nome_escola + ' foi eliminada!'))

            # Redireciona para a página de cursos
            return redirect('escola')        
        else:
            # Renderiza a página de cursos
            return render(request, 'escola.html', {})

# Eliminar Professor
def delete_professor(request):
    if request.user.is_authenticated:
        # Cria um dicionário com IDs e nomes das turmas
        if request.method == "POST":
            # Obtém o ID da turma a ser eliminado
            ID_Turma_POST = request.POST.get('ID_Turma_FK')

            # Elimina o registro do professor associado à turma
            professor = Professor.objects.get(ID_Professor=ID_Turma_POST)
            nome_professor = professor.Nome
            professor.delete()
            
            messages.success(request, ('Professor ' + nome_professor + ' foi eliminado!'))

            # Redireciona para a página de professores
            return redirect('professor')        
        else:
            # Direcion para a página de professores
            return render(request, 'professor.html', {})
    else:
        return render(request, 'professor.html', {})

# Reconhecimento facial
@csrf_exempt
def face_recognition(request):
    if request.user.is_authenticated:
        user = request.user
        info = Admin_Escola.objects.get(admin=user)
        escola_id = info.ID_Escola_id

        # Obter os nomes e IDs das salas
        sala = Sala.objects.filter(ID_Escola=escola_id)
        sala_names = sala.values_list('Nome_Sala', flat=True)
        sala_id = sala.values_list('ID_Sala', flat=True)
        sala_join = {k: v for k, v in zip(sala_id, sala_names)}

        if request.method == 'POST' and 'selected_option' in request.POST:
            selected_option = request.POST['selected_option']
            # Criar um objeto reconhecedor facial
            recognizer = cv2.face.LBPHFaceRecognizer_create()

            # Caminho para o arquivo cascade haarcascade
            face_cascade_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_default.xml')
            faceCascade = cv2.CascadeClassifier(face_cascade_path)

            # Fonte da janela para exibir texto
            font = cv2.FONT_HERSHEY_SIMPLEX

            id = 0
            
            # Dicionários para armazenar nomes, taxas de presença e IDs dos alunos
            names = {0: 'None'}
            presence_rate = {0:0}
            aluno = {0:0}
            sala = request.POST['selected_option']  # Convert to integer

            # Obter horários da sala e lista de alunos
            horario = Horario.objects.filter(ID_Sala=sala)
            alunos = Aluno.objects.all()

            # Obter data e hora atual
            today = datetime.today()

            # Verificar o horário, dia da semana e sala atual
            for item in horario:
                # Verificar se o dia da semana do horário coincide com o dia atual
                if item.Dia_semana == today.weekday():
                    # Verificar se o horário atual está dentro do intervalo do horário definido
                    if item.Hora_inicio <= localtime().time() <= item.Hora_fim:
                        # Obter o horário do aluno
                        horario_aluno = Horario.objects.get(ID_Horario=item.ID_Horario)
                        for i in alunos:
                            # Verificar se o ID da turma do aluno corresponde ao ID da turma do horário
                            id_turma = int(str(item.ID_Turma))
                            if int(i.ID_Turma) == id_turma:
                                # Obter o nome e o ID da turma
                                id_turma = Turma.objects.get(ID_Turma=i.ID_Turma)
                                nome_turma = id_turma.Nome

                                # Definir o número da turma do aluno ao seu ID e definir a taxa de presença inicial como 0
                                aluno[i.Numero_Turma] = i.ID_Aluno
                                names[i.Numero_Turma] = i.Nome
                                presence_rate[i.Numero_Turma] = 0

                                # Obter o ID da escola relacionada à turma
                                id_escola_turma = id_turma.ID_Escola
            
            # Nome do modelo de reconhecimento facial da turma
            ficheiro_treinado = "images/" + str(id_escola_turma) + "_" + str(nome_turma) + "_trainer.yml"

            # Carregar o arquivo treinado para reconhecimento facial
            trainer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ficheiro_treinado)
            recognizer.read(trainer_path)

            # Iniciar a captura de vídeo
            cam = cv2.VideoCapture(0)

            # Configurar a resolução do vídeo
            cam.set(3, 853) 
            cam.set(4, 480)
            try:
                while True:
                    # Capturar um frame da câmera
                    ret, img = cam.read()

                    # Converter a imagem para escala de cinza para reconhecimento facial
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    # Detectar rostos na imagem
                    faces = faceCascade.detectMultiScale(
                        gray,
                        scaleFactor=1.05,
                        minNeighbors=8,
                        minSize=(30, 30),
                    )

                    # Para cada rosto na imagem do frame
                    for (x, y, w, h) in faces:
                        # Desenhar um retângulo ao redor do rosto
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Fazer uma previsão do rosto
                        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

                        # Verificar se a probabilidade da previsão é alta o suficiente
                        if (confidence < 100):
                            # Atualizar a taxa de presença associada ao ID do aluno
                            presence_rate[id] += 1
                            id = names[id]  # Obter o nome do aluno pelo ID
                            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

                    # Exibir o reconhecimento facial em tela cheia
                    cv2.namedWindow("camera", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) 
                    cv2.imshow('camera', img) 

                    # Pressionar Esc para sair
                    k = cv2.waitKey(10) & 0xff
                    if k == 27:
                        break
            except Exception as e:
                print("An error occurred:", e)
            finally:
                # Finalizar e salvar as faltas dos alunos
                for keys in presence_rate:
                    if presence_rate[keys] < 30 and keys != 0:
                        aluno_id = aluno[keys]
                        aluno_falta = Aluno.objects.get(ID_Aluno=aluno_id)
                        falta = Falta(ID_Aluno=aluno_falta, ID_Horario=horario_aluno)
                        falta.save()

                cam.release()
                cv2.destroyAllWindows()
                response_data = {'message': 'Facial recognition executed for option: ' + selected_option}
                return JsonResponse(response_data)
        else:
            # Se não houver uma solicitação POST, renderizar a página HTML com as opções das salas
            return render(request, 'facial_recognition_page.html', { 'sala_join': sala_join})
    else:
        return render(request, 'facial_recognition_page.html', {})

# Página para tirar fotografias das caras
def take_photos(request, ID_Turma_pk, Numero_Turma, Nome):
    # Obter a turma com base no ID fornecido
    turma_escola = Turma.objects.get(ID_Turma=ID_Turma_pk)
    id_escola_turma = str(turma_escola.ID_Escola)
    nome_turma = str(turma_escola.Nome)

    # Construir o caminho para a pasta onde as imagens estão armazenadas
    pasta_path = "images/" + id_escola_turma + "_" + nome_turma
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pasta_path) 
    count = 0

    # Contar o número de fotografias de caras na pasta
    for path in os.listdir(image_path):
        if os.path.isfile(os.path.join(image_path, path)):
            count += 1    # Incrementar o contador

    # Determinar o número de caras com base no número de fotografias
    if(count != 0):
        caras = count/100
    else:
        caras = 0

    # Verificar se a pasta para armazenar as imagens existe, se não, criar
    if not os.path.exists('images'):
        os.makedirs('images')

    # Caminho para o arquivo cascade haarcascade
    face_cascade_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_default.xml')
    faceCascade = cv2.CascadeClassifier(face_cascade_Path)

    # Verificar se o arquivo cascade foi carregado corretamente
    if faceCascade.empty():
        print("Erro: Não foi possível abrir o arquivo haarcascade.")
        return HttpResponseServerError("Erro interno do servidor: Não foi possível abrir o arquivo haarcascade.")
        
    # Captura de Vídeo
    cam = cv2.VideoCapture(0)

    # Configurar a resolução do vídeo para 16:9
    cam.set(3,640)
    cam.set(4,480)

    # Reinicializar a variável de contagem
    count = 0
        
    # Atribuir um ID único a cada cara
    id_cara = caras + 1

    while(True):
        # Capturar um frame da câmera
        ret, img = cam.read()

        # Converter a imagem para escala de cinza para reconhecimento facial
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detectar caras no frame
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x,y,w,h) in faces:
            # Desenhar um retângulo ao redor da cara detectada
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
            count += 1

            # Guardar a imagem capturada na pasta 'images'
            cv2.imwrite("./home/images/" + id_escola_turma + "_" + nome_turma + "/" + str(Numero_Turma)
                         + "_" + str(Nome) + "_" + str(count) + ".jpg", gray[y:y+h,x:x+w])

            # Exibir a imagem em tela cheia
            cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('image', img)

        # Pressionar qualquer tecla para sair
        k = cv2.waitKey(100) & 0xff
        if k < 100:
            break
        # Capturar 100 amostras de cara e parar o vídeo
        elif count >= 100:
            break

    # Fechar a camara
    cam.release()
    cv2.destroyAllWindows()

        
    # Obter o caminho para as imagens de caras
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pasta_path)
    recognizer = cv2.face.LBPHFaceRecognizer_create() 
        
    # Carregar o arquivo cascade Haar
    cascade = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_default.xml')
    detector = cv2.CascadeClassifier(cascade)

    def getImagesAndLabels(path):
        # Obter caminhos para todas as imagens na pasta
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            # Abrir a imagem e converter para escala de cinza
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            
            # Obter o ID da imagem a partir do nome da fotografia
            id = int(os.path.split(imagePath)[-1].split("_")[0])
            
            # Detectar caras na imagem
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                # Recortar o rosto da imagem
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)

        # Devolver caras e ids
        return faceSamples, ids
    
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))
    
    # Guardar o modelo no pasta das images
    nome_ficheiro_treinado = "images/" + id_escola_turma + "_" + nome_turma + "_trainer.yml"
    trained_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_ficheiro_treinado)
    recognizer.write(trained_file_path)

    # Voltar para a página das turmas
    return render(request, 'turma.html', {})

# Treinar Fotos
def train_photos(request, ID_Turma_pk):
    # Obter a turma com base no ID 
    turma_escola = Turma.objects.get(ID_Turma=ID_Turma_pk)
    id_escola_turma = str(turma_escola.ID_Escola)
    nome_turma = str(turma_escola.Nome)

    # Construir o caminho para a pasta onde as imagens estão armazenadas
    pasta_path = "images/" + id_escola_turma + "_" + nome_turma
          
    # Caminho da pasta onde as imagens de rosto estão armazenadas
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pasta_path)
    # Criar um reconhecedor de rostos usando o algoritmo LBPH
    recognizer = cv2.face.LBPHFaceRecognizer_create() 
        
    # Ficheiro de HaarCascadeClassifier
    cascade = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'haarcascade_frontalface_default.xml')
    detector = cv2.CascadeClassifier(cascade)

    def getImagesAndLabels(path):
        # Obter caminhos para todas as imagens na pasta
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            # Converter para escala de cinza
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img,'uint8')
            # Obter o ID do aluno a partir do nome da pasta
            id = int(os.path.split(imagePath)[-1].split("_")[0])
            # Detectar caras na imagem usando o classificador Haar
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

        return faceSamples, ids
    # Obter amostras de caras e IDs correspondentes
    faces,ids = getImagesAndLabels(path)
    # Treinar o reconhecedor com as amostras de caras e IDs correspondentes
    if len(faces) != 0:
        recognizer.train(faces, np.array(ids))

        
    # Guarda o modelo na pasta correta da turma atual
    nome_ficheiro_treinado = "images/" + id_escola_turma + "_" + nome_turma + "_trainer.yml"
    trained_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_ficheiro_treinado)
    recognizer.write(trained_file_path)

    # Voltar para a página da turma
    return render(request, 'turma.html', {})
