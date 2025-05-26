import math
import base64
from io import BytesIO

import numpy as np
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Graph
from .forms import RegisterForm, LoginForm, GraphForm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def index(request):
    graphs = Graph.objects.all().order_by('-created_at')

    graphs_with_plots = []
    for graph in graphs:
        plot_data = generate_tan_plot(graph.x_value)
        graphs_with_plots.append({
            'id': graph.id,
            'user': graph.user,
            'x_value': graph.x_value,
            'created_at': graph.created_at,
            'plot_data': plot_data
        })

    return render(request, 'index.html', {'graphs': graphs_with_plots})

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

def generate_tan_plot(x):
    x_values = np.linspace(x - math.pi / 2 + 0.1, x + math.pi / 2 - 0.1, 100)
    y_values = np.tan(x_values)

    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, 'b-', linewidth=2)
    plt.scatter([x], [math.tan(x)], color='red', s=50)
    plt.title(f'График тангенса (tg(x))')
    plt.xlabel('x')
    plt.ylabel('tg(x)')
    plt.grid(True)
    plt.xlim(x - math.pi / 2 + 0.1, x + math.pi / 2 - 0.1)
    plt.ylim(-10, 10)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@login_required
def personal_area(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data['x_value']
            if (x - math.pi / 2) % math.pi == 0:
                form.add_error('x_value', 'Тангенс не определен в этой точке')
            else:
                # Генерируем график и сохраняем только x_value
                graph = Graph.objects.create(user=request.user, x_value=x)
                return redirect('personal_area')
    else:
        form = GraphForm()

    user_graphs = Graph.objects.filter(user=request.user).order_by('-created_at')

    graphs_with_plots = []
    for graph in user_graphs:
        plot_data = generate_tan_plot(graph.x_value)
        graphs_with_plots.append({
            'id': graph.id,
            'x_value': graph.x_value,
            'created_at': graph.created_at,
            'plot_data': plot_data
        })

    return render(request, 'personal_area.html', {
        'form': form,
        'graphs': graphs_with_plots
    })

@user_passes_test(lambda u: u.is_superuser)
def delete_graph(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    graph.delete()
    return redirect('index')


@login_required
def delete_personal_graph(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)

    if graph.user != request.user:
        return HttpResponseForbidden("У вас нет прав на удаление этого графика")

    graph.delete()
    return redirect('personal_area')


