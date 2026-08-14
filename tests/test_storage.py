from university import storage
from university.models import Course, Faculty, Student, University


def build() -> University:
    uni = University()
    uni.add_student(Student("S101", "Prachi", "CSE"))
    uni.add_faculty(Faculty("F201", "Garima Jain", "CSBS"))
    uni.add_course(Course("CSE100", "Python Basics", 3))
    uni.add_course(Course("CSE200", "OOP in Python", 4, ["CSE100"]))
    uni.assign_faculty("F201", "CSE200")
    uni.enroll_student("S101", "CSE100")
    uni.complete_course("S101", "CSE100", grade="A")
    uni.enroll_student("S101", "CSE200")
    return uni


def test_round_trip_preserves_state(tmp_path):
    path = tmp_path / "data.json"
    storage.save(build(), path)
    loaded = storage.load(path)

    student = loaded.get_student("S101")
    assert student.completed_course_codes == {"CSE100"}
    assert [c.course_code for c in student.enrolled_courses] == ["CSE200"]
    assert loaded.get_course("CSE200").assigned_faculty.person_id == "F201"
    assert [s.person_id for s in loaded.get_course("CSE200").enrolled_students] == ["S101"]


def test_courses_reload_even_when_listed_before_their_prerequisites():
    payload = {
        "students": [],
        "faculty": [],
        "courses": [
            {"code": "CSE200", "title": "OOP", "credits": 4, "prerequisites": ["CSE100"]},
            {"code": "CSE100", "title": "Basics", "credits": 3, "prerequisites": []},
        ],
        "enrollments": [],
    }
    assert set(storage.from_dict(payload).courses) == {"CSE100", "CSE200"}


def test_missing_file_yields_empty_university(tmp_path):
    assert storage.load(tmp_path / "absent.json").students == {}
