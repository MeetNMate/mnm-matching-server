from django.db.models.query import QuerySet
from django.http import response
from django.utils import timezone
import pandas as pd
import numpy as np

from django.shortcuts import get_object_or_404, render
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MatchingInfo, MatchingResult
from .serializers import MatchingInfoSerializer, MatchingReulstSerializer

class MatchingInfoView(APIView):
    """
    GET /infos
    GET /infos/{id}
    """
    def get(self, request, **kwargs):
        id = kwargs.get('id')
        if id is None:
            infos = MatchingInfo.objects.all()
            serializer = MatchingInfoSerializer(infos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            info = get_object_or_404(MatchingInfo, id=id)
            # info = MatchingInfo.objects.get(id=id)
            serializer = MatchingInfoSerializer(info)
            return Response(serializer.data, status=status.HTTP_200_OK)

    """
    POST /infos
    """
    def post(self, request, **kwargs):
        serializer = MatchingInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # mate_matching(id)
            return Response("success", status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """
    PUT /infos/{id}
    """
    def put(self, request, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            info = get_object_or_404(MatchingInfo, id=id)
            serializer = MatchingInfoSerializer(info, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response("success", status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
        else:
            return Response("failed", status=status.HTTP_400_BAD_REQUEST)

    """
    DELETE /infos/{id}
    """
    def delete(self, request, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            get_object_or_404(MatchingInfo, id=id).delete()
            return Response("success", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("failed", status=status.HTTP_400_BAD_REQUEST)

class MatchingResultView(APIView):
    """ 
    GET /results
    GET /results/{uid} 
    """
    def get(self, request, **kwargs):
        if kwargs.get('uid') is None:
            queryset = MatchingResult.objects.all()
            serializer = MatchingReulstSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            uid = kwargs.get('uid')
            queryset = MatchingResult.objects.filter(uid=uid).order_by('-update_at')[0]
            serializer = MatchingReulstSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

    """
    PUT /result/{uid}
    """
    def put(self, request, **kwargs):
        """ 해당 uid의 사용자에게 메이트 매칭을 진행한다. """
        if kwargs.get('uid') is None:
            return Response("invalid request", status=status.HTTP_400_BAD_REQUEST)
        else:
            uid = kwargs.get('uid')
            mate_matching(uid)
            return Response("success", status.HTTP_200_OK)


def index(request):
    matching_info = MatchingInfo.objects.all() # MatchingInfo 테이블의 모든 객체를 불러온다.
    context = {'matching_info': matching_info}
    return render(request, 'matching/matching_info.html', context)

def matching_result(request):
    user_id = 10

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

def mate_matching(uid):
    # 원본
    user_data = pd.DataFrame(MatchingInfo.objects.filter(id=uid).values()).iloc[0]
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

    # DB에 결과 저장
    update_at = timezone.now()
    r = MatchingResult(uid=uid, mate_list=result, update_at=update_at).save()
    print(r)


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


