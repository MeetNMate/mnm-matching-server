from django.db.models import fields
from rest_framework import serializers
from .models import MatchingInfo, MatchingResult

class MatchingInfoSerializer(serializers.ModelSerializer):
    class Meta:
       model = MatchingInfo # 모델 설정
       fields = ('id', 'sex', 'age', 'mbti', 'user_smoking', 'mate_smoking') # 필드 생성

class MatchingReulstSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingResult
        fields = ('uid', 'mate_list', 'update_at')