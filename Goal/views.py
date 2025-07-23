from rest_framework import viewsets

from Goal.serializers import GoalSerializer
from Goal.models import Goal
from Goal.permissions import ReadAuthenticatedOrEditOwn


class GoalViewSet(viewsets.ModelViewSet):
    """View for Goal CRUD operations"""
    serializer_class = GoalSerializer
    permission_classes = [ReadAuthenticatedOrEditOwn]

    def get_queryset(self):
        return Goal.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
