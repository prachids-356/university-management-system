# university_management_system.py

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
            print(f"{self.name} cannot enroll in {course.title} without prerequisites: {course.prerequisites}")

    def __str__(self):
        return f"Student: {self.name} | ID: {self.person_id} | Major: {self.major} | Enrolled: {[c.title for c in self.enrolled_courses]}"


class Faculty(Person):
    def __init__(self, faculty_id, name, department):
        super().__init__(faculty_id, name)
        self.department = department
        self.assigned_courses = []

    def assign_course(self, course):
        self.assigned_courses.append(course)
        course.assign_faculty(self)

    def __str__(self):
        return f"Faculty: {self.name} | ID: {self.person_id} | Dept: {self.department} | Courses: {[c.title for c in self.assigned_courses]}"


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
        faculty_name = self.assigned_faculty.name if self.assigned_faculty else "None"
        return f"Course: {self.title} | Code: {self.course_code} | Credits: {self.credits} | Prerequisites: {self.prerequisites} | Faculty: {faculty_name}"


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

    def enroll_student_in_course(self, student_id, course_code):
        student = self.students.get(student_id)
        course = self.courses.get(course_code)
        if student and course:
            student.enroll(course)
        else:
            print(f"Enrollment failed: student or course not found.")

    def assign_faculty_to_course(self, faculty_id, course_code):
        faculty = self.faculty.get(faculty_id)
        course = self.courses.get(course_code)
        if faculty and course:
            faculty.assign_course(course)
        else:
            print(f"Assignment failed: faculty or course not found.")

    def display_all(self):
        print("\n--- Students ---")
        for student in self.students.values():
            print(student)
        print("\n--- Faculty ---")
        for faculty in self.faculty.values():
            print(faculty)
        print("\n--- Courses ---")
        for course in self.courses.values():
            print(course)
            print("Roster:", [s.name for s in course.enrolled_students])


def main():
    uni = University()

    # Sample data
    s1 = Student("S101", "Prachi", "CSE")
    s2 = Student("S102", "Neha", "CSE")
    f1 = Faculty("F201", "Garima Jain", "CSBS")
    f2 = Faculty("F202", "Sanny Kumar", "CSBS")

    c1 = Course("CSE100", "Python Basics", 3)
    c2 = Course("CSE200", "OOP in Python", 4, ["CSE100"])
    c3 = Course("CSE300", "Data Structures", 4, ["CSE200"])

    # Adding data
    uni.add_student(s1)
    uni.add_student(s2)
    uni.add_faculty(f1)
    uni.add_faculty(f2)
    uni.add_course(c1)
    uni.add_course(c2)
    uni.add_course(c3)

    # Assign faculty
    uni.assign_faculty_to_course("F201", "CSE100")
    uni.assign_faculty_to_course("F202", "CSE200")

    # Enrollments
    uni.enroll_student_in_course("S101", "CSE100")
    uni.enroll_student_in_course("S101", "CSE200")
    uni.enroll_student_in_course("S101", "CSE300")  # should fail
    uni.enroll_student_in_course("S102", "CSE200")  # should fail

    # Display system data
    uni.display_all()


if __name__ == "__main__":
    main()
