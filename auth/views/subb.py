from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..decorators import student_required
from ..models import Assignments, Students, Submissions
from ..form import *
from .. import mail

from datetime import datetime

## Function to handle OMR submission for a test
@login_required(login_url="login")
@student_required("profile")
def submit_assignment_request_omr(request, assignment_id):
    return render("profile")


## Function to handle manual submission for a test
@login_required(login_url="login")
@student_required("profile")
def submit_assignment_request(request, assignment_id):
    assignment = Assignments.objects.get(pk=assignment_id)
    student_id = Students.objects.get(
        classroom_id=assignment.classroom_id, student_id=request.user.id
    )
    if request.method == "POST":
        assignment = Assignments.objects.get(pk=assignment_id)
        try:
            ans_key = assignment.ans_key
            num_ques = assignment.num_ques
            marks = 0
            response_key = ""
            for i in range(1, num_ques + 1):
                response_key += str(request.POST.get(f"{i}"))
                if ans_key[i - 1] == response_key[i - 1]:
                    marks = marks + assignment.positive_marks
                elif response_key[i - 1] != "0":
                    marks = marks - assignment.negative_marks
            print("\n\n", ans_key, "\n", response_key, "\n", marks, "\n\n")
            submission = Submissions(
                assignment_id=assignment,
                student_id=student_id,
                marks_alloted=marks,
                response_key=response_key,
            )
            submission.save()
            mail.submission_done_mail(assignment_id, request.user)
            return redirect("render_class", assignment.classroom_id.id)

        except Exception as e:
            print(str(e))
            return render("profile")


## take submission of a student using this function
@csrf_exempt
@login_required(login_url="login")
@student_required("home")
def submission_summary(request, assignment_id):
    assignment = Assignments.objects.filter(pk=assignment_id).first()
    return render(
        request,
        "auth/subb.html",
        {
            "assignment_id": assignment.id,
            "num_ques": assignment.num_ques,
        },
    )
