from django.db import models

class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __str__(self):
		return self.user.username