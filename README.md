---

# Health Information System

## Description

The **Health Information System** is a full-stack application designed to efficiently manage clients, health programs, and enrollments. It streamlines administrative health processes for doctors and health organizations. The system includes robust features for program management, client management, and program enrollment, along with secure API access for external integrations.

This system is ideal for small to medium-sized healthcare organizations looking to digitize their operations without the complexity or cost of large-scale enterprise solutions. It emphasizes security, ease of use, and scalability, making it a robust starting point for managing health program data effectively.

---

## Live Demo

You can access the live site for demonstration purposes using this link:  
[Health Information System Live](https://health-system-1-x9p6.onrender.com)

---

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Test Users and Credentials](#test-users-and-credentials)
7. [Database Schema](#database-schema)
8. [Running Tests](#running-tests)
9. [Known Issues](#known-issues)
10. [Future Roadmap](#future-roadmap)
11. [Acknowledgments](#acknowledgments)

---

## Features

1. **Health Program Management**
   - Create, view, and edit health programs (e.g., TB, Malaria, HIV).
   - Store detailed information about each program for easy reporting and analysis.

2. **Client Management**
   - Register new clients with personal information.
   - Search for clients by name or ID number.
   - View detailed client profiles.

3. **Program Enrollment**
   - Enroll clients in one or more health programs.
   - Update their enrollment statuses (Active, Inactive, Completed).

4. **API Access**
   - Expose client profiles via secure API endpoints.
   - Restrict access using API keys for enhanced security.

---

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

---

## Installation

Follow these steps to set up the Health Information System locally:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ARMSTRONGOPONDO/health-system.git
   cd health-system
   ```

2. **Set Up a Python Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   flask init-db
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

---

## Usage

### Access the Application
- Open your browser and navigate to `http://127.0.0.1:5000`.

### Health Program Management
- Use the dashboard to create, view, and manage health programs.

### Client Management
- Add new clients and search for existing ones by name or ID.

### Program Enrollment
- Enroll clients into health programs and update their statuses.

### API Access
- Use the provided API endpoints to access client data programmatically. Ensure you have an API key for authentication.

---

## API Documentation

The Health Information System provides secure API endpoints for accessing client data. Below are the details:

**Base URL**: `http://127.0.0.1:5000/api` (or the live demo URL)

### Example Endpoints

1. **Get All Clients**
   - `GET /clients`
   - Requires API key in the header (`X-API-Key`).
   - Response:
     ```json
     [
       {
         "id": 1,
         "name": "John Doe",
         "id_number": "123456",
         "date_of_birth": "1990-01-01",
         "gender": "Male",
         "contact": "555-1234",
         "address": "123 Main Street"
       }
     ]
     ```

2. **Get Client by ID**
   - `GET /clients/{id}`
   - Replace `{id}` with the client ID.
   - Requires API key in the header.

**Important**: Use the API key provided in the [Test Users and Credentials](#test-users-and-credentials) section.

---

## Test Users and Credentials

The Health Information System includes pre-configured test users for testing purposes. Below are the test users, their roles, plaintext passwords for login, and their hashed passwords as securely stored in the database:

| **Name**             | **Username**       | **Role**          | **Password (Plaintext)** | **Password (Hashed)**                                                                                               | **API Key**       |
|-----------------------|--------------------|-------------------|---------------------------|---------------------------------------------------------------------------------------------------------------------|-------------------|
| Doctor Testing        | Docter Testing    | Doctor            | `password`               | `pbkdf2:sha256$600000$k9j4JWcK9Z6xEh9G$5e2f9c2f0f921b7fbe2bae38bff45a7a1e2a9bde88b4a8a685f27f7d6f8bcd76`             | doctor_api_key    |
| Administrator Testing | Admin Testing     | Administrator      | `password`               | `pbkdf2:sha256$600000$k9j4JWcK9Z6xEh9G$5e2f9c2f0f921b7fbe2bae38bff45a7a1e2a9bde88b4a8a685f27f7d6f8bcd76`             | admin_api_key     |

---

## Database Schema

The Health Information System uses an SQLite database with the following schema:

- **`users` table**: Stores user information (username, hashed password, API key).
- **`clients` table**: Stores client details such as name, ID number, and contact information.
- **`programs` table**: Stores health program details.
- **`enrollments` table**: Links clients and programs, tracking enrollment status.

---

## Running Tests

To ensure the application works correctly, you can run the included tests:

```bash
pytest tests/
```

This will execute all the unit tests and provide a summary of the results.

---

## Known Issues

- The live demo link may experience downtime due to free-tier hosting limitations.
- Currently, the system does not support multi-language localization.

---

## Future Roadmap

- Add user authentication and role-based access control.
- Integrate SMS/email notifications for clients.
- Provide advanced analytics and reporting tools for administrators.

---

## Acknowledgments

- **Flask**: For building the backend.
- **SQLite**: For database management.
- **Render**: For hosting the live demo.


---
