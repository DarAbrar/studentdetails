from django.db import models

class Candidate(models.Model):
    mobile = models.CharField(max_length=20)
    candidate_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    is_marked = models.BooleanField(default=False)

class MarkedCandidate(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    is_marked = models.BooleanField(default=False)