from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from .models import *
from .forms import *
def home(request):
 qs=Project.objects.filter(cancelled=False,start_time__lte=timezone.now(),end_time__gte=timezone.now()); top=sorted(qs,key=lambda x:x.rating,reverse=True)[:5]
 q=request.GET.get('q',''); results=Project.objects.filter(Q(title__icontains=q)|Q(tags__name__icontains=q)).distinct() if q else []
 return render(request,'projects/home.html',{'top':top,'latest':Project.objects.order_by('-created_at')[:5],'featured':Project.objects.filter(featured=True)[:5],'categories':Category.objects.all(),'results':results,'q':q})
def detail(request,pk):
 p=get_object_or_404(Project,pk=pk); return render(request,'projects/detail.html',{'project':p,'donation_form':DonationForm(),'comment_form':CommentForm(),'rating_form':RatingForm(),'report_form':ReportForm()})
@login_required
def create(request):
 f=ProjectForm(request.POST or None)
 if request.method=='POST' and f.is_valid(): p=f.save(commit=False);p.creator=request.user;p.save();f.save_m2m();return redirect('project_detail',p.pk)
 return render(request,'projects/form.html',{'form':f})
@login_required
def donate(request,pk):
 p=get_object_or_404(Project,pk=pk);f=DonationForm(request.POST)
 if f.is_valid(): d=f.save(commit=False);d.project=p;d.user=request.user;d.save();messages.success(request,'Donation recorded.')
 return redirect('project_detail',pk)
@login_required
def comment(request,pk):
 p=get_object_or_404(Project,pk=pk);f=CommentForm(request.POST)
 if f.is_valid(): c=f.save(commit=False);c.project=p;c.user=request.user;c.save()
 return redirect('project_detail',pk)
@login_required
def rate(request,pk):
 p=get_object_or_404(Project,pk=pk);f=RatingForm(request.POST)
 if f.is_valid(): Rating.objects.update_or_create(project=p,user=request.user,defaults={'value':f.cleaned_data['value']})
 return redirect('project_detail',pk)
@login_required
def report(request,pk):
 p=get_object_or_404(Project,pk=pk);f=ReportForm(request.POST)
 if f.is_valid(): Report.objects.create(user=request.user,project=p,reason=f.cleaned_data['reason'])
 return redirect('project_detail',pk)
@login_required
def cancel(request,pk):
 p=get_object_or_404(Project,pk=pk,creator=request.user)
 if p.running and p.progress<25:p.cancelled=True;p.save();messages.success(request,'Project cancelled.')
 else:messages.error(request,'Project can only be cancelled while running and below 25% funded.')
 return redirect('project_detail',pk)
