CREATE TABLE Buildings
(
    building_id INT PRIMARY KEY IDENTITY(1,1),
    building_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    total_rooms INT NOT NULL
);


CREATE TABLE Users
(
    user_id INT PRIMARY KEY IDENTITY(1,1),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    room_number VARCHAR(20),
    building_id INT,
    phone_number VARCHAR(20),
    profile_picture VARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (building_id) REFERENCES Buildings(building_id)
);


CREATE TABLE Categories
(
    category_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Tasks
(
    task_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(MAX),
    due_date DATETIME,
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Completed')),
    category_id INT,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);


CREATE TABLE Shared_Tasks
(
    shared_id INT PRIMARY KEY IDENTITY(1,1),
    task_id INT NOT NULL,
    shared_with_user_id INT NOT NULL,
    status VARCHAR(10) DEFAULT 'Pending' CHECK (status IN ('Accepted', 'Declined', 'Pending')),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (shared_with_user_id) REFERENCES Users(user_id)
);


CREATE TABLE Notifications
(
    notification_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(25) NOT NULL CHECK (type IN ('Task Reminder', 'Shared Task Request')),
    read_status BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Sessions
(
    session_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Task_Logs
(
    log_id INT PRIMARY KEY IDENTITY(1,1),
    task_id INT NOT NULL,
    changed_by INT NOT NULL,
    change_description TEXT NOT NULL,
    changed_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (changed_by) REFERENCES Users(user_id)
);


CREATE TABLE Attachments
(
    attachment_id INT PRIMARY KEY IDENTITY(1,1),
    task_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
);

