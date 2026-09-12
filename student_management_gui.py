"""
Student Management System
--------------------------
A desktop GUI application built with Tkinter (UI) and SQLite (storage).

Features:
    - Add, view, update, delete student records (full CRUD)
    - Search students by roll number or name
    - Input validation with clear error messages
    - Data persisted in a local SQLite database (student_data.db)

Author: Ayush Kumar
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "student_data.db"


# --------------------------------------------------------------------------
# Database layer
# --------------------------------------------------------------------------
class StudentDatabase:
    """Handles all SQLite operations for student records."""

    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                roll_no     TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                course      TEXT NOT NULL,
                email       TEXT,
                phone       TEXT,
                marks       REAL
            )
            """
        )
        self.conn.commit()

    def add_student(self, roll_no, name, course, email, phone, marks):
        try:
            self.conn.execute(
                "INSERT INTO students (roll_no, name, course, email, phone, marks) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (roll_no, name, course, email, phone, marks),
            )
            self.conn.commit()
            return True, "Student added successfully."
        except sqlite3.IntegrityError:
            return False, f"A student with roll number '{roll_no}' already exists."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

    def update_student(self, roll_no, name, course, email, phone, marks):
        cur = self.conn.execute(
            "UPDATE students SET name=?, course=?, email=?, phone=?, marks=? "
            "WHERE roll_no=?",
            (name, course, email, phone, marks, roll_no),
        )
        self.conn.commit()
        if cur.rowcount == 0:
            return False, f"No student found with roll number '{roll_no}'."
        return True, "Student updated successfully."

    def delete_student(self, roll_no):
        cur = self.conn.execute("DELETE FROM students WHERE roll_no=?", (roll_no,))
        self.conn.commit()
        if cur.rowcount == 0:
            return False, f"No student found with roll number '{roll_no}'."
        return True, "Student deleted successfully."

    def get_all_students(self):
        return self.conn.execute(
            "SELECT roll_no, name, course, email, phone, marks FROM students ORDER BY roll_no"
        ).fetchall()

    def search_students(self, keyword):
        like = f"%{keyword}%"
        return self.conn.execute(
            "SELECT roll_no, name, course, email, phone, marks FROM students "
            "WHERE roll_no LIKE ? OR name LIKE ? ORDER BY roll_no",
            (like, like),
        ).fetchall()

    def get_student(self, roll_no):
        return self.conn.execute(
            "SELECT roll_no, name, course, email, phone, marks FROM students WHERE roll_no=?",
            (roll_no,),
        ).fetchone()

    def close(self):
        self.conn.close()


# --------------------------------------------------------------------------
# GUI layer
# --------------------------------------------------------------------------
class StudentApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("880x520")
        self.minsize(820, 480)
        self.configure(bg="#f4f6f8")

        self.db = StudentDatabase()
        self.selected_roll_no = None  # tracks which row is loaded for editing

        self._build_style()
        self._build_form()
        self._build_table()
        self._build_actions()
        self.refresh_table()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- UI construction ----------------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#f4f6f8", font=("Segoe UI", 10))

    def _build_form(self):
        frame = tk.Frame(self, bg="#f4f6f8", padx=16, pady=12)
        frame.pack(fill="x")

        self.fields = {}
        labels = [
            ("Roll No", "roll_no"),
            ("Name", "name"),
            ("Course", "course"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Marks", "marks"),
        ]

        for col, (label_text, key) in enumerate(labels):
            ttk.Label(frame, text=label_text).grid(row=0, column=col, sticky="w", padx=4)
            entry = ttk.Entry(frame, width=16)
            entry.grid(row=1, column=col, padx=4, pady=(0, 4))
            self.fields[key] = entry

    def _build_actions(self):
        frame = tk.Frame(self, bg="#f4f6f8", padx=16, pady=6)
        frame.pack(fill="x")

        ttk.Button(frame, text="Add", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(frame, text="Update", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(frame, text="Delete", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

        ttk.Label(frame, text="Search:").pack(side="left", padx=(24, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        ttk.Button(frame, text="Show All", command=self.refresh_table).pack(side="left", padx=4)

    def _build_table(self):
        frame = tk.Frame(self, padx=16, pady=8)
        frame.pack(fill="both", expand=True)

        columns = ("roll_no", "name", "course", "email", "phone", "marks")
        headings = ("Roll No", "Name", "Course", "Email", "Phone", "Marks")

        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col, heading in zip(columns, headings):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=130, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------------- Validation ----------------
    def _read_form(self):
        return {key: entry.get().strip() for key, entry in self.fields.items()}

    def _validate(self, data, require_roll_no=True):
        if require_roll_no and not data["roll_no"]:
            return "Roll No is required."
        if not data["name"]:
            return "Name is required."
        if not data["course"]:
            return "Course is required."
        if data["marks"]:
            try:
                float(data["marks"])
            except ValueError:
                return "Marks must be a number."
        if data["email"] and "@" not in data["email"]:
            return "Email looks invalid (missing '@')."
        return None

    # ---------------- CRUD actions ----------------
    def add_student(self):
        data = self._read_form()
        error = self._validate(data)
        if error:
            messagebox.showerror("Validation Error", error)
            return

        marks = float(data["marks"]) if data["marks"] else None
        ok, msg = self.db.add_student(
            data["roll_no"], data["name"], data["course"], data["email"], data["phone"], marks
        )
        (messagebox.showinfo if ok else messagebox.showerror)("Add Student", msg)
        if ok:
            self.clear_form()
            self.refresh_table()

    def update_student(self):
        data = self._read_form()
        error = self._validate(data)
        if error:
            messagebox.showerror("Validation Error", error)
            return

        marks = float(data["marks"]) if data["marks"] else None
        ok, msg = self.db.update_student(
            data["roll_no"], data["name"], data["course"], data["email"], data["phone"], marks
        )
        (messagebox.showinfo if ok else messagebox.showerror)("Update Student", msg)
        if ok:
            self.clear_form()
            self.refresh_table()

    def delete_student(self):
        data = self._read_form()
        roll_no = data["roll_no"]
        if not roll_no:
            messagebox.showerror("Validation Error", "Enter or select a Roll No to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete student '{roll_no}'?"):
            return
        ok, msg = self.db.delete_student(roll_no)
        (messagebox.showinfo if ok else messagebox.showerror)("Delete Student", msg)
        if ok:
            self.clear_form()
            self.refresh_table()

    def on_search(self):
        keyword = self.search_var.get().strip()
        rows = self.db.search_students(keyword) if keyword else self.db.get_all_students()
        self._populate_table(rows)

    # ---------------- Table / form sync ----------------
    def refresh_table(self):
        self._populate_table(self.db.get_all_students())

    def _populate_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_row_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        keys = ("roll_no", "name", "course", "email", "phone", "marks")
        for key, value in zip(keys, values):
            self.fields[key].delete(0, tk.END)
            self.fields[key].insert(0, "" if value is None else value)

    def clear_form(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()