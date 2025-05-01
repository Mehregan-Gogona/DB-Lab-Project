-- 1. PROCEDURE: Register a new user
CREATE PROCEDURE sp_CreateNewUser
    @name VARCHAR(255),
    @email VARCHAR(255),
    @password VARCHAR(255),
    @room_number VARCHAR(20) = NULL,
    @building_id INT = NULL,
    @phone_number VARCHAR(20) = NULL,
    @profile_picture VARCHAR(255) = NULL
AS
BEGIN
    -- Check if email already exists
    IF EXISTS (SELECT 1
    FROM Users
    WHERE email = @email)
    BEGIN
        RAISERROR('Email already registered', 16, 1)
        RETURN -1
    END

    -- Insert new user
    INSERT INTO Users
        (name, email, password, room_number, building_id, phone_number, profile_picture, created_at)
    VALUES
        (@name, @email, @password, @room_number, @building_id, @phone_number, @profile_picture, GETDATE())

    -- Return the new user ID
    RETURN SCOPE_IDENTITY()
END;
GO

-- 2. PROCEDURE: Create and assign a new task
CREATE PROCEDURE sp_CreateTask
    @user_id INT,
    @title VARCHAR(255),
    @description VARCHAR(MAX) = NULL,
    @due_date DATETIME = NULL,
    @priority VARCHAR(10) = 'Medium',
    @category_id INT = NULL
AS
BEGIN
    -- Validate parameters
    IF NOT EXISTS (SELECT 1
    FROM Users
    WHERE user_id = @user_id)
    BEGIN
        RAISERROR('User not found', 16, 1)
        RETURN -1
    END

    IF @category_id IS NOT NULL AND NOT EXISTS (SELECT 1
        FROM Categories
        WHERE category_id = @category_id)
    BEGIN
        RAISERROR('Category not found', 16, 1)
        RETURN -2
    END

    -- Insert new task
    INSERT INTO Tasks
        (user_id, title, description, due_date, priority, status, category_id, created_at)
    VALUES
        (@user_id, @title, @description, @due_date, @priority, 'Pending', @category_id, GETDATE())

    -- Return the new task ID
    RETURN SCOPE_IDENTITY()
END;
GO

-- 3. PROCEDURE: Share a task with another user
CREATE PROCEDURE sp_ShareTaskWithUser
    @task_id INT,
    @shared_with_user_id INT,
    @current_user_id INT
AS
BEGIN
    -- Validate task ownership
    IF NOT EXISTS (SELECT 1
    FROM Tasks
    WHERE task_id = @task_id AND user_id = @current_user_id)
    BEGIN
        RAISERROR('Task not found or you do not have permission to share it', 16, 1)
        RETURN -1
    END

    -- Check if user exists
    IF NOT EXISTS (SELECT 1
    FROM Users
    WHERE user_id = @shared_with_user_id)
    BEGIN
        RAISERROR('User to share with not found', 16, 1)
        RETURN -2
    END

    -- Check if task is already shared with this user
    IF EXISTS (SELECT 1
    FROM Shared_Tasks
    WHERE task_id = @task_id AND shared_with_user_id = @shared_with_user_id)
    BEGIN
        RAISERROR('Task is already shared with this user', 16, 1)
        RETURN -3
    END

    -- Share the task
    INSERT INTO Shared_Tasks
        (task_id, shared_with_user_id, status)
    VALUES
        (@task_id, @shared_with_user_id, 'Pending')

    -- Return the shared task ID
    RETURN SCOPE_IDENTITY()
END;
GO

-- 4. PROCEDURE: Update task status and log the change
CREATE PROCEDURE sp_UpdateTaskStatus
    @task_id INT,
    @status VARCHAR(20),
    @user_id INT
AS
BEGIN
    -- Check if task exists and user has permission
    IF NOT EXISTS (
        SELECT 1
    FROM Tasks
    WHERE task_id = @task_id
        AND (user_id = @user_id OR EXISTS (
            SELECT 1
        FROM Shared_Tasks
        WHERE task_id = @task_id
            AND shared_with_user_id = @user_id
            AND status = 'Accepted'
        ))
    )
    BEGIN
        RAISERROR('Task not found or you do not have permission to update it', 16, 1)
        RETURN -1
    END

    -- Get current status for logging
    DECLARE @old_status VARCHAR(20)
    SELECT @old_status = status
    FROM Tasks
    WHERE task_id = @task_id

    -- Update the task status
    UPDATE Tasks
    SET status = @status
    WHERE task_id = @task_id

    -- Log the change
    INSERT INTO Task_Logs
        (task_id, changed_by, change_description, changed_at)
    VALUES
        (@task_id, @user_id, CONCAT('Status changed from ''', @old_status, ''' to ''', @status, ''''), GETDATE())

    RETURN 0
END;
GO

-- 5. PROCEDURE: Get user's tasks with filtering options
CREATE PROCEDURE sp_GetUserTasks
    @user_id INT,
    @status VARCHAR(20) = NULL,
    @priority VARCHAR(10) = NULL,
    @category_id INT = NULL
AS
BEGIN
    SELECT
        t.task_id,
        t.title,
        t.description,
        t.due_date,
        t.priority,
        t.status,
        c.category_name,
        t.created_at
    FROM Tasks t
        LEFT JOIN Categories c ON t.category_id = c.category_id
    WHERE t.user_id = @user_id
        AND (@status IS NULL OR t.status = @status)
        AND (@priority IS NULL OR t.priority = @priority)
        AND (@category_id IS NULL OR t.category_id = @category_id)
    ORDER BY 
        CASE 
            WHEN t.status = 'Pending' THEN 1
            WHEN t.status = 'In Progress' THEN 2
            ELSE 3
        END,
        CASE 
            WHEN t.priority = 'High' THEN 1
            WHEN t.priority = 'Medium' THEN 2
            ELSE 3
        END,
        t.due_date
END;
GO
