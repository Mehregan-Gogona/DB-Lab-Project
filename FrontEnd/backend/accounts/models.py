from django.db import models

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    room_number = models.CharField(max_length=20, null=True, blank=True)
    building_id = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'Users'
        managed = False  # Because the table already exists

class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'Categories'
        managed = False

class Tasks(models.Model):
    task_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='Pending')
    category = models.ForeignKey(Categories, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'Tasks'
        managed = False  # If table already exists



# ...existing code...

class SharedTasks(models.Model):
    shared_id = models.AutoField(primary_key=True)
    task = models.ForeignKey('Tasks', on_delete=models.CASCADE, db_column='task_id')
    shared_with_user = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='shared_with_user_id')
    status = models.CharField(max_length=20, default='Pending')

    class Meta:
        db_table = 'Shared_Tasks'
        managed = False  




class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_id')
    message = models.TextField()
    type = models.CharField(max_length=25)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    shared = models.ForeignKey('SharedTasks', null=True, blank=True, on_delete=models.CASCADE, db_column='shared_id')  # <-- Add this

    class Meta:
        db_table = 'Notifications'
        managed = False