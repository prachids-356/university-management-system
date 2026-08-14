import pytest

from university.models import (
    Course,
    DomainError,
    Faculty,
    Student,
    University,
    parse_prerequisites,
)


@pytest.fixture
def uni() -> University:
    university = University()
    university.add_student(Student("S101", "Prachi", "CSE"))
    university.add_student(Student("S102", "Neha", "CSE"))
    university.add_faculty(Faculty("F201", "Garima Jain", "CSBS"))
    university.add_faculty(Faculty("F202", "Sanny Kumar", "CSBS"))
    university.add_course(Course("CSE100", "Python Basics", 3))
    university.add_course(Course("CSE200", "OOP in Python", 4, ["CSE100"]))
    return university


def test_prerequisites_are_trimmed_and_uppercased():
    assert parse_prerequisites("cse100, CSE200 ,") == ["CSE100", "CSE200"]


def test_course_codes_match_regardless_of_spacing(uni):
    uni.add_course(Course("cse300", "Data Structures", 4, [" cse200 "]))
    assert uni.get_course(" CSE300 ").prerequisites == ["CSE200"]


def test_enroll_requires_completed_prerequisite(uni):
    uni.enroll_student("S101", "CSE100")
    with pytest.raises(DomainError, match="missing prerequisites CSE100"):
        uni.enroll_student("S101", "CSE200")

    uni.complete_course("S101", "CSE100", grade="A")
    assert "enrolled in CSE200" in uni.enroll_student("S101", "CSE200")


def test_duplicate_enrollment_rejected(uni):
    uni.enroll_student("S101", "CSE100")
    with pytest.raises(DomainError, match="already enrolled"):
        uni.enroll_student("S101", "CSE100")
    assert len(uni.get_course("CSE100").enrolled_students) == 1


def test_duplicate_ids_rejected(uni):
    with pytest.raises(DomainError, match="already exists"):
        uni.add_student(Student("S101", "Someone Else", "ECE"))
    assert uni.get_student("S101").name == "Prachi"


def test_unknown_prerequisite_rejected(uni):
    with pytest.raises(DomainError, match="Unknown prerequisite"):
        uni.add_course(Course("CSE400", "Compilers", 4, ["CSE999"]))


def test_capacity_enforced(uni):
    uni.add_course(Course("CSE500", "Seminar", 1, capacity=1))
    uni.enroll_student("S101", "CSE500")
    with pytest.raises(DomainError, match="is full"):
        uni.enroll_student("S102", "CSE500")


def test_prerequisites_are_not_shared_between_courses():
    first = Course("A100", "A", 3)
    second = Course("B100", "B", 3)
    first.prerequisites.append("X")
    assert second.prerequisites == []


def test_reassigning_faculty_clears_previous_owner(uni):
    uni.assign_faculty("F201", "CSE100")
    uni.assign_faculty("F202", "CSE100")
    assert uni.get_course("CSE100").assigned_faculty is uni.get_faculty("F202")
    assert uni.get_faculty("F201").assigned_courses == []


def test_duplicate_assignment_rejected(uni):
    uni.assign_faculty("F201", "CSE100")
    with pytest.raises(DomainError, match="already assigned"):
        uni.assign_faculty("F201", "CSE100")


def test_missing_entities_raise(uni):
    with pytest.raises(DomainError, match="No student with ID S999"):
        uni.enroll_student("S999", "CSE100")
    with pytest.raises(DomainError, match="No course with code CSE999"):
        uni.enroll_student("S101", "CSE999")


@pytest.mark.parametrize("credits", [0, 13, "three", None])
def test_invalid_credits_rejected(credits):
    with pytest.raises(DomainError, match="Credits"):
        Course("CSE600", "Bad", credits)


def test_blank_identity_rejected():
    with pytest.raises(DomainError, match="ID is required"):
        Student("  ", "Nobody", "CSE")
    with pytest.raises(DomainError, match="Name is required"):
        Student("S1", "", "CSE")
