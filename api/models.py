# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class UserToken (models.Model):
    access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    access_token_created_at = models.DateTimeField(auto_now_add=True)
    refresh_token_created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(default=0)

    def __str__(self):
        return self.access_token
