from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from itertools import chain
from ..decorators import teacher_required
from ..models import Teachers, Students, Assignments, Submissions
from ..form import *
from .. import mail

# Function for handling correct response from a Test
@login_required(login_url="login")
@teacher_required("profile")
def ans_key_fun(request, assignment_id):
    if request.method == "POST":
        assignment = Assignments.objects.get(pk=assignment_id)
        try:
            # rec_ans is string of correct responses from the user
            rec_ans = ""
            num_ques = assignment.num_ques
            for i in range(1, num_ques + 1):
                rec_ans += str(request.POST.get(f"{i}"))
            assignment.ans_key = rec_ans
            assignment.save()

            # mailing every student that one test has been created inside your classroom
            # mail.assignment_post_mail(assignment.classroom_id, assignment.id)

            return redirect("render_class", assignment.classroom_id.id)
        except Exception as e:
            print(e)
            assignment.delete()
            return redirect("profile")
    return redirect("profile")


## Function used to create the assignment
@login_required(login_url="login")
@teacher_required("profile")
def create_assignment(request, classroom_id):
    if request.method == "POST":
        try:
            assignment_name = request.POST.get("asgn_name")
            due_date = request.POST.get("due_date")
            due_time = request.POST.get("due_time")
            classroom_id = Classrooms.objects.get(pk=classroom_id)
            instructions = request.POST.get("instructions")
            num_ques = int(request.POST.get("num_ques"))
            positive_marks = int(request.POST.get("positive_marks"))
            negative_marks = int(request.POST.get("negative_marks"))
            file_name = request.FILES.get("file")
            res_show = request.POST["res_show"]
            if res_show == "Yes":
                res_show = True
            else:
                res_show = False
            assignment = Assignments(
                assignment_name=assignment_name,
                due_date=due_date,
                due_time=due_time,
                instructions=instructions,
                classroom_id=classroom_id,
                num_ques=num_ques,
                positive_marks=positive_marks,
                negative_marks=negative_marks,
                question_file=file_name,
                show_result=res_show,
            )
            assignment.save()

            # redirect to take correct response for current assignment
            return render(
                request,
                "auth/ans_key.html",
                {"assignment_id": assignment.id, "num_ques": num_ques},
            )

        except Exception as e:
            print("\n\n", e, "\n\n\n")
            return render(
                request,
                "auth/create_asgn.html",
                {"classroom": classroom_id},
            )
    return render(
        request,
        "auth/create_asgn.html",
        {"classroom": classroom_id},
    )


## Function to handle assignment summary request
@login_required(login_url="login")
@teacher_required("profile")
def assignment_summary(request, assignment_id):
    assignment = Assignments.objects.filter(pk=assignment_id).first()
    no_of_students = Students.objects.filter(classroom_id=assignment.classroom_id)
    submission = Submissions.objects.filter(assignment_id=assignment_id)
    return render(
        request,
        "auth/asgn_summary.html",
        {
            "assignment": assignment,
            "no_of_students": no_of_students,
            "submissions_count": submission.count,
        },
    )


## Function to delete assignment
@login_required(login_url="login")
@teacher_required("home")
def delete_assignment(request, assignment_id):
    try:
        assignment = Assignments.objects.get(pk=assignment_id)
        classroom_id = assignment.classroom_id.id
        Assignments.objects.get(pk=assignment_id).delete()
        return redirect("render_class", id=classroom_id)
    except Exception(e):
        return redirect("home")
