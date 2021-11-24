from django.contrib import admin
from . import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

## Contains path to each URL
urlpatterns = [
    path("", views.home, name="home"),
    path("signup", views.signup, name="signup"),
    path("login", views.signin, name="login"),
    path("logout", views.signout, name="logout"),
    path("forget_pass_req", views.forget_pass_req, name="forget_pass_req"),
    path("profile", views.prof, name="profile"),
    path("activate/<uid64>/<token>", views.activate, name="activate"),
    path("forget/<uid64>/<token>", views.forget_pass, name="forget"),
    path(
        "create_class_request/",
        views.create_class_request,
        name="create_class_request",
    ),
    path("join_class_request/", views.join_class_request, name="join_class_request"),
    path("class/<int:id>", views.render_class, name="render_class"),
    path(
        "unenroll_class/<int:classroom_id>", views.unenroll_class, name="unenroll_class"
    ),
    path("delete_class/<int:classroom_id>", views.delete_class, name="delete_class"),
    path(
        "create_assignment/<int:classroom_id>",
        views.create_assignment,
        name="create_assignment",
    ),
    path(
        "create_notification/<int:classroom_id>/<slug:name>",
        views.create_notification,
        name="create_notification",
    ),
    path(
        "delete_notification/<int:notification_id>",
        views.delete_notification,
        name="delete_notification",
    ),
    path(
        "assignment_summary/<int:assignment_id>",
        views.assignment_summary,
        name="assignment_summary",
    ),
    path(
        "delete_assignment/<int:assignment_id>",
        views.delete_assignment,
        name="delete_assignment",
    ),
    path(
        "submit_assignment_request/<int:assignment_id>",
        views.submit_assignment_request,
        name="submit_assignment_request",
    ),
    path(
        "submit_assignment_request_omr/<int:assignment_id>",
        views.submit_assignment_request_omr,
        name="submit_assignment_request_omr",
    ),
    path(
        "ans_key/<int:assignment_id>",
        views.ans_key_fun,
        name="ans_key",
    ),
    path(
        "sub_url/<int:assignment_id>",
        views.submission_summary,
        name="sub_url",
    ),
    path(
        "sub_omr_success/<int:assignment_id>",
        views.submit_omr_success,
        name="sub_omr_success",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
