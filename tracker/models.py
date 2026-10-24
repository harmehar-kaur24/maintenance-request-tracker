from django.db import models


class Request(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    urgency = models.IntegerField(default=1)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
