from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/tasks/', views.get_tasks, name='get_tasks'),   
    path('update_profile/', views.update_profile, name='update_profile'),
    path('get_profile/', views.get_profile, name='get_profile'),
]