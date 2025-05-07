DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS programs;
DROP TABLE IF EXISTS enrollments;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  api_key TEXT UNIQUE NOT NULL
);

CREATE TABLE clients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  id_number TEXT UNIQUE NOT NULL,
  date_of_birth TEXT NOT NULL,
  gender TEXT NOT NULL,
  contact TEXT,
  address TEXT
);

CREATE TABLE programs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE enrollments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_id INTEGER NOT NULL,
  program_id INTEGER NOT NULL,
  enrollment_date TEXT NOT NULL,
  status TEXT NOT NULL,
  FOREIGN KEY (client_id) REFERENCES clients (id),
  FOREIGN KEY (program_id) REFERENCES programs (id)
);

-- Insert default Admin user with password 'admin123'
INSERT INTO users (username, password, api_key)
VALUES ('Admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'test_api_key_12345');

-- Insert sample programs
INSERT INTO programs (name, description)
VALUES 
  ('TB', 'Tuberculosis Treatment Program'),
  ('Malaria', 'Malaria Prevention and Treatment'),
  ('HIV', 'HIV/AIDS Management Program');
