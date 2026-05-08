from rest_framework import serializers
from django.contrib.auth.models import User
from schools.models import School, SchoolUser
from academics.models import AcademicYear, ClassLevel, Subject, ClassSection, Student, ParentStudentLink, TeacherSubjectAssignment
from attendance.models import AttendanceSession, AttendanceRecord
from results.models import Term, GradeScale, StudentResult
from notifications.models import Announcement

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class SchoolUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = SchoolUser
        fields = '__all__'

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ClassSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSection
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'

class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'

class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'

class StudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResult
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

from fees.models import FeeStructure, FeeInvoice, FeePayment, Expense, ExpenseCategory

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class FeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeInvoice
        fields = '__all__'

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
