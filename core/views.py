from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from django.utils import timezone

from projects.models import Category, Project


def home(request):
    now = timezone.now()

    categories = Category.objects.all()

    latest_projects = Project.objects.order_by('-created_at')[:5]

    featured_projects = Project.objects.filter(
        featured=True
    ).order_by('-created_at')[:5]

    top_projects = (
        Project.objects
        .filter(
            start_time__lte=now,
            end_time__gte=now,
            cancelled=False
        )
        .annotate(avg_rating=Avg('ratings__value'))
        .order_by('-avg_rating')[:5]
    )

    query = request.GET.get('q', '').strip()

    search_results = Project.objects.none()

    if query:
        search_results = Project.objects.filter(
            Q(title__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    return render(request, 'core/home.html', {
        'categories': categories,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'top_projects': top_projects,
        'query': query,
        'search_results': search_results,
    })


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    projects = Project.objects.filter(
        category=category
    ).order_by('-created_at')

    return render(request, 'core/category_detail.html', {
        'category': category,
        'projects': projects,
    })