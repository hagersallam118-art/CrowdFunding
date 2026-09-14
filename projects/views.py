from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg
from django.utils import timezone

from .forms import DonationForm, ProjectForm, CommentForm, RatingForm, ReportForm
from .models import Project, ProjectImage, Comment, Rating, Report


def project_list(request):
    projects = Project.objects.filter(is_cancelled=False).order_by("-created_at")

    return render(
        request,
        "projects/project_list.html",
        {"projects": projects}
    )


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    total_donations = sum(
        donation.amount for donation in project.donations.all()
    )

    if project.target > 0:
        progress = (total_donations / project.target) * 100
    else:
        progress = 0

    comments = project.comments.filter(parent__isnull=True).order_by("-created_at")
    average_rating = project.ratings.aggregate(
         avg=Avg("value")
        )["avg"] or 0
    similar_projects = Project.objects.filter(
         tags__in=project.tags.all(),
         is_cancelled=False
              ).exclude(
         pk=project.pk
             ).distinct()[:4]


    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "total_donations": total_donations,
            "progress": progress,
            "comments": comments,
            "comment_form": CommentForm(),
            "average_rating": average_rating,
            "rating_form": RatingForm(),
            "report_form": ReportForm(),
            "similar_projects": similar_projects,
        }
    )

@login_required
def add_comment(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()

    return redirect("project_detail", pk=pk)

@login_required
def add_reply(request, pk, comment_id):
    project = get_object_or_404(Project, pk=pk)
    parent_comment = get_object_or_404(
        Comment,
        pk=comment_id,
        project=project
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.project = project
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()

    return redirect("project_detail", pk=pk)

@login_required
def add_rating(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = RatingForm(request.POST)

        if form.is_valid():
            Rating.objects.update_or_create(
                project=project,
                user=request.user,
                defaults={
                    "value": form.cleaned_data["value"]
                }
            )

    return redirect("project_detail", pk=pk)

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            form.save_m2m()

            images = request.FILES.getlist("images")

            for image in images:
                ProjectImage.objects.create(
                    project=project,
                    image=image
                )

            return redirect("project_detail", pk=project.pk)

    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {"form": form}
    )


@login_required
def donate(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.is_cancelled:
        return redirect("project_detail", pk=project.pk)

    now = timezone.now()

    if now < project.start_time:
     messages.error(
        request,
        "This project has not started yet."
    )
     return redirect("project_detail", pk=project.pk)

    if now > project.end_time:
      messages.error(
        request,
        "This project has already ended."
    )
      return redirect("project_detail", pk=project.pk)

    if request.method == "POST":
        form = DonationForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]

            total_donations = sum(
                donation.amount
                for donation in project.donations.all()
            )

            remaining = project.target - total_donations

            if amount > remaining:
                form.add_error(
                    "amount",
                    f"You can donate a maximum of {remaining}."
                )
            else:
                donation = form.save(commit=False)
                donation.project = project
                donation.donor = request.user
                donation.save()

                return redirect("project_detail", pk=project.pk)

    else:
        form = DonationForm()

    return render(
        request,
        "projects/donate.html",
        {
            "form": form,
            "project": project
        }
    )

@login_required
def report_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.report_type = "project"
            report.project = project
            report.save()

    return redirect("project_detail", pk=pk)

@login_required
def report_comment(request, pk, comment_id):
    project = get_object_or_404(Project, pk=pk)

    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        project=project
    )

    if request.method == "POST":
        form = ReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.report_type = "comment"
            report.project = project
            report.comment = comment
            report.save()

    return redirect("project_detail", pk=pk)

@login_required
def cancel_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user != project.creator:
        messages.error(request, "You are not allowed to cancel this project.")
        return redirect("project_detail", pk=pk)

    total_donations = sum(
        donation.amount
        for donation in project.donations.all()
    )

    if total_donations < project.target * Decimal("0.25"):
        project.is_cancelled = True
        project.save(update_fields=["is_cancelled"])

        messages.success(
            request,
            "Project cancelled successfully."
        )
    else:
        messages.error(
            request,
            "You cannot cancel this project because donations reached 25% of the target."
        )

    return redirect("project_detail", pk=pk)