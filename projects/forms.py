from django import forms
from .models import Project, Category, Tag, Donation, Comment,Rating,Report


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "details",
            "category",
            "target",
            "tags",
            "start_time",
            "end_time",
        ]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "details": forms.Textarea(
                attrs={"rows": 5}
            ),
            "tags": forms.SelectMultiple(
                attrs={"size": 5}
            ),
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["amount"]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "min": "1",
                    "step": "0.01"
                }
            )
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": 
    forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write your comment..."
                }
            )
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]
        widgets = {
            "value": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "step": 1
                }
            )
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Why are you reporting this?"
                }
            )
        }