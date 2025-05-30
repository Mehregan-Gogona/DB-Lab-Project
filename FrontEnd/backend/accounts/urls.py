from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [

    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/tasks/', views.get_tasks, name='get_tasks'),   
    path('update_profile/', views.update_profile, name='update_profile'),
    path('get_profile/', views.get_profile, name='get_profile'),
    path('add_task/', views.add_task, name='add_task'),
    path('update_task_status/', views.update_task_status, name='update_task_status'),
    path('share_task/', views.share_task, name='share_task'),
    path('get_shared_tasks/', views.get_shared_tasks, name='get_shared_tasks'),
    path('update_shared_task_status/', views.update_shared_task_status, name='update_shared_task_status'),
    path('get_tasks_shared_by_me/', views.get_tasks_shared_by_me, name='get_tasks_shared_by_me'),
    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('mark_notification_read/', views.mark_notification_read, name='mark_notification_read'),
    path('create_notification/', views.create_notification, name='create_notification'),
    path('update_shared_task_status/', views.update_shared_task_status, name='update_shared_task_status'),
    path('respond_shared_task/', views.respond_shared_task, name='respond_shared_task'),
    
]

