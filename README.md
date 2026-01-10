# FlexR

FlexR is a web application aimed at gyms, focused on centralized management of members and internal data. The project is currently under development and serves as a practical learning project combining backend development, authentication, and persistence.

## Screenshots

### Create account
<img width="1862" height="971" alt="Register" src="https://github.com/user-attachments/assets/afb59888-cf50-4b2a-b993-374351550c0f" />

### Member list

<img width="1857" height="969" alt="Member_List" src="https://github.com/user-attachments/assets/294af190-6705-46c2-ac25-e3b59acb3ac8" />

### New member

<img width="1860" height="973" alt="New_Member" src="https://github.com/user-attachments/assets/f84dbdff-e8f5-4192-83d3-0b61c747ac98" />

### Member information

<img width="1855" height="969" alt="Member_Info" src="https://github.com/user-attachments/assets/e5f6f9d7-6c5c-43e1-94a6-9c374cad3cf7" />

### Reception

<img width="1859" height="970" alt="Reception" src="https://github.com/user-attachments/assets/047ac9f7-1337-4d7a-98a8-6d989e113747" />

## Features

* Gym registration and authentication
* Secure login with salted and hashed passwords
* Member creation, update, and deletion
* Centralized member management (activity status, routines, payments – planned)
* Session persistence
* SQLite database

## Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite
* **Authentication:** Session-based authentication
* **Security:** Password hashing with salt

## Project Status

FlexR is currently **in development**. Some features are implemented, while others are planned or partially completed.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/flexr.git
   cd flexr
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux / macOS
   venv\\Scripts\\activate     # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   flask run
   ```

5. Open your browser at:

   ```
   http://127.0.0.1:5000
   ```

## Database

The application uses an SQLite database stored locally. Database initialization and schema are handled within the project.

## Security Notes

* Passwords are never stored in plain text.
* Passwords are salted and hashed before being saved to the database.
* Sessions are used to maintain authentication state.
