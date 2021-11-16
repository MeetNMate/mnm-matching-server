from django.db.models import fields
from rest_framework.serializers import ModelSerializer
from .models import MatchingInfo, MatchingResult

class MatchingInfoSerializer(ModelSerializer):
    class Meta:
       model = MatchingInfo
       fields = '__all__'

class MatchingReulstSerializer(ModelSerializer):
    class Meta:
        model = MatchingResult
        fields = '__all__'
