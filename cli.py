"""Console demo of the University Management System."""

from collections.abc import Callable

from university.models import Course, DomainError, Faculty, Student, University


def seed(uni: University) -> None:
    uni.add_student(Student("S101", "Prachi", "CSE"))
    uni.add_student(Student("S102", "Neha", "CSE"))
    uni.add_faculty(Faculty("F201", "Garima Jain", "CSBS"))
    uni.add_faculty(Faculty("F202", "Sanny Kumar", "CSBS"))

    uni.add_course(Course("CSE100", "Python Basics", 3))
    uni.add_course(Course("CSE200", "OOP in Python", 4, ["CSE100"]))
    uni.add_course(Course("CSE300", "Data Structures", 4, ["CSE200"]))

    uni.assign_faculty("F201", "CSE100")
    uni.assign_faculty("F202", "CSE200")


def report(action: Callable[[], str]) -> None:
    """Run ``action`` and print its outcome, including rejected domain rules."""
    try:
        print(action())
    except DomainError as exc:
        print(f"Rejected: {exc}")


def main() -> None:
    uni = University()
    seed(uni)

    report(lambda: uni.enroll_student("S101", "CSE100"))
    report(lambda: uni.complete_course("S101", "CSE100", grade="A"))
    report(lambda: uni.enroll_student("S101", "CSE200"))
    report(lambda: uni.enroll_student("S101", "CSE300"))  # prerequisite not completed
    report(lambda: uni.enroll_student("S102", "CSE200"))  # prerequisite not completed
    report(lambda: uni.enroll_student("S999", "CSE100"))  # unknown student

    print()
    print(uni.summary())


if __name__ == "__main__":
    main()
