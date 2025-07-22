from django.contrib import admin
from SurvivalPlan.models import (
    SurvivalPlan,
    PlanItem,
    Expense
)

admin.site.register(SurvivalPlan)
admin.site.register(PlanItem)
admin.site.register(Expense)
