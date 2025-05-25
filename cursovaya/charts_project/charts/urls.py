from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('personal/', views.personal_area, name='personal_area'),
    path('delete/<int:graph_id>/', views.delete_graph, name='delete_graph'),
]
