from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users  # Use your custom Users model
from .models import Tasks  # Use your custom Users model

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
            return JsonResponse({'success': True})
        except Users.DoesNotExist:
            print("Login failed for username:", username)
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_tasks(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        tasks = list(Tasks.objects.filter(user_id=user_id).values())
        return JsonResponse({'tasks': tasks})
    



