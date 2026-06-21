# Enterprise Banking Management System

An enterprise-grade Banking Management System built with **FastAPI**, Postgresql, and **SQLAlchemy ORM**. This project demonstrates scalable backend architecture, robust security practices, and real-world financial transaction management.

## 🚀 Key Features

### 🏦 Core Banking Operations
- **Onboarding & Accounts**: Customer registration and creation of Savings/Current accounts.
- **Financial Transactions**: Real-time deposits, withdrawals, and atomic fund transfers.
- **Statement & History**: Paginated transaction history and automated analytic summaries.
- **Loan Management**: Multi-step loan application and approval workflow with EMI calculation.

### 🛡️ Enterprise-Grade Security
- **MFA (Multi-factor Authentication)**: TOTP-based secondary security layer (Google Authenticator compatible).
- **Refresh Token Rotation**: Advanced JWT security to prevent stale token hijacking.
- **RBAC (Role-Based Access Control)**: Granular permissions for Admin, Employee, and Customer.
- **Account Lockout**: Automated protection against brute-force attacks.
- **Data Integrity**: Full ACID compliance using database transactions and PostgreSQL functions.

### 🏦 Advanced Banking Features
- **Fixed Deposits (FD)**: Term-based savings with calculated maturity and interest.
- **Credit Cards**: Integrated card management, limits, and outstanding tracking.
- **UPI Integration**: Simulated peer-to-peer VPA payments.
- **Statement Reporting**: Dynamic generation of **PDF Bank Statements** and **Excel Transaction Reports**.
- **Scheduled Payments**: Automated recurring transfers (Simulation).

### 🤖 Intelligent Automation
- **Fraud Detection**: Real-time inspection of transactions for suspicious activities.
- **Background Tasks**: Automated monthly interest calculation for savings accounts using `APScheduler`.
- **Notifications**: Automated logging and simulation of email alerts for transactions.

## 🛠️ Tech Stack
- **Framework**: FastAPI
- **Database**: postgresql
- **ORM**: SQLAlchemy
- **Security**: jose (JWT), Passlib (Bcrypt), SlowAPI (Rate Limiting)
- **Task Scheduling**: APScheduler
- **Testing**: Pytest

## 📂 Project Structure
```text
/app
  /api/v1      # Versioned RESTful API routes
  /core        # Config, Security, Logging, and Task Scheduler
  /db          # Connection strings and Session management
  /models      # SQLAlchemy Entities
  /schemas     # Pydantic data validation models
  /repositories# Database Access Object (DAO) layer
  /services    # Complex Business Logic layer
  /utils       # Calculators and Pagination helpers
/tests         # Pytest test suite
/logs          # Persistent log files
main.py        # App entry point
database_schema.sql # PostgreSQL DDL & Stored Procedures
```

## 🚥 Getting Started

### 1. Prerequisites
- Python 3.9+ and a PostgreSQL instance (pgAdmin recommended).

### 2. Installation
```bash
git clone <repo_url>
cd python_banking_management_system
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file based on the template:
```env
# PostgreSQL Connection
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_DB=banking_db
# JWT Secret
SECRET_KEY=generate_random_string
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

## 🧪 Testing
Run the comprehensive test suite:
```bash
pytest
```

## 📈 Portfolio Summary
This system follows a professional **Layered Architecture**, separating concerns between the presentation (API), logic (Service), and data (Repository) layers. It showcases clean code principles, robust error handling, and sophisticated database designs suitable for modern fintech applications.
