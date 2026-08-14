from django.core.exceptions import ValidationError


PASSING_GRADES = {"A", "B", "C", "D"}


class UniversityService:
    @staticmethod
    def validate_student_role(user):
        if not user.is_authenticated or user.role != user.Role.STUDENT:
            raise ValidationError("Only students can enroll in courses.")

    @staticmethod
    def validate_capacity(course):
        if course.enrollments.count() >= course.capacity:
            raise ValidationError("Course capacity has been reached.")

    @staticmethod
    def validate_duplicate(enrollment_model, student, course):
        if enrollment_model.objects.filter(student=student, course=course).exists():
            raise ValidationError("Student is already enrolled in this course.")

    @staticmethod
    def validate_prerequisites(enrollment_model, student, course):
        required_codes = set(course.prerequisites.values_list("code", flat=True))
        if not required_codes:
            return
        completed_codes = set(
            enrollment_model.objects.filter(
                student=student,
                status=enrollment_model.Status.COMPLETED,
                grade__in=PASSING_GRADES,
            ).values_list("course__code", flat=True)
        )
        missing = sorted(required_codes - completed_codes)
        if missing:
            raise ValidationError(
                f"Missing prerequisite courses: {', '.join(missing)}"
            )
