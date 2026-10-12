# Complaint and Feedback Management System

A web-based Complaint and Feedback Management System built with Python and Flask. The system allows users to submit complaints, track their status, and receive updates, while administrators manage complaints, categories, and users.

## Features

### User Features
- User registration and login
- Submit complaints with a title, description, category, and optional image
- Track complaint status
- View administrator responses
- Receive notifications about complaint updates
- Manage account information

### Administrator Features
- View and manage submitted complaints
- Respond to complaints
- Update complaint status: Pending, In Progress, and Resolved
- Manage complaint categories
- Manage users and administrator privileges
- View dashboard statistics
- Send notifications to users through complaint updates

## Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **ORM:** Flask-SQLAlchemy
- **Authentication:** Flask-Login, Flask-Bcrypt
- **Forms and Validation:** Flask-WTF, WTForms
- **Frontend:** HTML, CSS, JavaScript, Jinja2

## Requirements

- Python 3
- pip
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jasoncs38/Comp_management.git
cd Comp_management
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows (Command Prompt):**

```bash
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize the Database

The database is not included in the repository. Create the database tables locally before running the application.

Open the Flask shell:

```bash
flask --app run.py shell
```

Then execute:

```python
from comp_management import db
db.create_all()
```

Exit the shell:

```python
exit()
```

This creates the database tables defined by the application models. It does not create sample users or populate the database with categories.

### 6. Run the Application

```bash
python run.py
```

Open the local address displayed in the terminal in your browser. It is commonly:

`http://127.0.0.1:5000/`

## First-Time Use

## First-Time Setup

A fresh installation requires an administrator account and complaint categories before the system can be used fully.

### 1. Create a User Account

Start the application and register an account through the registration page.

Stop the application after registering.

### 2. Promote the Account to Administrator

From the project directory, with the virtual environment activated, open the Flask shell:

```bash
flask --app run.py shell
```

Run the following Python commands, replacing the email with the email address used during registration:

```python
from comp_management.models import User
from comp_management import db

user = User.query.filter_by(email="your-email@example.com").first()

if user:
    user.is_admin = True
    user.is_main_admin = True
    db.session.commit()
    print("Administrator account created successfully.")
else:
    print("User not found. Check the registered email address.")
```

Exit the shell:

```python
exit()
```

The account now has administrator and main-administrator privileges.

**Security note:** Only grant these privileges to an account you control. This procedure is intended for local development setup.

### 3. Create Complaint Categories

Start the application again and log in using the administrator account.

Open the category management page and create the categories needed by your organization, such as:

- Electrical
- Network
- Maintenance
- Other

Make sure an `Other` category exists if the application relies on it when a category is deleted.

### 4. Start Using the System

Once the administrator account and categories are configured, users can register, submit complaints, and track their progress. The administrator can manage complaints and respond to users.


## Database

The application uses SQLite for local development. The database file is excluded from GitHub, so each person running the project starts with their own database.

Uploaded complaint images and local instance files are also excluded from version control.

## Project Structure

```text
Comp_management/
├── comp_management/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── static/
│   └── templates/
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Notes

- This project is intended for educational and development purposes.
- A fresh installation requires database initialization and any necessary initial configuration.
- Do not commit passwords, secret keys, private user information, or production database files to the repository.

## Author

Developed as a Complaint and Feedback Management System project using Flask and Python.
