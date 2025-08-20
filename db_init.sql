-- Database schema for Shift Handover App (MySQL)

CREATE TABLE account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'active'
);

CREATE TABLE team (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'active',
    account_id INT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES account(id)
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'active',
    account_id INT,
    team_id INT,
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE team_member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(64) NOT NULL,
    email VARCHAR(120) NOT NULL,
    contact_number VARCHAR(32) NOT NULL,
    role VARCHAR(64),
    account_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE escalation_matrix_file (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    upload_time DATETIME NOT NULL,
    account_id INT,
    team_id INT,
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE shift_roster (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    team_member_id INT NOT NULL,
    shift_code VARCHAR(8),
    account_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (team_member_id) REFERENCES team_member(id),
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE shift (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    current_shift_type VARCHAR(16) NOT NULL,
    next_shift_type VARCHAR(16) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'draft',
    account_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE incident (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL,
    priority VARCHAR(16) NOT NULL,
    handover TEXT,
    shift_id INT,
    type VARCHAR(32) NOT NULL,
    account_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (shift_id) REFERENCES shift(id),
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE shift_key_point (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NOT NULL,
    status VARCHAR(16) NOT NULL,
    responsible_engineer_id INT,
    shift_id INT,
    jira_id VARCHAR(64),
    account_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (responsible_engineer_id) REFERENCES team_member(id),
    FOREIGN KEY (shift_id) REFERENCES shift(id),
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (team_id) REFERENCES team(id)
);

CREATE TABLE shift_key_point_update (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_point_id INT NOT NULL,
    update_text TEXT NOT NULL,
    update_date DATE NOT NULL,
    updated_by VARCHAR(64) NOT NULL,
    FOREIGN KEY (key_point_id) REFERENCES shift_key_point(id)
);

CREATE TABLE current_shift_engineers (
    shift_id INT,
    team_member_id INT,
    FOREIGN KEY (shift_id) REFERENCES shift(id),
    FOREIGN KEY (team_member_id) REFERENCES team_member(id)
);

CREATE TABLE next_shift_engineers (
    shift_id INT,
    team_member_id INT,
    FOREIGN KEY (shift_id) REFERENCES shift(id),
    FOREIGN KEY (team_member_id) REFERENCES team_member(id)
);

-- Initial data
INSERT INTO account (name, is_active, status) VALUES ('Alpha Corp', TRUE, 'active');
INSERT INTO account (name, is_active, status) VALUES ('Beta Inc', TRUE, 'active');

INSERT INTO team (name, is_active, status, account_id) VALUES ('Alpha Team', TRUE, 'active', 1);
INSERT INTO team (name, is_active, status, account_id) VALUES ('Beta Team', TRUE, 'active', 2);

INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id) VALUES ('superadmin', 'superadmin@example.com', 'hashedpassword', 'super_admin', TRUE, 'active', 1, 1);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id) VALUES ('accadmin2', 'accadmin2@example.com', 'hashedpassword', 'account_admin', TRUE, 'active', 2, 2);

INSERT INTO team_member (user_id, name, email, contact_number, role, account_id, team_id) VALUES (1, 'Alice', 'alice@example.com', '1234567890', 'Engineer', 1, 1);
INSERT INTO team_member (user_id, name, email, contact_number, role, account_id, team_id) VALUES (2, 'Bob', 'bob@example.com', '0987654321', 'Engineer', 2, 2);
