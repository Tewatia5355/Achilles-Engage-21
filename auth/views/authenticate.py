from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from eng import settings

from ..tokens import generate_token
from ..decorators import login_excluded
from .. import mail

# Create your views here.


def home(request):
    return render(request, "auth/index.html")


## function to handle registration of new account
@login_excluded("profile")
def signup(request):
    if request.method == "POST":
        name = request.POST["nam"]
        email = request.POST["email"]
        password = request.POST["pass"]
        role = request.POST["role1"]

        if User.objects.filter(username=email):
            messages.error(request, "User already exist with same email!")
            return redirect("home")

        if not (name.replace(" ", "")).isalpha():
            messages.error(request, "Name should consist of Alphabets only!")
            return redirect("home")

        myuser = User.objects.create_user(email, email, password)
        myuser.first_name = name
        myuser.last_name = role
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your Account has been successfully created!")

        # Welcome Email to user
        subject = "Welcome to Achilles Platform - Engage '21"
        message = (
            "Hello "
            + myuser.first_name
            + "!!\nWelcome to Achilles Platform.\nThank you for visiting our Website\nA confirmation mail has been sent to you, please confirm you email,\n(Please check Spam for same)\n\nThank You\n Achilles"
        )
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Confirmation to user
        current_site = get_current_site(request)
        email_subject = "Confirm Email Address @ Achilles - Engage '21"
        message2 = render_to_string(
            "email_confirmation.html",
            {
                "name": myuser.first_name,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token": generate_token.make_token(myuser),
            },
        )
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = False
        email.send()
        return redirect("login")
    return render(request, "auth/signup.html")


## Login request function
@login_excluded("profile")
def signin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["pass"]
        role = request.POST["role1"]
        user = authenticate(username=email, password=password)
        if user is not None and role == user.last_name:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Bad Credentials")
            return redirect("home")

    return render(request, "auth/login.html")


## Logout function
@login_required(login_url="login")
def signout(request):
    logout(request)
    messages.success(request, "Logged Out Succesfully!")
    return redirect("home")


## Email activation function
@login_excluded("profile")
def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return render(
            request,
            "auth/index.html",
            context={"Name": myuser.first_name, "Role": myuser.last_name},
        )
    else:
        return render(request, "activation_failed.html")


@login_excluded("profile")
def forget_pass_req(request):
    # Email to user for new password
    if request.method == "POST":
        try:
            myuser = User.objects.filter(username=request.POST["email"])
            myuser = myuser[0]
        except Exception as e:
            messages.success(request, "Email is not valid")
            return redirect("home")
        current_site = get_current_site(request)
        email_subject = "Recover Password @ Achilles - Engage '21"
        message2 = render_to_string(
            "forget_pass.txt",
            {
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token": generate_token.make_token(myuser),
            },
        )
        print("\nHeree\n")
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = False
        email.send()
        print("\nMailsent\n")
        messages.success(request, "Recovery email is sent!!")
        return redirect("home")
    return render(request, "auth/forget.html")


@login_excluded("profile")
def forget_pass(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except Exception as e:
        myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
        if request.method == "POST":
            password = request.POST["cpass"]
            myuser.set_password(password)
            myuser.save()
            messages.success(request, "New password is set succesfully!")
            return redirect("home")
        return render(
            request,
            "auth/forget_req.html",
            {
                "uid64": uid64,
                "token": token,
            },
        )
    messages.success(request, "Unauthorized Access!!")
    return redirect("home")
