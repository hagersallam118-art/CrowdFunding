from django import forms
from .models import Project,ProjectImage,Donation,Comment,Rating,Report
class ProjectForm(forms.ModelForm):
 class Meta:
  model=Project; fields=['title','details','category','target','start_time','end_time','tags']
  widgets={'start_time':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end_time':forms.DateTimeInput(attrs={'type':'datetime-local'})}
class ImageForm(forms.ModelForm):
 class Meta: model=ProjectImage; fields=['image']
class DonationForm(forms.ModelForm):
 class Meta: model=Donation; fields=['amount']
class CommentForm(forms.ModelForm):
 class Meta: model=Comment; fields=['text']
class RatingForm(forms.ModelForm):
 class Meta: model=Rating; fields=['value']; widgets={'value':forms.Select(choices=[(i,i) for i in range(1,6)])}
class ReportForm(forms.ModelForm):
 class Meta: model=Report; fields=['reason']
