# Virtual Group Concepts

A simple group chat application built with Flask, SQLAlchemy, and other technologies.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Flask Chat App is designed to provide users with a platform for creating groups, joining discussions, and sharing messages. Users can create their profiles, update their bio, and even upload profile pictures. The application uses Flask for the web framework, SQLAlchemy as the database ORM, and integrates Flask-Login for user authentication.

## Features

- User Registration and Authentication
- Profile Management
- Group Creation and Joining
- Real-time Chat Messaging
- Activity Tracking
- ...

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python installed (version 3.12.1)
- SQLite or another relational database system
- Pipenv installed (for dependency management)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Andrewtanui/0x1chatapp.git
   ```

2. Navigate to the project directory:

   ```bash
   cd 0x1chatapp
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Usage

1. Run the development server:

   ```bash
   flask run
   ```

2. Open your web browser and go to `http://localhost:5000`.

3. Explore the different features of the application, such as user registration, profile management, group creation, and chat messaging.

## Contributing

Contributions are welcome! Please follow the [contribution guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

---
