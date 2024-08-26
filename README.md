# CodeCheckerAI Project

## Overview

CodeCheckerAI is a web application consisting of a backend built with Django and a frontend developed with React. This README provides instructions for setting up and running both components of the project.

## Project Structure

- **Backend**: A Django-based server.
- **Frontend**: A React-based client application.

## Backend Setup

### Prerequisites

- Python 3.8 or later
- `pip` for Python package management

### Installation

1. **Navigate to the Backend Directory**

   Open your terminal in Visual Studio Code and change to the `backend` directory:
   ```bash
   cd CodeCheckerAI-/backend

2. **Create and Activate a Virtual Environment**

    Create a virtual environment if you haven't already:
    ```bash
    python -m venv venv

### Activate the Virtual Environment

Activate the virtual environment:

- **On Windows:**
  ```bash
  venv\Scripts\activate


- **On macOS/Linux:** 
  ```bash
 source venv/bin/activate


3. **Install Dependencies**
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt


4. **Run the Django Server**

    Start the development server:
    ```bash
    python manage.py runserver

The server will be available at http://127.0.0.1:8000/.

## Additional Information

- **Checking URLs**: For information on the various URLs used by the web application, refer to the `utils.py` file. This file contains definitions for different URLs and endpoints utilized throughout the application.



## Frontend Setup

### Prerequisites

- Node.js (v16 or later) and npm

### Installation

1. **Navigate to the Frontend Directory**

    Open your terminal in Visual Studio Code and change to the frontend directory:
    ```bash
    cd CodeCheckerAI-/frontend

2. **Install Dependencies**

    Install the required npm packages:
    ```bash
    npm install


3. **Run the React Development Server**

    Start the development server:
    ```bash
    npm start

The application will be available at http://localhost:3000.

## Additional Notes
- Ensure you have the correct environment variables set up for both the backend and frontend if needed.
- Regularly check for updates in the dependencies for both backend and frontend.



