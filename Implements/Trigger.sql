-- 1. TRIGGER: Log task changes automatically to Task_Logs table
CREATE TRIGGER trg_TaskChanges
ON Tasks
AFTER UPDATE
AS
BEGIN
    INSERT INTO Task_Logs
        (task_id, changed_by, change_description, changed_at)
    SELECT
        i.task_id,
        i.user_id,
        CONCAT(
            'Status changed from ''', d.status, ''' to ''', i.status, '''',
            CASE WHEN d.priority <> i.priority 
                THEN CONCAT(', priority changed from ''', d.priority, ''' to ''', i.priority, '''') 
                ELSE '' END,
            CASE WHEN d.due_date <> i.due_date 
                THEN CONCAT(', due date changed from ''', CONVERT(VARCHAR, d.due_date, 120), ''' to ''', CONVERT(VARCHAR, i.due_date, 120), '''') 
                ELSE '' END
        ),
        GETDATE()
    FROM inserted i
        JOIN deleted d
        ON i.task_id = d.task_id
    WHERE i.status <> d.status OR i.priority <> d.priority OR i.due_date <> d.due_date;
END;
GO

-- 2. TRIGGER: Create notification when task is shared with a user
CREATE TRIGGER trg_TaskSharedNotification
ON Shared_Tasks
AFTER INSERT
AS
BEGIN
    DECLARE @task_title VARCHAR(255);
    DECLARE @owner_name VARCHAR(255);

    SELECT @task_title = t.title, @owner_name = u.name
    FROM inserted i
        JOIN Tasks t
        ON i.task_id = t.task_id
        JOIN Users u
        ON t.user_id = u.user_id;

    INSERT INTO Notifications
        (user_id, message, type, read_status, created_at)
    SELECT
        i.shared_with_user_id,
        CONCAT('Task "', @task_title, '" has been shared with you by ', @owner_name),
        'Shared Task Request',
        0,
        GETDATE()
    FROM inserted i;
END;
GO

-- 3. TRIGGER: Create notification when task due date is approaching (within 24 hours)
CREATE TRIGGER trg_TaskDueSoonReminder
ON Tasks
AFTER INSERT, UPDATE
AS
BEGIN
    -- Check for tasks due within the next 24 hours
    INSERT INTO Notifications
        (user_id, message, type, read_status, created_at)
    SELECT
        i.user_id,
        CONCAT('Task "', i.title, '" is due soon (', CONVERT(VARCHAR, i.due_date, 120), ')'),
        'Task Reminder',
        0,
        GETDATE()
    FROM inserted i
    WHERE i.due_date IS NOT NULL
        AND i.due_date BETWEEN GETDATE() AND DATEADD(HOUR, 24, GETDATE())
        AND i.status <> 'Completed';
END;
GO

-- 4. TRIGGER: Update task status counts for user when task status changes
CREATE TRIGGER trg_UpdateSessionExpiry
ON Sessions
AFTER INSERT, UPDATE
AS
BEGIN
    -- Automatically expire sessions that are older than 30 days
    UPDATE Sessions
    SET expires_at = CASE 
                        WHEN DATEDIFF(DAY, GETDATE(), expires_at) > 30 
                        THEN DATEADD(DAY, 30, GETDATE())
                        ELSE expires_at
                     END
    WHERE session_id IN (SELECT session_id
    FROM inserted);
END;
GO
