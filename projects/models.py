from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
class Category(models.Model):
 name=models.CharField(max_length=100,unique=True)
 def __str__(self): return self.name
class Tag(models.Model):
 name=models.CharField(max_length=50,unique=True)
 def __str__(self): return self.name
class Project(models.Model):
 creator=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='projects')
 title=models.CharField(max_length=200); details=models.TextField(); category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='projects')
 target=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(1)]); start_time=models.DateTimeField(); end_time=models.DateTimeField(); tags=models.ManyToManyField(Tag,blank=True); featured=models.BooleanField(default=False); cancelled=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
 @property
 def raised(self): return self.donations.aggregate(x=models.Sum('amount'))['x'] or 0
 @property
 def progress(self): return min(float(self.raised/self.target*100),100) if self.target else 0
 @property
 def rating(self): return self.ratings.aggregate(x=models.Avg('value'))['x'] or 0
 @property
 def running(self): return self.start_time<=timezone.now()<=self.end_time and not self.cancelled
class ProjectImage(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='images'); image=models.ImageField(upload_to='projects/')
class Donation(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='donations'); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); amount=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(1)]); created_at=models.DateTimeField(auto_now_add=True)
class Comment(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='comments'); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); text=models.TextField(); parent=models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='replies'); created_at=models.DateTimeField(auto_now_add=True)
class Rating(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='ratings'); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); value=models.PositiveSmallIntegerField()
 class Meta: unique_together=('project','user')
class Report(models.Model):
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); project=models.ForeignKey(Project,null=True,blank=True,on_delete=models.CASCADE); comment=models.ForeignKey(Comment,null=True,blank=True,on_delete=models.CASCADE); reason=models.TextField(); created_at=models.DateTimeField(auto_now_add=True)
