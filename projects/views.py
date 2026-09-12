from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ProjectForm,
    DonationForm,
    CommentForm,
    RatingForm,
    ReportForm,
)
from .models import (
    Project,
    ProjectImage,
    Donation,
    Comment,
    Rating,
    Report,
    Category,
)


def home(request):
    qs = Project.objects.filter(
        cancelled=False,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )

    top = sorted(
        qs,
        key=lambda x: x.rating,
        reverse=True
    )[:5]

    q = request.GET.get("q", "")

    if q:
        results = Project.objects.filter(
            Q(title__icontains=q) |
            Q(tags__name__icontains=q)
        ).distinct()
    else:
        results = []

    return render(request, "projects/home.html", {
        "top": top,
        "latest": Project.objects.order_by("-created_at")[:5],
        "featured": Project.objects.filter(
            featured=True
        ).order_by("-created_at")[:5],
        "categories": Category.objects.all(),
        "results": results,
        "q": q,
    })


def detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    tag_ids = project.tags.values_list(
        "id",
        flat=True
    )

    if tag_ids:
        similar_projects = (
            Project.objects
            .filter(
                tags__id__in=tag_ids,
                cancelled=False
            )
            .exclude(pk=project.pk)
            .distinct()[:4]
        )
    else:
        similar_projects = Project.objects.none()

    return render(request, "projects/detail.html", {
        "project": project,
        "donation_form": DonationForm(),
        "comment_form": CommentForm(),
        "rating_form": RatingForm(),
        "report_form": ReportForm(),
        "similar_projects": similar_projects,
    })


@login_required
def create(request):
    form = ProjectForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.creator = request.user
        project.save()

        form.save_m2m()

        for image in request.FILES.getlist("images"):
            ProjectImage.objects.create(
                project=project,
                image=image
            )

        return redirect(
            "project_detail",
            project.pk
        )

    return render(request, "projects/form.html", {
        "form": form
    })


@login_required
def donate(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk
    )

    form = DonationForm(request.POST)

    if form.is_valid():
        donation = form.save(commit=False)

        donation.project = project
        donation.user = request.user

        donation.save()

        messages.success(
            request,
            "Donation recorded."
        )

    return redirect(
        "project_detail",
        pk
    )


@login_required
def comment(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk
    )

    form = CommentForm(request.POST)

    if form.is_valid():
        new_comment = form.save(commit=False)

        new_comment.project = project
        new_comment.user = request.user

        new_comment.save()

    return redirect(
        "project_detail",
        pk
    )


@login_required
def rate(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk
    )

    form = RatingForm(request.POST)

    if form.is_valid():
        Rating.objects.update_or_create(
            project=project,
            user=request.user,
            defaults={
                "value": form.cleaned_data["value"]
            }
        )

    return redirect(
        "project_detail",
        pk
    )


@login_required
def report(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk
    )

    form = ReportForm(request.POST)

    if form.is_valid():
        Report.objects.create(
            user=request.user,
            project=project,
            reason=form.cleaned_data["reason"]
        )

        messages.success(
            request,
            "Project reported."
        )

    return redirect(
        "project_detail",
        pk
    )


@login_required
def report_comment(request, comment_id):
    comment_obj = get_object_or_404(
        Comment,
        pk=comment_id
    )

    form = ReportForm(request.POST)

    if form.is_valid():
        Report.objects.create(
            user=request.user,
            comment=comment_obj,
            reason=form.cleaned_data["reason"]
        )

        messages.success(
            request,
            "Comment reported."
        )

    return redirect(
        "project_detail",
        comment_obj.project.pk
    )


@login_required
def cancel(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk,
        creator=request.user
    )

    if project.running and project.progress < 25:
        project.cancelled = True
        project.save()

        messages.success(
            request,
            "Project cancelled."
        )
    else:
        messages.error(
            request,
            "Project can only be cancelled while running and below 25% funded."
        )

    return redirect(
        "project_detail",
        pk
    )