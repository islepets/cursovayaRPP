import io
import math

import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from .models import Graph
from .forms import RegisterForm, LoginForm, GraphForm
import matplotlib.pyplot as plt

def index(request):
    graphs = Graph.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'graphs': graphs})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def personal_area(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data['x_value']

            # Проверка на точки разрыва тангенса
            if (x - math.pi / 2) % math.pi == 0:
                form.add_error('x_value', 'Тангенс не определен в этой точке')
                return render(request, 'personal_area.html',
                              {'form': form, 'graphs': Graph.objects.filter(user=request.user)})

            # Создаем диапазон значений для построения графика
            x_values = np.linspace(x - math.pi / 2 + 0.1, x + math.pi / 2 - 0.1, 100)
            y_values = np.tan(x_values)

            # Построение графика
            plt.figure(figsize=(8, 6))
            plt.plot(x_values, y_values, 'b-', linewidth=2)  # линия графика
            plt.scatter([x], [math.tan(x)], color='red', s=50)  # выделяем точку
            plt.title(f'График тангенса (tg(x))')
            plt.xlabel('x')
            plt.ylabel('tg(x)')
            plt.grid(True)

            # Настройка области просмотра
            plt.xlim(x - math.pi / 2 + 0.1, x + math.pi / 2 - 0.1)
            plt.ylim(-10, 10)  # ограничиваем по y для лучшего отображения

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            plt.close()
            buf.seek(0)
            image_file = ContentFile(buf.read(), name=f'tan_graph_{request.user.id}_{x}.png')
            Graph.objects.create(user=request.user, x_value=x, image=image_file)
            return redirect('personal_area')
    else:
        form = GraphForm()

    user_graphs = Graph.objects.filter(user=request.user)
    return render(request, 'personal_area.html', {'form': form, 'graphs': user_graphs})

@user_passes_test(lambda u: u.is_superuser)
def delete_graph(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    graph.delete()
    return redirect('index')