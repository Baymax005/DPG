# 🔧 Quick PostgreSQL Setup Guide

## Update Your Database Connection

Edit the `.env` file and change this line:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/dpg_dev
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

## Create the Database

### Option 1: Using pgAdmin (GUI)
1. Open pgAdmin
2. Right-click on "Databases"
3. Create → Database
4. Name: `dpg_dev`
5. Click Save

### Option 2: Using psql (Command Line)
```powershell
# Connect to PostgreSQL (it will ask for password)
psql -U postgres

# Once connected, run:
CREATE DATABASE dpg_dev;

# Exit
\q
```

### Option 3: Let Python Create It
The database tables will be auto-created when you start the server!
Just make sure the DATABASE_URL in .env is correct.

## Then Start Your Server

```powershell
cd backend
..\venv\Scripts\Activate.ps1
python main.py
```

Your API will be at: http://localhost:8001
