import tkinter as tk
from tkinter import messagebox, simpledialog


# --- Models (same OOP structure) ---
class Person:
    def __init__(self, person_id, name):
        self.person_id = person_id
        self.name = name


class Student(Person):
    def __init__(self, student_id, name, major):
        super().__init__(student_id, name)
        self.major = major
        self.enrolled_courses = []

    def enroll(self, course):
        if all(prereq in [c.course_code for c in self.enrolled_courses] for prereq in course.prerequisites):
            self.enrolled_courses.append(course)
            course.add_student(self)
        else:
            return f"{self.name} cannot enroll in {course.title} without prerequisites: {course.prerequisites}"
        return "Enrolled successfully"

    def __str__(self):
        return f"{self.name} ({self.person_id}) - {self.major}"


class Faculty(Person):
    def __init__(self, faculty_id, name, department):
        super().__init__(faculty_id, name)
        self.department = department
        self.assigned_courses = []

    def assign_course(self, course):
        self.assigned_courses.append(course)
        course.assign_faculty(self)

    def __str__(self):
        return f"{self.name} ({self.person_id}) - {self.department}"


class Course:
    def __init__(self, course_code, title, credits, prerequisites=[]):
        self.course_code = course_code
        self.title = title
        self.credits = credits
        self.prerequisites = prerequisites
        self.enrolled_students = []
        self.assigned_faculty = None

    def add_student(self, student):
        self.enrolled_students.append(student)

    def assign_faculty(self, faculty):
        self.assigned_faculty = faculty

    def __str__(self):
        return f"{self.course_code}: {self.title}"


class University:
    def __init__(self):
        self.students = {}
        self.faculty = {}
        self.courses = {}

    def add_student(self, student):
        self.students[student.person_id] = student

    def add_faculty(self, faculty):
        self.faculty[faculty.person_id] = faculty

    def add_course(self, course):
        self.courses[course.course_code] = course

    def enroll_student(self, student_id, course_code):
        s = self.students.get(student_id)
        c = self.courses.get(course_code)
        if s and c:
            return s.enroll(c)
        return "Enrollment failed."

    def assign_faculty(self, faculty_id, course_code):
        f = self.faculty.get(faculty_id)
        c = self.courses.get(course_code)
        if f and c:
            f.assign_course(c)
            return "Faculty assigned"
        return "Assignment failed"


users = {
    "admin": "admin123",
    "faculty": "fac123",
    "student": "stud123"
}

uni = University()


root = tk.Tk()
root.title("University Management System")
root.geometry("500x400")


login_frame = tk.Frame(root)
admin_frame = tk.Frame(root)

def clear_frames():
    for widget in root.winfo_children():
        widget.pack_forget()


def login():
    username = user_entry.get()
    password = pass_entry.get()

    if username in users and users[username] == password:
        messagebox.showinfo("Login", "Login successful!")
        show_admin_dashboard()
    else:
        messagebox.showerror("Error", "Invalid credentials")

def show_login_screen():
    clear_frames()
    tk.Label(root, text="Login", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="Username").pack()
    global user_entry
    user_entry = tk.Entry(root)
    user_entry.pack()

    tk.Label(root, text="Password").pack()
    global pass_entry
    pass_entry = tk.Entry(root, show="*")
    pass_entry.pack()

    tk.Button(root, text="Login", command=login).pack(pady=10)


def show_admin_dashboard():
    clear_frames()
    tk.Label(root, text="Admin Dashboard", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Add Student", command=add_student).pack(pady=5)
    tk.Button(root, text="Add Faculty", command=add_faculty).pack(pady=5)
    tk.Button(root, text="Add Course", command=add_course).pack(pady=5)
    tk.Button(root, text="Enroll Student in Course", command=enroll_student_gui).pack(pady=5)
    tk.Button(root, text="Assign Faculty to Course", command=assign_faculty_gui).pack(pady=5)
    tk.Button(root, text="View All Data", command=view_all).pack(pady=5)
    tk.Button(root, text="Logout", command=show_login_screen).pack(pady=10)


def add_student():
    sid = simpledialog.askstring("Student ID", "Enter Student ID:")
    name = simpledialog.askstring("Student Name", "Enter Student Name:")
    major = simpledialog.askstring("Major", "Enter Major:")
    if sid and name:
        uni.add_student(Student(sid, name, major))
        messagebox.showinfo("Success", "Student Added!")

def add_faculty():
    fid = simpledialog.askstring("Faculty ID", "Enter Faculty ID:")
    name = simpledialog.askstring("Faculty Name", "Enter Faculty Name:")
    dept = simpledialog.askstring("Department", "Enter Department:")
    if fid and name:
        uni.add_faculty(Faculty(fid, name, dept))
        messagebox.showinfo("Success", "Faculty Added!")

def add_course():
    code = simpledialog.askstring("Course Code", "Enter Course Code:")
    title = simpledialog.askstring("Title", "Enter Course Title:")
    credits = simpledialog.askinteger("Credits", "Enter Credits:")
    prereq = simpledialog.askstring("Prerequisites", "Enter prereq (comma-separated):")
    prereq_list = prereq.split(",") if prereq else []
    if code and title:
        uni.add_course(Course(code, title, credits, prereq_list))
        messagebox.showinfo("Success", "Course Added!")

def enroll_student_gui():
    sid = simpledialog.askstring("Student ID", "Enter Student ID:")
    ccode = simpledialog.askstring("Course Code", "Enter Course Code:")
    result = uni.enroll_student(sid, ccode)
    messagebox.showinfo("Enrollment", result)

def assign_faculty_gui():
    fid = simpledialog.askstring("Faculty ID", "Enter Faculty ID:")
    ccode = simpledialog.askstring("Course Code", "Enter Course Code:")
    result = uni.assign_faculty(fid, ccode)
    messagebox.showinfo("Assignment", result)

def view_all():
    data = "--- Students ---\n"
    for s in uni.students.values():
        data += str(s) + "\n"
    data += "\n--- Faculty ---\n"
    for f in uni.faculty.values():
        data += str(f) + "\n"
    data += "\n--- Courses ---\n"
    for c in uni.courses.values():
        enrolled = [s.name for s in c.enrolled_students]
        faculty = c.assigned_faculty.name if c.assigned_faculty else "None"
        data += f"{c.course_code} - {c.title} | Faculty: {faculty} | Enrolled: {enrolled}\n"
    messagebox.showinfo("Database", data)

# --- Start UI ---
show_login_screen()
root.mainloop()
