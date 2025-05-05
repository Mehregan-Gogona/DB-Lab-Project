CREATE VIEW v_UserTaskSummary
AS
    SELECT
        u.user_id,
        u.name,
        u.email,
        u.room_number,
        b.building_name,
        COUNT(t.task_id) AS total_tasks,
        SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks,
        SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_tasks,
        SUM(CASE WHEN t.status = 'Pending' THEN 1 ELSE 0 END) AS pending_tasks,
        SUM(CASE WHEN t.priority = 'High' THEN 1 ELSE 0 END) AS high_priority_tasks,
        SUM(CASE WHEN t.due_date < GETDATE() AND t.status <> 'Completed' THEN 1 ELSE 0 END) AS overdue_tasks
    FROM Users u
        LEFT JOIN Buildings b ON u.building_id = b.building_id
        LEFT JOIN Tasks t ON u.user_id = t.user_id
    GROUP BY u.user_id, u.name, u.email, u.room_number, b.building_name;
GO


CREATE VIEW v_PendingTasksWithDetails
AS
    SELECT
        t.task_id,
        t.title,
        t.description,
        t.priority,
        t.due_date,
        DATEDIFF(DAY, GETDATE(), t.due_date) AS days_remaining,
        u.name AS owner_name,
        u.email AS owner_email,
        c.category_name,
        t.created_at
    FROM Tasks t
        JOIN Users u ON t.user_id = u.user_id
        LEFT JOIN Categories c ON t.category_id = c.category_id
    WHERE t.status = 'Pending'
        AND t.due_date > GETDATE();
GO


CREATE VIEW v_BuildingOccupancy
AS
    SELECT
        b.building_id,
        b.building_name,
        b.location,
        b.total_rooms,
        COUNT(u.user_id) AS occupied_rooms,
        b.total_rooms - COUNT(u.user_id) AS available_rooms,
        CAST(COUNT(u.user_id) * 100.0 / NULLIF(b.total_rooms, 0) AS DECIMAL(5,2)) AS occupancy_rate
    FROM Buildings b
        LEFT JOIN Users u ON b.building_id = u.building_id
    GROUP BY b.building_id, b.building_name, b.location, b.total_rooms;
GO


CREATE VIEW v_SharedTasksWithUserInfo
AS
    SELECT
        st.shared_id,
        t.task_id,
        t.title AS task_title,
        t.description,
        t.due_date,
        t.priority,
        st.status AS sharing_status,
        owner.user_id AS owner_id,
        owner.name AS owner_name,
        owner.email AS owner_email,
        shared.user_id AS shared_with_id,
        shared.name AS shared_with_name,
        shared.email AS shared_with_email
    FROM Shared_Tasks st
        JOIN Tasks t ON st.task_id = t.task_id
        JOIN Users owner ON t.user_id = owner.user_id
        JOIN Users shared ON st.shared_with_user_id = shared.user_id;
GO

