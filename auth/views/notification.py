from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from itertools import chain
from ..decorators import teacher_required
from ..models import Teachers, Students, Classrooms, Notification
from ..form import *
from .. import mail

# Function for creating new Annoucement in class
@login_required(login_url="login")
@teacher_required("profile")
def create_notification(request, classroom_id, name):
    if request.method == "POST":
        try:
            heading = request.POST.get("noti_header")
            message = request.POST.get("noti_message")
            attachment = request.FILES.get("file", False)
            classroom_id = Classrooms.objects.get(pk=classroom_id)
            if attachment:
                notification = Notification(
                    classroom_id=classroom_id,
                    header=heading,
                    message=message,
                    author=name,
                    attachment=attachment,
                    attached=True,
                )
            else:
                notification = Notification(
                    classroom_id=classroom_id,
                    header=heading,
                    message=message,
                    author=name,
                )
            notification.save()
            # Mailing Annoucement to each student
            mail.notification_post_mail(notification.classroom_id, notification.id)
            # redirect to class page
            return redirect("render_class", classroom_id.id)

        except Exception as e:
            print("\n\n", e, "\n\n\n")
            return render(
                request,
                "auth/create_notification.html",
                {"classroom": classroom_id.id, "name": name},
            )
    return render(
        request,
        "auth/create_notification.html",
        {"classroom": classroom_id, "name": name},
    )


# Function for deleting a annoucement in class
@login_required(login_url="login")
@teacher_required("profile")
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(pk=notification_id)
        classroom_id = notification.classroom_id.id
        Notification.objects.get(pk=notification_id).delete()
        return redirect("render_class", id=classroom_id)
    except Exception(e):
        return redirect("home")
