from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.files import File
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
from datetime import datetime
from django.forms.models import model_to_dict
from itertools import chain
import os
import pandas as pd
import time

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


## rendering class page from profile page
@login_required(login_url="login")
@access_class("profile")
def render_class(request, id):
    name = request.user.first_name
    classroom = Classrooms.objects.get(pk=id)
    try:
        assignments = Assignments.objects.filter(classroom_id=id)
        for assignment in assignments:
            if assignment.ans_key == None:
                assignment.delete()
        assignments = Assignments.objects.filter(classroom_id=id)
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

    ## Marking Test is available by student to be solved by student or not
    for assignment in assignments:
        dt1 = datetime.now()
        dt2 = datetime.combine(assignment.due_date, assignment.due_time)
        if dt1.time() >= dt2.time():
            assignment.is_available = False
        else:
            assignment.is_available = True
        assignment.save()

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
                time.sleep(2)
                try:
                    os.remove(f"result_{assignment.id}.csv")
                except Exception as e:
                    print("\n\n", e, "\n\n")

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
