-- Database schema and initial data for Shift Handover App (MySQL)

-- Table definitions (same as previous)
-- ...existing code...

-- Initial data
INSERT INTO account (name, is_active, status) VALUES ('Acme Corp', TRUE, 'active');
INSERT INTO account (name, is_active, status) VALUES ('Beta Inc', TRUE, 'active');

INSERT INTO team (name, is_active, status, account_id) VALUES ('Acme Corp Team A', TRUE, 'active', 1);
INSERT INTO team (name, is_active, status, account_id) VALUES ('Acme Corp Team B', TRUE, 'active', 1);
INSERT INTO team (name, is_active, status, account_id) VALUES ('Beta Inc Team A', TRUE, 'active', 2);
INSERT INTO team (name, is_active, status, account_id) VALUES ('Beta Inc Team B', TRUE, 'active', 2);

-- Passwords are hashed using MySQL's SHA2 function for demonstration
-- Replace with your app's hash logic if needed

INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('superadmin', 'superadmin@example.com', SHA2('superadmin123', 256), 'super_admin', TRUE, 'active', NULL, NULL);

INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('accadmin1', 'accadmin1@example.com', SHA2('accadmin1123', 256), 'account_admin', TRUE, 'active', 1, NULL);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('accadmin2', 'accadmin2@example.com', SHA2('accadmin2123', 256), 'account_admin', TRUE, 'active', 2, NULL);

INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_a_admin', 'acme_corp_team_a_admin@example.com', SHA2('admin123', 256), 'team_admin', TRUE, 'active', 1, 1);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_b_admin', 'acme_corp_team_b_admin@example.com', SHA2('admin123', 256), 'team_admin', TRUE, 'active', 1, 2);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_a_admin', 'beta_inc_team_a_admin@example.com', SHA2('admin123', 256), 'team_admin', TRUE, 'active', 2, 3);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_b_admin', 'beta_inc_team_b_admin@example.com', SHA2('admin123', 256), 'team_admin', TRUE, 'active', 2, 4);

INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_a_user1', 'acme_corp_team_a_user1@example.com', SHA2('user1123', 256), 'user', TRUE, 'active', 1, 1);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_a_user2', 'acme_corp_team_a_user2@example.com', SHA2('user2123', 256), 'user', TRUE, 'active', 1, 1);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_b_user1', 'acme_corp_team_b_user1@example.com', SHA2('user1123', 256), 'user', TRUE, 'active', 1, 2);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('acme_corp_team_b_user2', 'acme_corp_team_b_user2@example.com', SHA2('user2123', 256), 'user', TRUE, 'active', 1, 2);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_a_user1', 'beta_inc_team_a_user1@example.com', SHA2('user1123', 256), 'user', TRUE, 'active', 2, 3);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_a_user2', 'beta_inc_team_a_user2@example.com', SHA2('user2123', 256), 'user', TRUE, 'active', 2, 3);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_b_user1', 'beta_inc_team_b_user1@example.com', SHA2('user1123', 256), 'user', TRUE, 'active', 2, 4);
INSERT INTO user (username, email, password, role, is_active, status, account_id, team_id)
VALUES ('beta_inc_team_b_user2', 'beta_inc_team_b_user2@example.com', SHA2('user2123', 256), 'user', TRUE, 'active', 2, 4);

-- Team Members (IDs must match inserted user IDs)
-- Example for Acme Corp Team A
INSERT INTO team_member (user_id, name, email, contact_number, role, account_id, team_id)
VALUES (3, 'acme_corp_team_a_admin', 'acme_corp_team_a_admin@example.com', '1111111111', 'Team Admin', 1, 1);
INSERT INTO team_member (user_id, name, email, contact_number, role, account_id, team_id)
VALUES (5, 'acme_corp_team_a_user1', 'acme_corp_team_a_user1@example.com', '1111111112', 'Engineer', 1, 1);
INSERT INTO team_member (user_id, name, email, contact_number, role, account_id, team_id)
VALUES (6, 'acme_corp_team_a_user2', 'acme_corp_team_a_user2@example.com', '1111111113', 'Engineer', 1, 1);
-- Repeat for other teams as needed
