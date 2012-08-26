from django.db import models

# Create your models here.
class RadioItem(models.Model):
	user_title = models.CharField(max_length=50)
	video_id = models.CharField(max_length=20)
	submission_date = models.DateField()
	played = models.BooleanField(default=False)