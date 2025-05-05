CREATE FUNCTION fn_GetUserTaskCount (
    @user_id INT,
    @status VARCHAR(20) = NULL
)
RETURNS INT
AS
BEGIN
    DECLARE @count INT;

    SELECT @count = COUNT(*)
    FROM Tasks
    WHERE user_id = @user_id
        AND (@status IS NULL OR status = @status);

    RETURN @count;
END;
GO


CREATE FUNCTION fn_GetBuildingOccupancyRate (
    @building_id INT
)
RETURNS DECIMAL(5,2)
AS
BEGIN
    DECLARE @total_rooms INT;
    DECLARE @occupied_rooms INT;
    DECLARE @occupancy_rate DECIMAL(5,2);

    SELECT @total_rooms = total_rooms
    FROM Buildings
    WHERE building_id = @building_id;

    SELECT @occupied_rooms = COUNT(*)
    FROM Users
    WHERE building_id = @building_id;

    IF @total_rooms = 0
        SET @occupancy_rate = 0;
    ELSE
        SET @occupancy_rate = (@occupied_rooms * 100.0) / @total_rooms;

    RETURN @occupancy_rate;
END;
GO


CREATE FUNCTION fn_HasUserUpcomingTasks (
    @user_id INT,
    @days_ahead INT = 7
)
RETURNS BIT
AS
BEGIN
    DECLARE @has_tasks BIT = 0;

    IF EXISTS (
        SELECT 1
    FROM Tasks
    WHERE user_id = @user_id
        AND status <> 'Completed'
        AND due_date BETWEEN GETDATE() AND DATEADD(DAY, @days_ahead, GETDATE())
    )
        SET @has_tasks = 1;

    RETURN @has_tasks;
END;
GO


CREATE FUNCTION fn_CalculateUserProductivity (
    @user_id INT,
    @days_back INT = 30
)
RETURNS DECIMAL(5,2)
AS
BEGIN
    DECLARE @total_tasks INT;
    DECLARE @completed_tasks INT;
    DECLARE @completed_on_time INT;
    DECLARE @productivity_score DECIMAL(5,2);

    -- Get total tasks assigned in the period
    SELECT @total_tasks = COUNT(*)
    FROM Tasks
    WHERE user_id = @user_id
        AND created_at >= DATEADD(DAY, -@days_back, GETDATE());

    -- Get completed tasks in the period
    SELECT @completed_tasks = COUNT(*)
    FROM Tasks
    WHERE user_id = @user_id
        AND status = 'Completed'
        AND created_at >= DATEADD(DAY, -@days_back, GETDATE());

    -- Get tasks completed before due date
    SELECT @completed_on_time = COUNT(*)
    FROM Tasks
    WHERE user_id = @user_id
        AND status = 'Completed'
        AND created_at >= DATEADD(DAY, -@days_back, GETDATE())
        AND (due_date IS NULL OR due_date >= created_at);

    -- Calculate productivity score (50% completion rate, 50% on-time rate)
    IF @total_tasks = 0
        SET @productivity_score = 0;
    ELSE
        SET @productivity_score = (
            (@completed_tasks * 100.0 / @total_tasks) * 0.5 +
            (CASE WHEN @completed_tasks = 0 THEN 0 
                 ELSE (@completed_on_time * 100.0 / @completed_tasks) END) * 0.5
        );

    RETURN @productivity_score;
END;
GO

