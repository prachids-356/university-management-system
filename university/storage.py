"""JSON persistence so data survives a restart.

The on-disk format is intentionally flat and human-readable; it maps closely to
the relational schema described in ARCHITECTURE.md, which makes the eventual
move to a real database a data migration rather than a rewrite.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from university.models import (
    Course,
    Enrollment,
    EnrollmentStatus,
    Faculty,
    Student,
    University,
)

DEFAULT_DATA_FILE = Path(
    os.environ.get("UMS_DATA_FILE", Path(__file__).resolve().parent.parent / "data.json")
)


def to_dict(uni: University) -> dict:
    return {
        "version": 1,
        "students": [
            {"id": s.person_id, "name": s.name, "major": s.major} for s in uni.students.values()
        ],
        "faculty": [
            {"id": f.person_id, "name": f.name, "department": f.department}
            for f in uni.faculty.values()
        ],
        "courses": [
            {
                "code": c.course_code,
                "title": c.title,
                "credits": c.credits,
                "prerequisites": c.prerequisites,
                "capacity": c.capacity,
                "faculty_id": c.assigned_faculty.person_id if c.assigned_faculty else None,
            }
            for c in uni.courses.values()
        ],
        "enrollments": [
            {
                "student_id": s.person_id,
                "course_code": e.course.course_code,
                "status": e.status.value,
                "grade": e.grade,
            }
            for s in uni.students.values()
            for e in s.enrollments
        ],
    }


def from_dict(payload: dict) -> University:
    uni = University()
    for record in payload.get("students", []):
        uni.add_student(Student(record["id"], record["name"], record.get("major", "")))
    for record in payload.get("faculty", []):
        uni.add_faculty(Faculty(record["id"], record["name"], record.get("department", "")))

    # Courses are inserted prerequisite-first so University.add_course can
    # validate that every referenced prerequisite already exists.
    pending = {r["code"]: r for r in payload.get("courses", [])}
    while pending:
        ready = [r for r in pending.values() if all(p in uni.courses for p in r["prerequisites"])]
        if not ready:
            raise ValueError(f"Unresolvable prerequisite cycle in: {sorted(pending)}")
        for record in ready:
            course = uni.add_course(
                Course(
                    record["code"],
                    record["title"],
                    record["credits"],
                    record.get("prerequisites", []),
                    record.get("capacity"),
                )
            )
            if record.get("faculty_id"):
                uni.get_faculty(record["faculty_id"]).assign_course(course)
            del pending[record["code"]]

    for record in payload.get("enrollments", []):
        student = uni.get_student(record["student_id"])
        course = uni.get_course(record["course_code"])
        status = EnrollmentStatus(record.get("status", "enrolled"))
        student.enrollments.append(Enrollment(course, status, record.get("grade")))
        if status is EnrollmentStatus.ENROLLED:
            course.add_student(student)
    return uni


def save(uni: University, path: Path | None = None) -> Path:
    path = Path(path or DEFAULT_DATA_FILE)
    path.write_text(json.dumps(to_dict(uni), indent=2))
    return path


def load(path: Path | None = None) -> University:
    """Load a university from ``path``; return an empty one if it does not exist."""
    path = Path(path or DEFAULT_DATA_FILE)
    if not path.exists():
        return University()
    return from_dict(json.loads(path.read_text()))
