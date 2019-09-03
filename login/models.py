from django.db import models
from django.contrib.auth.models import User

class infor(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    package = models.CharField(max_length = 25)
    started = models.BooleanField(default = False)
    price = models.FloatField(default = 0)
    start = models.DateField(null = True)
    end = models.DateField(null = True)
    passwordkey = models.CharField(max_length = 10,null = True)

    def __str__(self):
        return (str(self.user))