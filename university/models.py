"""Domain models for the University Management System.

This module is the single source of truth for the domain rules. Both the
console entry point (``cli.py``) and the Tkinter entry point (``gui.py``)
import from here.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum


class DomainError(Exception):
    """Raised when an operation violates a domain rule."""


class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"


def normalize_code(code: str) -> str:
    """Normalize a course code so lookups are whitespace- and case-insensitive."""
    return code.strip().upper()


def parse_prerequisites(raw: str | None) -> list[str]:
    """Parse a comma-separated prerequisite string into normalized course codes."""
    if not raw:
        return []
    return [normalize_code(part) for part in raw.split(",") if part.strip()]


class Person:
    def __init__(self, person_id: str, name: str) -> None:
        person_id = (person_id or "").strip()
        name = (name or "").strip()
        if not person_id:
            raise DomainError("ID is required.")
        if not name:
            raise DomainError("Name is required.")
        self.person_id = person_id
        self.name = name


class Enrollment:
    """A student's registration in a course, with a status and optional grade."""

    def __init__(
        self,
        course: Course,
        status: EnrollmentStatus = EnrollmentStatus.ENROLLED,
        grade: str | None = None,
    ) -> None:
        self.course = course
        self.status = status
        self.grade = grade


class Student(Person):
    def __init__(self, student_id: str, name: str, major: str) -> None:
        super().__init__(student_id, name)
        self.major = (major or "").strip()
        self.enrollments: list[Enrollment] = []

    @property
    def enrolled_courses(self) -> list[Course]:
        return [e.course for e in self.enrollments if e.status is EnrollmentStatus.ENROLLED]

    @property
    def completed_course_codes(self) -> set[str]:
        return {
            e.course.course_code for e in self.enrollments if e.status is EnrollmentStatus.COMPLETED
        }

    def missing_prerequisites(self, course: Course) -> list[str]:
        """Prerequisites the student has not yet *completed*."""
        return [p for p in course.prerequisites if p not in self.completed_course_codes]

    def enroll(self, course: Course) -> str:
        """Enroll in ``course``, raising :class:`DomainError` if the rules forbid it."""
        if any(
            e.course is course and e.status is EnrollmentStatus.ENROLLED for e in self.enrollments
        ):
            raise DomainError(f"{self.name} is already enrolled in {course.course_code}.")
        missing = self.missing_prerequisites(course)
        if missing:
            raise DomainError(
                f"{self.name} cannot enroll in {course.title}: "
                f"missing prerequisites {', '.join(missing)}."
            )
        if course.is_full:
            raise DomainError(f"{course.course_code} is full ({course.capacity} seats).")
        self.enrollments.append(Enrollment(course))
        course.add_student(self)
        return f"{self.name} enrolled in {course.course_code}."

    def complete(self, course: Course, grade: str | None = None) -> str:
        """Mark an active enrollment as completed so it counts as a prerequisite."""
        for enrollment in self.enrollments:
            if enrollment.course is course and enrollment.status is EnrollmentStatus.ENROLLED:
                enrollment.status = EnrollmentStatus.COMPLETED
                enrollment.grade = grade
                course.remove_student(self)
                return f"{self.name} completed {course.course_code}."
        raise DomainError(f"{self.name} is not currently enrolled in {course.course_code}.")

    def __str__(self) -> str:
        return f"{self.name} ({self.person_id}) - {self.major}"


class Faculty(Person):
    def __init__(self, faculty_id: str, name: str, department: str) -> None:
        super().__init__(faculty_id, name)
        self.department = (department or "").strip()
        self.assigned_courses: list[Course] = []

    def assign_course(self, course: Course) -> str:
        if course in self.assigned_courses:
            raise DomainError(f"{self.name} is already assigned to {course.course_code}.")
        previous = course.assigned_faculty
        if previous is not None and previous is not self:
            previous.unassign_course(course)
        self.assigned_courses.append(course)
        course.assign_faculty(self)
        return f"{self.name} assigned to {course.course_code}."

    def unassign_course(self, course: Course) -> None:
        if course in self.assigned_courses:
            self.assigned_courses.remove(course)

    def __str__(self) -> str:
        return f"{self.name} ({self.person_id}) - {self.department}"


class Course:
    def __init__(
        self,
        course_code: str,
        title: str,
        credits: int,
        prerequisites: Iterable[str] | None = None,
        capacity: int | None = None,
    ) -> None:
        course_code = normalize_code(course_code or "")
        title = (title or "").strip()
        if not course_code:
            raise DomainError("Course code is required.")
        if not title:
            raise DomainError("Course title is required.")
        if not isinstance(credits, int) or not 1 <= credits <= 12:
            raise DomainError("Credits must be an integer between 1 and 12.")
        if capacity is not None and capacity < 1:
            raise DomainError("Capacity must be at least 1.")
        self.course_code = course_code
        self.title = title
        self.credits = credits
        self.prerequisites = [normalize_code(p) for p in (prerequisites or [])]
        self.capacity = capacity
        self.enrolled_students: list[Student] = []
        self.assigned_faculty: Faculty | None = None

    @property
    def is_full(self) -> bool:
        return self.capacity is not None and len(self.enrolled_students) >= self.capacity

    def add_student(self, student: Student) -> None:
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)

    def remove_student(self, student: Student) -> None:
        if student in self.enrolled_students:
            self.enrolled_students.remove(student)

    def assign_faculty(self, faculty: Faculty) -> None:
        self.assigned_faculty = faculty

    def __str__(self) -> str:
        faculty_name = self.assigned_faculty.name if self.assigned_faculty else "None"
        return (
            f"{self.course_code}: {self.title} | Credits: {self.credits} | "
            f"Prerequisites: {self.prerequisites or 'None'} | Faculty: {faculty_name}"
        )


class University:
    """Aggregate root holding every student, faculty member and course."""

    def __init__(self) -> None:
        self.students: dict[str, Student] = {}
        self.faculty: dict[str, Faculty] = {}
        self.courses: dict[str, Course] = {}

    def add_student(self, student: Student) -> Student:
        if student.person_id in self.students:
            raise DomainError(f"Student ID {student.person_id} already exists.")
        self.students[student.person_id] = student
        return student

    def add_faculty(self, faculty: Faculty) -> Faculty:
        if faculty.person_id in self.faculty:
            raise DomainError(f"Faculty ID {faculty.person_id} already exists.")
        self.faculty[faculty.person_id] = faculty
        return faculty

    def add_course(self, course: Course) -> Course:
        if course.course_code in self.courses:
            raise DomainError(f"Course code {course.course_code} already exists.")
        unknown = [p for p in course.prerequisites if p not in self.courses]
        if unknown:
            raise DomainError(f"Unknown prerequisite course(s): {', '.join(unknown)}.")
        self.courses[course.course_code] = course
        return course

    def get_student(self, student_id: str) -> Student:
        student = self.students.get((student_id or "").strip())
        if student is None:
            raise DomainError(f"No student with ID {student_id}.")
        return student

    def get_faculty(self, faculty_id: str) -> Faculty:
        faculty = self.faculty.get((faculty_id or "").strip())
        if faculty is None:
            raise DomainError(f"No faculty with ID {faculty_id}.")
        return faculty

    def get_course(self, course_code: str) -> Course:
        course = self.courses.get(normalize_code(course_code or ""))
        if course is None:
            raise DomainError(f"No course with code {course_code}.")
        return course

    def enroll_student(self, student_id: str, course_code: str) -> str:
        return self.get_student(student_id).enroll(self.get_course(course_code))

    def complete_course(self, student_id: str, course_code: str, grade: str | None = None) -> str:
        return self.get_student(student_id).complete(self.get_course(course_code), grade)

    def assign_faculty(self, faculty_id: str, course_code: str) -> str:
        return self.get_faculty(faculty_id).assign_course(self.get_course(course_code))

    def summary(self) -> str:
        lines = ["--- Students ---"]
        lines += [str(s) for s in self.students.values()] or ["(none)"]
        lines += ["", "--- Faculty ---"]
        lines += [str(f) for f in self.faculty.values()] or ["(none)"]
        lines += ["", "--- Courses ---"]
        if not self.courses:
            lines.append("(none)")
        for course in self.courses.values():
            roster = ", ".join(s.name for s in course.enrolled_students) or "none"
            lines.append(f"{course}\n    Roster: {roster}")
        return "\n".join(lines)
