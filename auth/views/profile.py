from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

from itertools import chain

from ..models import Students, Teachers


## Home page rendering, you will see all the classes here
@login_required(login_url="login")
def prof(request):
    role = request.user.last_name
    name = request.user.first_name
    teacher_mapping = Teachers.objects.filter(teacher_id=request.user).select_related(
        "classroom_id"
    )
    student_mapping = Students.objects.filter(student_id=request.user).select_related(
        "classroom_id"
    )
    teachers_all = Teachers.objects.all()
    current_site = get_current_site(request)

    mappings = chain(teacher_mapping, student_mapping)
    return render(
        request,
        "auth/prof.html",
        {
            "name": name,
            "mappings": mappings,
            "teachers_all": teachers_all,
            "domain": current_site.domain,
            "role": role,
        },
    )
