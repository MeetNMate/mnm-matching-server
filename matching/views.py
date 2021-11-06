from django.utils import timezone
import pandas as pd
import numpy as np

from django.shortcuts import render
from .models import MatchingInfo, MatchingResult

from rest_framework import serializers, viewsets
from .serializers import MatchingInfoSerializer

class MatchingInfoViewSet(viewsets.ModelViewSet):
    queryset = MatchingInfo.objects.all()
    serializer_class = MatchingInfoSerializer

def index(request):
    matching_info = MatchingInfo.objects.all() # MatchingInfo 테이블의 모든 객체를 불러온다.
    context = {'matching_info': matching_info}
    return render(request, 'matching/matching_info.html', context)

def matching_result(request):
    user_id = 8

    # 원본
    user_data = pd.DataFrame(MatchingInfo.objects.filter(id=user_id).values()).iloc[0]
    df = pd.DataFrame(list(MatchingInfo.objects.all().values()))
    
    # 변형
    dataset = df[['mbti', 'sex', 'age', 'air_night_airconditioner', 'noise_alarm', 'eat_together', 'share_item', 'mate_alcohol', 'mate_clean', 'permission_to_enter']]
    user = user_data[['mbti', 'sex', 'age', 'air_night_airconditioner', 'noise_alarm', 'eat_together', 'share_item', 'mate_alcohol', 'mate_clean', 'permission_to_enter']]

    # 데이터 필터링
    if user_data['mate_pet'] == 1:
        is_not_user_pet = df['user_pet'] == 0
        dataset = dataset[is_not_user_pet]
    elif user_data['mate_pet'] == 0.5:
        user['pet_dog'], user['pet_cat'], user['pet_reptile_fish'], user['pet_rodent'], user['pet_bird'] = user_data['mate_pet_dog'], user_data['mate_pet_cat'], user_data['mate_pet_reptile_fish'], user_data['mate_pet_rodent'], user_data['mate_pet_bird']
        dataset[['pet_dog', 'pet_cat', 'pet_reptile_fish', 'pet_rodent', 'pet_bird']] = df[['user_pet_dog', 'user_pet_cat', 'user_pet_reptile_fish', 'user_pet_rodent', 'user_pet_bird']]

    if user_data['mate_smoking'] != 0.5:
        user['smoking'] = df.iloc[0]['mate_smoking']
        dataset['smoking'] = df['user_smoking']

    if user_data['air_like_airconditioner'] != 0:
        user['air_like_airconditioner'] = df.iloc[0]['air_like_airconditioner']
        dataset['air_like_airconditioner'] = df['air_like_airconditioner']

    if user_data['air_like_heater'] != 0.5:
        user['air_like_heater'] = df.iloc[0]['air_like_heater']
        dataset['air_like_heater'] = df['air_like_heater']

    if user_data['noise_talking'] != 0:
        user['noise_talking'] = df.iloc[0]['noise_talking']
        dataset['noise_talking'] = df['noise_talking']

    if user_data['noise_music'] != 0:
        user['noise_music'] = df.iloc[0]['noise_music']
        dataset['noise_music'] = df['noise_music']

    if user_data['mate_bug_killer'] != 0:
        user['bug_killer'] = df.iloc[0]['mate_bug_killer']
        dataset['bug_killer'] = df['user_bug_killer']

    if user_data['mate_cooking'] != 0:
        user['cooking'] = df.iloc[0]['mate_cooking']
        dataset['cooking'] = df['user_cooking']
    
    distance_result = np.zeros(len(dataset))

    # 기준 사용자와 다른 사용자 간의 거리를 구한다.
    for i in range(len(dataset)):
        distance_result[i] = distance(user, dataset.iloc[i])

    # 오름차순으로 정렬하여 인덱스들의 리스트를 리턴한다.
    result_index_list = np.argsort(distance_result)[:20]

    result = [df.iloc[i]['id'] for i in result_index_list]
    
    content = {'id': user_id, 'result': result}

    # MatchingResult
    update_at = timezone.now()
    MatchingResult(uid=user_id, mate_list=result, update_at=update_at).save()

    return render(request, 'matching/matching_result.html', content)

MBTI_DISTANCE = np.array([
    [0.25, 0.25, 0.25, 0, 0.25, 0, 0.25, 0.25, 1, 1, 1, 1, 1, 1, 1, 1, 0.5],
    [0.25, 0.25, 0, 0.25, 0, 0.25, 0.25, 0.25, 1, 1, 1, 1, 1, 1, 1, 1, 0.5],
    [0.25, 0, 0.25, 0.25, 0.25, 0.25, 0.25, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0.5],
    [0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0, 1, 1, 1, 1, 1, 1, 1, 0.5],
    [0.25, 0, 0.25, 0.25, 0.25, 0.25, 0.25, 0, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0.5],
    [0, 0.25, 0.25, 0.25, 0.25, 0.25, 0, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    [0.25, 0.25, 0.25, 0.25, 0.25, 0, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0, 0.5],
    [0.25, 0.25, 0, 0.25, 0, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0.5],
    [1, 1, 1, 0, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0.5, 0, 0.5, 0, 0.5],
    [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0, 0.5, 0, 0.5, 0.5],
    [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0.5, 0, 0.5, 0, 0.5],
    [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.75, 0, 0.5, 0, 0.5, 0.5],
    [1, 1, 1, 1, 0.75, 0.5, 0.75, 0.75, 0.5, 0, 0.5, 0, 0.25, 0.25, 0.25, 0.25, 0.5],
    [1, 1, 1, 1, 0.75, 0.5, 0.75, 0.75, 0, 0.5, 0, 0.5, 0.25, 0.25, 0.25, 0.25, 0.5],
    [1, 1, 1, 1, 0.75, 0.5, 0.75, 0.75, 0.5, 0, 0.5, 0, 0.25, 0.25, 0.25, 0.25, 0.5],
    [1, 1, 1, 1, 0.75, 0.5, 0, 0.75, 0, 0.5, 0, 0.5, 0.25, 0.25, 0.25, 0.25, 0.5], 
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
])

MBTI_MAP = dict(
    infp=0,
    enfp=1,
    infj=2,
    enfj=3,
    intj=4,
    entj=5,
    intp=6,
    entp=7,
    isfp=8,
    esfp=9,
    istp=10,
    estp=11,
    isfj=12,
    esfj=13,
    istj=14,
    estj=15,
    모른다=16
)

def distance(u1, u2):
    ''' 사용자 사이의 거리 리턴'''
    mbti = MBTI_DISTANCE[MBTI_MAP[u1[0]]][MBTI_MAP[u2[0]]] ** 2
    sum_ = np.sum(np.power((u2[1:]-u1[1:]),2))
    return np.sqrt(sum_ + mbti)


