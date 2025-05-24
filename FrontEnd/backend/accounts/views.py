from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users  # Use your custom Users model
from .models import Tasks  # Use your custom Users model
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
        return JsonResponse({'tasks': tasks})
    
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
