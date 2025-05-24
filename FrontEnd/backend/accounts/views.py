from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users , Tasks , Categories , Notifications ,SharedTasks
import os
from django.conf import settings


@csrf_exempt
def signup(request):
    print("DB Connection:", connection.settings_dict)

    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')

        print("Signup data:", name, email, password, phone_number)

        # Check for existing user by email
        if Users.objects.filter(email=email).exists():
            print("User already exists with email:", email)
            return JsonResponse({'success': False, 'error': 'Email already exists'})

        user = Users(
            name=name,
            email=email,
            password=password,
            phone_number=phone_number
        )
        user.save()
        print("User saved with ID:", user.user_id)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        print("Login attempt:", username, password)

        try:
            user = Users.objects.get(name=username, password=password)
            print("Login successful for user_id:", user.user_id)
            request.session['user_id'] = user.user_id
            return JsonResponse({'success': True, 'user_id': user.user_id})  # <-- FIXED HERE
        except Users.DoesNotExist:
            print("Login failed for username:", username)
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_profile(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        try:
            user = Users.objects.get(user_id=user_id)
            return JsonResponse({
                'success': True,
                'user': {
                    'name': user.name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'room_number': user.room_number,
                    'building_id': user.building_id,
                    'profile_picture': user.profile_picture,
                }
            })
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def get_tasks(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        tasks = list(Tasks.objects.filter(user_id=user_id).values())
    return JsonResponse({'success': True, 'tasks': tasks})    

@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        if request.content_type.startswith('multipart/form-data'):
            data = request.POST
            files = request.FILES
        else:
            data = json.loads(request.body)
            files = None

        user_id = data.get('user_id')
        print("user_id is ", user_id)
        print("data is ", data)
        try:
            user = Users.objects.get(user_id=user_id)
            if data.get('name'):
                user.name = data.get('name')
            if data.get('email'):
                user.email = data.get('email')
            if data.get('phone_number'):
                user.phone_number = data.get('phone_number')
            if data.get('room_number'):
                user.room_number = data.get('room_number')
            # Handle profile picture upload
            if files and 'profile_picture' in files:
                pic = files['profile_picture']
                # Save to media/profile_pics/ (ensure this folder exists and is writable)
                pic_path = os.path.join('media/profile_pics', f'user_{user_id}_{pic.name}')
                full_path = os.path.join(settings.BASE_DIR, pic_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'wb+') as destination:
                    for chunk in pic.chunks():
                        destination.write(chunk)
                user.profile_picture = '/' + pic_path  # Save relative path for use in src
            user.save()
            return JsonResponse({'success': True, 'user': {
                'name': user.name,
                'email': user.email,
                'phone_number': user.phone_number,
                'room_number': user.room_number,
                'profile_picture': user.profile_picture
            }})
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        title = data.get('title')
        description = data.get('description', '')
        due_date = data.get('due_date')
        priority = data.get('priority', 'Normal')
        status = data.get('status', 'Pending')
        category_id = data.get('category_id')

        try:
            user = Users.objects.get(user_id=user_id)
            category = Categories.objects.get(id=category_id) if category_id else None
            task = Tasks.objects.create(
                user=user,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                status=status,
                category=category
            )
            return JsonResponse({'success': True, 'task_id': task.task_id})
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


@csrf_exempt
def get_shared_tasks(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        shared = SharedTasks.objects.filter(shared_with_user_id=user_id).select_related('task')
        shared_list = [
            {
                'shared_id': s.shared_id,
                'task_id': s.task.task_id,
                'title': s.task.title,
                'description': s.task.description,
                'due_date': s.task.due_date,
                'priority': s.task.priority,
                'status': s.task.status  # <-- This is from Tasks table
            }
            for s in shared
        ]
        return JsonResponse({'success': True, 'shared_tasks': shared_list})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def update_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')
        if new_status not in ['Pending', 'In Progress', 'Completed']:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        try:
            task = Tasks.objects.get(task_id=task_id)
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        except Tasks.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@csrf_exempt
def share_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        shared_with_username = data.get('shared_with_username')
        print("Creating notification for shared task:", task_id, "to", shared_with_username)
        try:
            task = Tasks.objects.get(task_id=task_id)
            user = Users.objects.get(name=shared_with_username)
            shared_task, created = SharedTasks.objects.get_or_create(
                task=task,
                shared_with_user=user,
                defaults={'status': 'Pending'}
            )
            # Only create notification if it doesn't already exist for this shared_task
            notif_exists = Notifications.objects.filter(
                user=user,
                type='Shared Task Request',
                shared=shared_task
            ).exists()
            if not notif_exists:
                Notifications.objects.create(
                    user=user,
                    message=f"{task.user.name} shared a task with you: {task.title}",
                    type='Shared Task Request',
                    shared=shared_task
                )
            return JsonResponse({'success': True, 'shared_id': shared_task.shared_id})
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def update_shared_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        shared_id = data.get('shared_id')
        status = data.get('status')
        try:
            shared_task = SharedTasks.objects.get(shared_id=shared_id)
            shared_task.status = status
            shared_task.save()
            return JsonResponse({'success': True})
        except SharedTasks.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Shared task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def get_tasks_shared_by_me(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        shared = SharedTasks.objects.filter(task__user_id=user_id).select_related('task', 'shared_with_user')
        shared_list = [
            {
                'shared_id': s.shared_id,
                'task_id': s.task.task_id,
                'title': s.task.title,
                'description': s.task.description,
                'due_date': s.task.due_date,
                'priority': s.task.priority,
                'status': s.status,
                'shared_with': s.shared_with_user.name  # or .email
            }
            for s in shared
        ]
        return JsonResponse({'success': True, 'shared_by_me': shared_list})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def get_notifications(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        notifications = Notifications.objects.filter(user_id=user_id).order_by('-created_at')
        notif_list = []
        for n in notifications:
            notif_dict = {
                'notification_id': n.notification_id,
                'message': n.message,
                'type': n.type,
                'read_status': n.read_status,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
            }
            if n.type == 'Shared Task Request' and n.shared:
                notif_dict['shared_id'] = n.shared.shared_id
                notif_dict['shared_status'] = n.shared.status
            notif_list.append(notif_dict)
        return JsonResponse({'success': True, 'notifications': notif_list})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def mark_notification_read(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        notif_id = data.get('notification_id')
        try:
            notif = Notifications.objects.get(notification_id=notif_id)
            notif.read_status = True
            notif.save()
            return JsonResponse({'success': True})
        except Notifications.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def create_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        message = data.get('message')
        notif_type = data.get('type')
        print("Generic notification created:", message)
        # Prevent duplicate shared task notifications
        if notif_type == 'Shared Task Request':
            return JsonResponse({'success': False, 'error': 'Use share_task endpoint for shared task notifications'})
        try:
            user = Users.objects.get(user_id=user_id)
            notif = Notifications.objects.create(user=user, message=message, type=notif_type)
            return JsonResponse({'success': True, 'notification_id': notif.notification_id})
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def update_shared_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        shared_id = data.get('shared_id')
        status = data.get('status')
        allowed_statuses = ['Pending', 'In Progress', 'Completed']
        if status not in allowed_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status value'})
        try:
            shared_task = SharedTasks.objects.get(shared_id=shared_id)
            shared_task.status = status
            shared_task.save()
            return JsonResponse({'success': True})
        except SharedTasks.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Shared task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def respond_shared_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        shared_id = data.get('shared_id')
        action = data.get('action')  # 'Accepted' or 'Declined'
        if action not in ['Accepted', 'Declined']:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        try:
            shared_task = SharedTasks.objects.get(shared_id=shared_id)
            shared_task.status = action
            shared_task.save()
            return JsonResponse({'success': True})
        except SharedTasks.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Shared task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})