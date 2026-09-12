Student Management System

A desktop application for managing student academic records, built with Python, Tkinter (GUI), and SQLite (database). It supports complete CRUD operations — add, view, update, delete, and search — through a clean, form-based interface.

Features
Add students — capture Roll No, Name, Course, Email, Phone, and Marks
Update records — click a row to load it into the form, edit, and save
Delete records — with a confirmation prompt to prevent accidental deletion
Live search — filter the table instantly by Roll No or Name
Input validation — required fields, numeric marks, and basic email format checks
Persistent storage — all data is saved locally in a SQLite database (student_data.db), created automatically on first run
Duplicate protection — prevents adding two students with the same Roll No
Tech Stack
Layer	Technology
GUI	Tkinter (ttk widgets)
Database	SQLite (sqlite3)
Language	Python 3
Project Structure
student-management-system/
├── student_management_gui.py   # Application entry point (GUI + database logic)
├── student_data.db             # Auto-created on first run (not tracked in git)
└── README.md

The code is organized into two classes:

StudentDatabase — handles all SQLite operations (create table, add, update, delete, search, fetch)
StudentApp — builds and manages the Tkinter interface (form, table, buttons, search box)
Getting Started
Prerequisites
Python 3.8 or later (Tkinter ships with the standard Python installer on Windows/macOS; on Linux you may need sudo apt install python3-tk)
Run it
bash
git clone https://github.com/Ayushkumar055/Student-management-system.git
cd Student-management-system
python student_management_gui.py

No extra dependencies to install — everything used (tkinter, sqlite3) is part of the Python standard library.

Usage
Fill in the form fields and click Add to create a new student record.
Click any row in the table to load it into the form — edit the fields and click Update to save changes.
Select a row (or type its Roll No) and click Delete to remove a record.
Use the Search box to filter records by Roll No or Name as you type.
Click Show All to clear the search filter and view every record again.
Click Clear Form to reset the input fields without affecting the database.
Possible Improvements
Export records to CSV/Excel
Sort table columns by clicking headers
Add subject-wise marks and auto-calculate grade/CGPA
Package as a standalone .exe with PyInstaller
Author

Ayush Kumar GitHub · LinkedIn
