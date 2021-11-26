from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.files import File
from django.forms.models import model_to_dict

from datetime import datetime
from itertools import chain
import os
import pandas as pd
import time, re

from .. import mail
from ..codegen import generate_class_code
from ..decorators import access_class, teacher_required, student_required
from ..models import (
    Classrooms,
    Teachers,
    Students,
    Assignments,
    Submissions,
    Notification,
)


## Student unenrolling from a class
@login_required(login_url="login")
@student_required("profile")
def unenroll_class(request, classroom_id):
    classroom = Classrooms.objects.get(pk=classroom_id)
    student_mapping = Students.objects.filter(
        student_id=request.user, classroom_id=classroom
    ).delete()
    return redirect("profile")


## Teacher deleting a class
@login_required(login_url="login")
@teacher_required("profile")
def delete_class(request, classroom_id):
    classroom = Classrooms.objects.get(pk=classroom_id)
    teacher_mapping = Teachers.objects.get(
        teacher_id=request.user, classroom_id=classroom
    )
    teacher_mapping.delete()
    classroom.delete()
    return redirect("profile")


## Teacher deleting a class
@login_required(login_url="login")
def send_invites(request, class_code):
    classroom = Classrooms.objects.get(class_code=class_code)
    if request.method == "POST":
        name = request.user.first_name
        emails = list((request.POST.get("emails")).split(","))
        print("\n\n", request.POST, "\n\n")
        print("\n\n", emails, "\n\n")
        regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        gen_email_notExist = []
        gen_email_exist = []
        for email in emails:
            email = email.strip()
            if re.search(regex, email):
                try:
                    user = User.objects.get(username=email)
                    try:
                        student = Students.objects.get(
                            student_id=request.user, classroom_id=classroom
                        )
                        continue
                    except:
                        gen_email_exist.append(email)
                except User.DoesNotExist:
                    gen_email_notExist.append(email)
        if len(gen_email_notExist) > 0:
            mail.send_invites_notExist(
                gen_email_notExist, class_code, name, get_current_site(request).domain
            )
        if len(gen_email_exist) > 0:
            mail.send_invites_exist(
                gen_email_exist, class_code, name, get_current_site(request).domain
            )
        return JsonResponse({"status": "SUCCESS"})
    try:
        student = Students.objects.filter(
            student_id=request.user, classroom_id=classroom
        )
        user = User.objects.get(pk=request.user.id)
        if student.count() != 0 or user.last_name == "Teacher":
            return redirect("profile")
    except Exception as e:
        print(e)
        return redirect("profile")
    student = Students(student_id=request.user, classroom_id=classroom)
    student.save()
    return redirect("render_class", id=classroom.id)


## rendering class page from profile page
@login_required(login_url="login")
@access_class("profile")
def render_class(request, id):
    try:
        directory = str(os.getcwd())
        files_in_directory = os.listdir(directory)
        filtered_files = [file for file in files_in_directory if file.endswith(".csv")]
        for file in filtered_files:
            path_to_file = os.path.join(directory, file)
            os.remove(path_to_file)
    except Exception as e:
        print("\n\n", e, "\n\n")
    name = request.user.first_name
    classroom = Classrooms.objects.get(pk=id)
    try:
        assignments = Assignments.objects.filter(classroom_id=id)
        for assignment in assignments:
            dt1 = datetime.now()
            dt2 = datetime.combine(assignment.due_date, assignment.due_time)
            if dt1.date() > dt2.date():
                assignment.is_available = False
            elif dt1.date() == dt2.date() and dt1.time() >= dt2.time():
                assignment.is_available = False
            else:
                assignment.is_available = True
            assignment.save()
            if assignment.ans_key == None:
                assignment.delete()
        assignments = Assignments.objects.filter(classroom_id=id).order_by(
            "-due_date", "-due_time"
        )
    except Exception as e:
        print("Asgn error: ", e)
        assignments = None

    try:
        notifications = Notification.objects.filter(classroom_id=id).order_by(
            "-posted_date", "-posted_time"
        )

    except Exception as e:
        print("Notification error: ", e)
        notifications = None

    try:
        students = Students.objects.filter(classroom_id=id)
    except Exception as e:
        print("Std error: ", e)
        students = None
    role = request.user.last_name

    ## Empty test list, will contain details about [test, submission marks of kids, total marks of the test]
    test = []
    if role == "Student" and assignments != None:
        for assignment in assignments:
            student_id = Students.objects.get(
                classroom_id=assignment.classroom_id, student_id=request.user.id
            )
            total_marks = assignment.num_ques * assignment.positive_marks
            try:
                ## Check if any submission is given by student
                submission = Submissions.objects.get(
                    assignment_id=assignment.id, student_id=student_id
                )
                dt1 = datetime.now()
                dt2 = datetime.combine(assignment.due_date, assignment.due_time)

                ## if due date is past, show marks of student to
                if dt1.time() >= dt2.time():
                    test.append([assignment, submission, total_marks])

                ## if due date isn't past, don't show marks right now
                else:
                    test.append([assignment, -1, None])
            except Exception as e:
                print("Calc error: ", e)
                ## means submission isn't made, let him make it, if test is still open
                test.append([assignment, None, None])
    else:

        ## Role is "Teacher"
        for assignment in assignments:
            dt1 = datetime.now()
            dt2 = datetime.combine(assignment.due_date, assignment.due_time)
            result = []
            ## If result isn't made and due date is past, make CSV of result and commit it to database
            if dt1.time() >= dt2.time() and assignment.result == "":
                submissions = Submissions.objects.filter(assignment_id=assignment.id)
                for submission in submissions:
                    student = User.objects.filter(
                        username=submission.student_id.student_id
                    )
                    student = student[0].first_name
                    solution_file = (
                        "http://"
                        + str(get_current_site(request))
                        + "/media/"
                        + str(submission.solution_file)
                    )
                    result.append(
                        [
                            submission.student_id.student_id,
                            student,
                            submission.submitted_date,
                            submission.submitted_time,
                            submission.marks_alloted,
                            submission.response_key,
                            solution_file,
                        ]
                    )
                    print("\n\n", solution_file, "\n\n")

                columns = [
                    "EMAIL",
                    "NAME",
                    "SUBMITTED DATE",
                    "SUBMITTED TIME",
                    "MARKS",
                    "RESPONSES",
                    "SOLUTION FILE",
                ]

                ## Make result CSV using pandas
                my_df = pd.DataFrame(result, columns=columns)
                my_df.to_csv(f"result_{assignment.id}.csv")
                f = open(f"result_{assignment.id}.csv", "r")
                assignment.result = File(f)
                assignment.save()
                f.closed
            test.append([assignment, None, None])

    current_site = get_current_site(request)
    teachers = Teachers.objects.filter(classroom_id=id)
    return render(
        request,
        "auth/subj.html",
        {
            "notifications": notifications,
            "classroom": classroom,
            "assignments": assignments,
            "students": students,
            "teachers": teachers,
            "domain": current_site.domain,
            "role": role,
            "test": test,
            "name": name,
        },
    )


## Create a new Class function
@login_required(login_url="login")
def create_class_request(request):
    if request.POST.get("action") == "post":
        classrooms = Classrooms.objects.all()
        existing_codes = []
        for classroom in classrooms:
            existing_codes.append(classroom.class_code)

        class_name = request.POST.get("class_name")

        class_code = generate_class_code(6, existing_codes)
        classroom = Classrooms(classroom_name=class_name, class_code=class_code)
        classroom.save()
        teacher = Teachers(teacher_id=request.user, classroom_id=classroom)
        teacher.save()
        return JsonResponse({"status": "SUCCESS"})


## Join a new class function
@login_required(login_url="login")
def join_class_request(request):
    if request.POST.get("action") == "post":
        code = request.POST.get("class_code")
        try:
            classroom = Classrooms.objects.get(class_code=code)
            student = Students.objects.filter(
                student_id=request.user, classroom_id=classroom
            )
            if student.count() != 0:
                return redirect("profile")
        except Exception as e:
            print(e)
            return JsonResponse({"status": "FAIL", "message": str(e)})
        student = Students(student_id=request.user, classroom_id=classroom)
        student.save()
        return JsonResponse({"status": "SUCCESS"})
