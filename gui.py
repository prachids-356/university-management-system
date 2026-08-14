"""Tkinter front end for the University Management System."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, simpledialog, ttk

from university import storage
from university.auth import AuthError, Role, User, authenticate, load_users, require
from university.models import (
    Course,
    DomainError,
    Faculty,
    Student,
    University,
    parse_prerequisites,
)

# Which actions each role sees on its dashboard.
ROLE_ACTIONS: dict[Role, tuple[str, ...]] = {
    Role.ADMIN: (
        "add_student",
        "add_faculty",
        "add_course",
        "enroll_student",
        "assign_faculty",
        "view_all",
    ),
    Role.FACULTY: ("enroll_student", "view_all"),
    Role.STUDENT: ("view_all",),
}


class Cancelled(Exception):
    """Raised when the user dismisses an input dialog."""


class App:
    def __init__(self, root: tk.Tk, uni: University | None = None) -> None:
        self.root = root
        self.uni = uni if uni is not None else storage.load()
        self.users = load_users()
        self.current_user: User | None = None
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        root.title("University Management System")
        root.geometry("520x420")
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login()

    # --- screen management -------------------------------------------------
    def clear(self) -> None:
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self) -> None:
        self.current_user = None
        self.clear()
        tk.Label(self.container, text="Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.container, text="Username").pack()
        self.user_entry = tk.Entry(self.container)
        self.user_entry.pack()

        tk.Label(self.container, text="Password").pack()
        self.pass_entry = tk.Entry(self.container, show="*")
        self.pass_entry.pack()
        self.pass_entry.bind("<Return>", lambda _event: self.login())

        tk.Button(self.container, text="Login", command=self.login).pack(pady=10)
        self.user_entry.focus_set()

    def login(self) -> None:
        try:
            self.current_user = authenticate(
                self.user_entry.get(), self.pass_entry.get(), self.users
            )
        except AuthError as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.show_dashboard()

    def show_dashboard(self) -> None:
        assert self.current_user is not None
        role = self.current_user.role
        self.clear()
        tk.Label(
            self.container,
            text=f"{role.value.title()} Dashboard - {self.current_user.username}",
            font=("Arial", 16),
        ).pack(pady=10)

        actions = self.actions()
        for name in ROLE_ACTIONS[role]:
            label, permission, handler = actions[name]
            tk.Button(
                self.container,
                text=label,
                command=self.guarded(permission, handler),
            ).pack(pady=5)
        tk.Button(self.container, text="Logout", command=self.show_login).pack(pady=10)

    def actions(self) -> dict[str, tuple[str, str, Callable[[], None]]]:
        """Map action name to its (button label, required permission, handler)."""
        return {
            "add_student": ("Add Student", "student:create", self.add_student),
            "add_faculty": ("Add Faculty", "faculty:create", self.add_faculty),
            "add_course": ("Add Course", "course:create", self.add_course),
            "enroll_student": (
                "Enroll Student in Course",
                "enrollment:create",
                self.enroll_student,
            ),
            "assign_faculty": (
                "Assign Faculty to Course",
                "assignment:create",
                self.assign_faculty,
            ),
            "view_all": ("View All Data", "data:view", self.view_all),
        }

    def guarded(self, permission: str, handler: Callable[[], None]) -> Callable[[], None]:
        """Wrap ``handler`` so permission and domain errors surface as dialogs."""

        def run() -> None:
            try:
                require(self.current_user, permission)
                handler()
            except Cancelled:
                pass
            except AuthError as exc:
                messagebox.showerror("Not allowed", str(exc))
            except DomainError as exc:
                messagebox.showerror("Invalid input", str(exc))

        return run

    # --- prompts -----------------------------------------------------------
    def ask_text(self, title: str, prompt: str) -> str:
        value = simpledialog.askstring(title, prompt, parent=self.root)
        if value is None:
            raise Cancelled
        return value

    def ask_int(self, title: str, prompt: str) -> int:
        value = simpledialog.askinteger(title, prompt, parent=self.root)
        if value is None:
            raise Cancelled
        return value

    # --- actions -----------------------------------------------------------
    def add_student(self) -> None:
        student = Student(
            self.ask_text("Student ID", "Enter Student ID:"),
            self.ask_text("Student Name", "Enter Student Name:"),
            self.ask_text("Major", "Enter Major:"),
        )
        self.uni.add_student(student)
        self.persist(f"Student {student.person_id} added.")

    def add_faculty(self) -> None:
        faculty = Faculty(
            self.ask_text("Faculty ID", "Enter Faculty ID:"),
            self.ask_text("Faculty Name", "Enter Faculty Name:"),
            self.ask_text("Department", "Enter Department:"),
        )
        self.uni.add_faculty(faculty)
        self.persist(f"Faculty {faculty.person_id} added.")

    def add_course(self) -> None:
        code = self.ask_text("Course Code", "Enter Course Code:")
        title = self.ask_text("Title", "Enter Course Title:")
        credits = self.ask_int("Credits", "Enter Credits (1-12):")
        prerequisites = parse_prerequisites(
            simpledialog.askstring(
                "Prerequisites", "Enter prerequisites (comma-separated):", parent=self.root
            )
        )
        course = Course(code, title, credits, prerequisites)
        self.uni.add_course(course)
        self.persist(f"Course {course.course_code} added.")

    def enroll_student(self) -> None:
        result = self.uni.enroll_student(
            self.ask_text("Student ID", "Enter Student ID:"),
            self.ask_text("Course Code", "Enter Course Code:"),
        )
        self.persist(result)

    def assign_faculty(self) -> None:
        result = self.uni.assign_faculty(
            self.ask_text("Faculty ID", "Enter Faculty ID:"),
            self.ask_text("Course Code", "Enter Course Code:"),
        )
        self.persist(result)

    def view_all(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("University Data")
        window.geometry("640x420")

        tree = ttk.Treeview(window, columns=("detail",), show="tree headings")
        tree.heading("#0", text="Record")
        tree.heading("detail", text="Details")
        tree.column("detail", width=380)

        students = tree.insert("", "end", text="Students", open=True)
        for student in self.uni.students.values():
            enrolled = ", ".join(c.course_code for c in student.enrolled_courses) or "none"
            completed = ", ".join(sorted(student.completed_course_codes)) or "none"
            tree.insert(
                students,
                "end",
                text=str(student),
                values=(f"Enrolled: {enrolled} | Completed: {completed}",),
            )

        faculty_node = tree.insert("", "end", text="Faculty", open=True)
        for faculty in self.uni.faculty.values():
            courses = ", ".join(c.course_code for c in faculty.assigned_courses) or "none"
            tree.insert(faculty_node, "end", text=str(faculty), values=(f"Courses: {courses}",))

        courses_node = tree.insert("", "end", text="Courses", open=True)
        for course in self.uni.courses.values():
            roster = ", ".join(s.name for s in course.enrolled_students) or "none"
            teacher = course.assigned_faculty.name if course.assigned_faculty else "None"
            tree.insert(
                courses_node,
                "end",
                text=str(course.course_code) + ": " + course.title,
                values=(f"Faculty: {teacher} | Roster: {roster}",),
            )

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

    # --- persistence -------------------------------------------------------
    def persist(self, message: str) -> None:
        storage.save(self.uni)
        messagebox.showinfo("Success", message)

    def on_close(self) -> None:
        storage.save(self.uni)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
