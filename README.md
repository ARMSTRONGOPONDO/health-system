Health Information System

A basic health information system for managing clients and health programs/services. This system allows doctors to manage clients, health programs, and enrollments.
Features

    Health Program Management
        Create health programs (e.g., TB, Malaria, HIV)
        View and edit existing programs

    Client Management
        Register new clients with personal information
        Search for clients by name or ID number
        View client profiles

    Program Enrollment
        Enroll clients in one or more health programs
        Update enrollment status (Active, Inactive, Completed)

    API Access
        Expose client profiles via API endpoints
        Secure API access with API keys

Technology Stack

    Backend: Flask (Python)
    Database: SQLite
    Frontend: HTML, CSS, JavaScript


    flask init-db to initialize the database in the commandline
    python -m venv venv to create a venv
    source venv/bin/activate to activate the enviroment
    run health-system/app.py
