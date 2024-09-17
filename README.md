# Task Tracker Backend

This is a minimal task tracker backend built using FastAPI.\
It provides generic endpoints for creating, reading, updating, and deleting tasks, as well as user authentication and authorization.\
A lot of things could be done better (e.g. project structure breakdown, more roles, constraints on the users/assignee/reporter), but that should be good to go for developer screening :)

## Features

- User authentication and authorization
- CRUD operations for Task management
- Role-based access control (admin and read-only roles)
- JWT token-based authentication
- Email sending mock up to reporter when status of the task is changed

## Requirements

- Docker

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com//task-tracker-backend.git
    cd task-tracker-backend
    ```

2. Build the Docker image:

    ```bash
    docker build -t task_tracker .
    ```

3. Run the Docker container:

    ```bash
    docker run -d -p 8000:8000 --name task_tracker task_tracker
    ```

4. Access the API documentation:

    Open your browser and go to `http://localhost:8000/docs` to see the automatically generated Swagger documentation.

5. First of all you need to create users via /post/users/ endpoint.\
    You can create users with different roles (admin, read-only) and assign them to tasks.\
    Admin can use all endpoints, read-only can only use GET endpoints.
6. Go to the Authorize button on the top right corner of the Swagger UI and enter user email and password to access the endpoints
    ![auth button](./pic/auth_button.png)

## Running Tests

You can also verify basic functionality with the functional tests.\
To run the tests, follow these steps:

1. Install the dependencies:

    ```bash
    poetry install
    ```

2. Run the tests using `pytest`:

    ```bash
    poetry run pytest -v --disable-warnings
    ```

## Environment Variables

The following environment variables can be changed to configure the application (in case needed):

- `DATABASE_URL`: The database URL to connect to (default: `sqlite:///./test.db`).
