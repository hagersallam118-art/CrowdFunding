from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from projects.models import Donation

from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User
from .tokens import make_activation_token, get_user_from_activation_token


def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    form = RegisterForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        user.is_active = False
        user.set_password(
            form.cleaned_data["password"]
        )
        user.save()

        token = make_activation_token(user)

        encoded_token = urlsafe_base64_encode(
              force_bytes(token)
              ).rstrip("=")

        activation_url = request.build_absolute_uri(
              reverse(
              "activate",
        args=[encoded_token]
         )
         )

        send_mail(
            "Activate your Crowd-Funding account",
            f"Welcome {user.first_name}! "
            f"Activate your account within 24 hours:\n"
            f"{activation_url}",
            None,
            [user.email],
        )

        return render(
            request,
            "accounts/activation_sent.html",
            {
                "email": user.email
            }
        )

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


def activate_view(request, token):
   
    try:
       token += "=" * (-len(token) % 4)
       token = force_str(urlsafe_base64_decode(token))
    except (ValueError, TypeError, UnicodeDecodeError):
     return render(
        request,
        "accounts/activation_invalid.html"
    )

    user_id = get_user_from_activation_token(token)

    if not user_id:
        return render(
            request,
            "accounts/activation_invalid.html"
        )

    user = get_object_or_404(
        User,
        pk=user_id
    )

    if user.is_active:
        messages.info(
            request,
            "This account is already activated."
        )
        return redirect("login")

    user.is_active = True
    user.save(update_fields=["is_active"])

    messages.success(
        request,
        "Account activated successfully. You can now login."
    )

    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    form = LoginForm(
        request,
        data=request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        if not user.is_active:
            form.add_error(
                None,
                "Please activate your account from the email first."
            )

        else:
            login(
                request,
                user
            )

            return redirect("profile")

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


def logout_view(request):
    logout(request)

    return redirect("login")


@login_required
def profile_view(request):

    my_projects = (
        request.user.projects
        .all()
        .order_by("-created_at")
    )

    my_donations = (
        Donation.objects
        .filter(donor=request.user)
        .select_related("project")
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "user_obj": request.user,
            "my_projects": my_projects,
            "my_donations": my_donations,
        }
    )


@login_required
def profile_edit_view(request):

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form
        }
    )


@login_required
def delete_account_view(request):

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        if not request.user.check_password(password):

            messages.error(
                request,
                "Incorrect password."
            )

        else:
            user = request.user

            logout(request)

            user.delete()

            return redirect("register")

    return render(
        request,
        "accounts/delete_account.html"
    )


password_reset = PasswordResetView.as_view(
    template_name="accounts/password_reset.html",
    email_template_name="accounts/password_reset_email.txt",
    subject_template_name="accounts/password_reset_subject.txt",
    success_url="/password-reset/done/",
)