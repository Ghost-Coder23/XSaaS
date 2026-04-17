"""
Notifications utility functions
SMS is stubbed - integrate Africa's Talking / any provider later by replacing send_sms()
"""
from .models import Notification, SMSLog


def send_sms(school, phone, name, message):
    """
    STUB: Log the SMS locally. Replace this function body with
    real SMS provider SDK (e.g. Africa's Talking) when ready.
    """
    SMSLog.objects.create(
        school=school,
        recipient_phone=phone,
        recipient_name=name,
        message=message,
        status='stub',
        provider_response='SMS gateway not configured. Message logged only.',
    )


def notify_user(school, user, title, message, notification_type='info', link=''):
    """Create an in-app notification for a user"""
    Notification.objects.create(
        school=school,
        recipient=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )


def notify_absences(school, session, absent_students):
    """Notify parents of absent students"""
    for student in absent_students:
        msg = (
            f"Dear Parent/Guardian, {student.user.get_full_name()} was marked ABSENT "
            f"on {session.date} at {school.name}. "
            f"Please contact the school if this is an error."
        )
        # SMS to parent
        if student.parent_phone:
            send_sms(school, student.parent_phone, student.parent_name, msg)
        # In-app notification if parent has account
        from django.contrib.auth.models import User
        try:
            parent_user = User.objects.get(email=student.parent_email)
            notify_user(
                school, parent_user,
                f"Absence Alert: {student.user.get_full_name()}",
                msg,
                notification_type='attendance',
                link=f'/attendance/'
            )
        except User.DoesNotExist:
            pass


def notify_fee_reminder(school, invoice):
    """Send fee reminder to parent"""
    student = invoice.student
    msg = (
        f"Dear {student.parent_name}, this is a fee reminder. "
        f"Invoice #{invoice.invoice_number} for {student.user.get_full_name()} "
        f"is {invoice.get_status_display()}. "
        f"Balance: {invoice.currency} {invoice.balance}. "
        f"Please contact {school.name} to settle this amount."
    )
    if student.parent_phone:
        send_sms(school, student.parent_phone, student.parent_name, msg)


def notify_results_published(school, term):
    """Notify all parents that results are available"""
    from academics.models import Student
    students = Student.objects.filter(school=school, is_active=True)
    for student in students:
        msg = (
            f"Dear {student.parent_name}, {term.name} results for "
            f"{student.user.get_full_name()} are now available on {school.name} portal."
        )
        if student.parent_phone:
            send_sms(school, student.parent_phone, student.parent_name, msg)


def create_announcement_notifications(announcement):
    """Create in-app notifications for all relevant users"""
    from schools.models import SchoolUser
    school = announcement.school
    members = SchoolUser.objects.filter(school=school, is_active=True).select_related('user')

    role_map = {
        'all': None,
        'teachers': 'teacher',
        'parents': 'parent',
        'students': 'student',
    }
    target_role = role_map.get(announcement.audience)

    for member in members:
        if target_role and member.role != target_role:
            continue
        notify_user(
            school, member.user,
            announcement.title,
            announcement.content,
            notification_type='announcement',
        )
