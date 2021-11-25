from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import base64
from django.core.files.base import ContentFile


from ..utils import calc_resp
from ..decorators import student_required
from ..models import Assignments, Students, Submissions
from .. import mail


## Function to handle OMR submission for a test
@login_required(login_url="login")
@student_required("profile")
def submit_assignment_request_omr(request, assignment_id):
    assignment = Assignments.objects.get(pk=assignment_id)
    student_id = Students.objects.get(
        classroom_id=assignment.classroom_id, student_id=request.user.id
    )
    try:
        submission = Submissions.objects.get(
            assignment_id=assignment.id, student_id=student_id.id
        )
        if submission != None:
            submission.delete()
    except Exception as e:
        print(e)
    ans_key = assignment.ans_key
    num_ques = assignment.num_ques
    marks = 0
    formati, imgstr = request.POST["file"].split(";base64,")
    ext = formati.split("/")[-1]
    submission = Submissions(
        assignment_id=assignment,
        student_id=student_id,
        marks_alloted=0,
        response_key="",
        omr_file=ContentFile(base64.b64decode(imgstr), name="temp." + ext),
        solution_file=request.FILES["file2"],
    )
    submission.save()
    path = "/media/" + str(submission.omr_file)
    response_key = calc_resp(path)
    if response_key == None:
        print("\n\nOMR is Faulty\n\n")
        return render(
            "auth/sub_omr.html",
            {"responses": None, "num_ques": None, "assignment_id": assignment.id},
        )
    for i in range(num_ques):
        if response_key[i] == "0":
            continue
        elif response_key[i] == ans_key[i]:
            marks = marks + assignment.positive_marks
        else:
            marks = marks - assignment.negative_marks
    submission.marks_alloted = marks
    submission.response_key = response_key[0:num_ques]
    submission.save()
    response = []
    for i in range(num_ques):
        if response_key[i] == "0":
            response.append([i + 1, "Unattempted"])
        else:
            response.append([i + 1, response_key[i]])
    return render(
        request,
        "auth/sub_omr.html",
        {
            "responses": response,
            "num_ques": num_ques,
            "assignment_id": assignment.id,
        },
    )


@login_required(login_url="login")
@student_required("profile")
def submit_omr_success(request, assignment_id):
    assignment = Assignments.objects.get(pk=assignment_id)
    # mail.submission_done_mail(assignment_id, request.user)
    return redirect("render_class", assignment.classroom_id.id)


## Function to handle manual submission for a test
@login_required(login_url="login")
@student_required("profile")
def submit_assignment_request(request, assignment_id):
    assignment = Assignments.objects.get(pk=assignment_id)
    student_id = Students.objects.get(
        classroom_id=assignment.classroom_id, student_id=request.user.id
    )
    try:
        submission = Submissions.objects.get(
            assignment_id=assignment.id, student_id=student_id.id
        )
        if submission != None:
            submission.delete()
    except Exception as e:
        print(e)
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
                solution_file=request.FILES["file2"],
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
            "assignment": assignment,
            "num_ques": assignment.num_ques,
        },
    )


@login_required(login_url="login")
@student_required("home")
def fill_omr(request, assignment_id):
    return render(request, "auth/fill_omr.html", {"assignment_id": assignment_id})


@login_required(login_url="login")
@student_required("home")
def res_key_check(request, assignment_id, submission_id):
    assignment = Assignments.objects.get(pk=assignment_id)
    submission = Submissions.objects.get(pk=submission_id)

    ans_key = assignment.ans_key
    res_key = submission.response_key
    listt = []
    for i in range(assignment.num_ques):
        if res_key[i] == "0":
            listt.append((i + 1, ans_key[i], "Unattempted", "Blank"))
        else:
            if ans_key[i] == res_key[i]:
                listt.append((i + 1, ans_key[i], res_key[i], "Correct"))
            else:
                listt.append((i + 1, ans_key[i], res_key[i], "Wrong"))
    return render(
        request,
        "auth/check_response.html",
        {
            "listt": listt,
            "pos": assignment.positive_marks,
            "neg": assignment.negative_marks,
            "marks": submission.marks_alloted,
        },
    )
