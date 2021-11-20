from rest_framework.serializers import ModelSerializer
from .models import User, MatchingInfo, MatchingResult

class UserSerializer(ModelSerializer):
    class Meta:
       model = User
       fields = '__all__'    

class MatchingInfoSerializer(ModelSerializer):
    class Meta:
       model = MatchingInfo
       fields = '__all__'

class MatchingReulstSerializer(ModelSerializer):
    class Meta:
        model = MatchingResult
        fields = '__all__'
