from dataclasses import dataclass, field


@dataclass
class Person:
    person_id: str
    name: str


@dataclass
class Student(Person):
    major: str
    enrolled_courses: list[str] = field(default_factory=list)


@dataclass
class Faculty(Person):
    department: str
    assigned_courses: list[str] = field(default_factory=list)


@dataclass
class Course:
    course_code: str
    title: str
    credits: int
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class University:
    students: dict[str, Student] = field(default_factory=dict)
    faculty: dict[str, Faculty] = field(default_factory=dict)
    courses: dict[str, Course] = field(default_factory=dict)
