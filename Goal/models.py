from django.db import models
from django.contrib.auth import get_user_model
from SurvivalPlan.models import SurvivalPlan

User = get_user_model()


class Goal(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_amount = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255)

    plans = models.ManyToManyField(
        SurvivalPlan,
        related_name='goals',
        blank=True,
    )

    def __str__(self):
        return self.title
