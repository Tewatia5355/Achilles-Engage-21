from django.core.mail import send_mail
from eng.settings import EMAIL_HOST_USER
from .models import Submissions, Assignments, Classrooms, Students, Notification
from django.contrib.auth.models import User
from datetime import datetime

## Function to send mail
def send_email(subject, recipient, message):
    if isinstance(recipient, str):
        send_mail(
            subject,
            message,
            EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=True,
        )
    elif isinstance(recipient, list):
        send_mail(
            subject,
            message,
            EMAIL_HOST_USER,
            recipient_list=recipient,
            fail_silently=True,
        )


## Mail when new assignment is posted in class, every student will be informed
def assignment_post_mail(classroom_id, assignment_id):
    users = Students.objects.filter(classroom_id=classroom_id)
    email_list = [user.student_id.email for user in users]
    assignment = Assignments.objects.get(pk=assignment_id)
    assignment_name = assignment.assignment_name
    classroom_name = Classrooms.objects.get(pk=classroom_id.id).classroom_name
    due_date = assignment.due_date
    message = "Dear Students, {} Test has been posted to {}. Due date of the Test is {}.\nAttempt it soon!\nThanks,\nAchilles".format(
        assignment_name, classroom_name, due_date
    )
    instructions = "Instructions of the assignment are: {}".format(
        assignment.instructions
    )
    message = message + "\n\n" + instructions
    subject = "New Assignment in {} class".format(classroom_name)
    send_email(subject, email_list, message)


## When you make a submission then a mail to student will be sent
def submission_done_mail(assignment_id, user):
    user_email = user.email
    assignment = Assignments.objects.get(pk=assignment_id)
    assignment_name = assignment.assignment_name
    message = "Dear Student {}, \nyour submission for the Test {} on {} has been received.\nWait for due date and time for Test to be graded!\n Thanks,\nAchilles".format(
        user.username, assignment_name, datetime.now()
    )
    subject = "Submission for assignment {}".format(assignment_name)
    send_email(subject, user_email, message)


## Mail when new Annoucement is made in class, every student will be informed
def notification_post_mail(classroom_id, notification_id):
    users = Students.objects.filter(classroom_id=classroom_id)
    email_list = [user.student_id.email for user in users]
    notification = Notification.objects.get(pk=notification_id)
    notification_header = notification.header
    classroom_name = Classrooms.objects.get(pk=classroom_id.id).classroom_name
    message = "Dear Students,\n{} Annoucement has been posted to {}.\nThanks,\nAchilles".format(
        notification_header, classroom_name
    )
    subject = "New Annoucement in {} class".format(classroom_name)
    send_email(subject, email_list, message)
