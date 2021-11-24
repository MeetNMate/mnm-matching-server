from django.utils import timezone
import pandas as pd
import numpy as np
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MatchingInfo, MatchingResult, User
from .serializers import UserSerializer, MatchingInfoSerializer, MatchingReulstSerializer

class UserView(APIView):
    def get(self, request, **kwargs):
        id = kwargs.get('id')
        if id is None:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user = get_object_or_404(User, id=id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        id = kwargs.get('id')
        if id is not None and request.data['id'] == id:
            info = get_object_or_404(User, id=id)
            serializer = UserSerializer(info, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
        else:
            return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            get_object_or_404(User, id=id).delete()
            return Response("사용자 정보 삭제에 성공하였습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            User.objects.all().delete()
            return Response("사용자 정보를 모두 삭제하였습니다.", status=status.HTTP_400_BAD_REQUEST)

class MatchingInfoView(APIView):
    def get(self, request, **kwargs):
        uid = kwargs.get('uid')
        if uid is None:
            infos = MatchingInfo.objects.all()
            serializer = MatchingInfoSerializer(infos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            info = get_object_or_404(MatchingInfo, uid=uid)
            serializer = MatchingInfoSerializer(info)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        data = data_preprocess(request.data) # 매칭 정보 전처리
        serializer = MatchingInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        uid = kwargs.get('uid')
        if uid is not None and request.data['uid'] == uid:
            info = get_object_or_404(MatchingInfo, uid=uid)
            serializer = MatchingInfoSerializer(info, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
        else:
            return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        uid = kwargs.get('uid')
        if uid is not None:
            get_object_or_404(MatchingInfo, uid=uid).delete()
            return Response("매칭 정보 삭제에 성공하였습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)

class MatchingResultView(APIView):
    def get(self, request, **kwargs):
        uid = kwargs.get('uid')
        if uid is None:
            queryset = MatchingResult.objects.all()
            serializer = MatchingReulstSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                queryset = MatchingResult.objects.filter(uid=uid).order_by('-update_at')[0]
                serializer = MatchingReulstSerializer(queryset)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response("매칭 결과가 존재하지 않습니다.", status.HTTP_400_BAD_REQUEST)

    def post(self, request, **kwargs):
        uid = kwargs.get('uid')
        try:
            mate_list = mate_matching(uid) # 메이트 매칭
            update_at = timezone.now()
            print(mate_list)
            print(update_at)
            MatchingResult(uid_id=uid, mate_list=mate_list, update_at=update_at).save()
            return Response(str(mate_list)[1:-1], status.HTTP_201_CREATED)
        except:
            return Response("메이트 매칭 중 에러 발생", status.HTTP_500_INTERNAL_SERVER_ERROR)

def data_preprocess(data):
    """ 매칭 정보 전처리 """
    age = int(data['age'])
    if age >= 40:
        age = 1
    elif 30 <= age <= 39:
        age = 0.8
    elif 27 <= age <= 29:
        age = 0.6
    elif 24 <= age <= 26:
        age = 0.4
    elif 20 <= age <= 23:
        age = 0.2
    else:
        age = 0
    data['age'] = age

    mate_smoking = int(data['mate_smoking'])
    if mate_smoking == 2:
        mate_smoking = 0
    elif mate_smoking == 3:
        mate_smoking = 0.5
    data['mate_smoking'] = mate_smoking

    

    mate_pet = int(data['mate_pet'])
    if mate_pet == 1:
        mate_pet = 0
    elif mate_pet == 2:
        mate_pet = 0.5
    else:
        mate_pet = 0
    data['mate_pet'] = mate_pet

    air_like_airconditioner = int(data['air_like_airconditioner'])
    if air_like_airconditioner == 2:
        air_like_airconditioner = 0.5
    elif air_like_airconditioner == 3:
        air_like_airconditioner = 0
    data['air_like_airconditioner'] = air_like_airconditioner

    air_like_heater = int(data['air_like_heater'])
    if air_like_heater == 2:
        air_like_heater = 0.5
    elif air_like_heater == 3:
        air_like_heater = 0
    data['air_like_heater'] = air_like_heater

    noise_talking = int(data['noise_talking'])
    if noise_talking == 2:
        noise_talking = 0.5
    elif noise_talking == 3:
        noise_talking = 0
    data['noise_talking'] = noise_talking

    noise_music = int(data['noise_music'])
    if noise_music == 2:
        noise_music = 0.5
    elif noise_music == 3:
        noise_music = 0
    data['noise_music'] = noise_music
    
    user_bug_killer = int(data['user_bug_killer'])
    if user_bug_killer == 2:
        user_bug_killer = 0.5
    elif user_bug_killer == 3:
        user_bug_killer = 0
    data['user_bug_killer'] = user_bug_killer

    share_item = int(data['share_item'])
    if share_item == 2:
        share_item = 0.75
    elif share_item == 3:
        share_item = 0
    data['share_item'] = share_item

    mate_alcohol = int(data['mate_alcohol'])
    if mate_alcohol == 2:
        mate_alcohol = 0.66
    elif mate_alcohol == 3:
        mate_alcohol = 0.33
    elif mate_alcohol == 4:
        mate_alcohol = 0
    data['mate_alcohol'] = mate_alcohol

    mate_clean = int(data['mate_clean'])
    if mate_clean == 2:
        mate_clean = 0.5
    elif mate_clean == 3:
        mate_clean = 0
    data['mate_clean'] = mate_clean

    permission_to_enter = int(data['permission_to_enter'])
    if permission_to_enter == 2:
        permission_to_enter = 0.5
    elif permission_to_enter == 3:
        permission_to_enter = 0
    data['permission_to_enter'] = permission_to_enter
    print(data['permission_to_enter'])
    return data 

def mate_matching_all():
    """ 모든 사용자 메이트 매칭 """
    infos = MatchingInfo.objects.all()
    for info in infos:
        mate_matching(info.uid)

def mate_matching(uid):
    """ 메이트 매칭 """
    # 원본
    user_data = pd.DataFrame(MatchingInfo.objects.filter(uid=uid).values()).iloc[0]
    df = pd.DataFrame(list(MatchingInfo.objects.exclude(uid=uid).values()))

    # 변형
    dataset = df[['mbti', 'sex', 'age','noise_alarm', 'eat_together', 'share_item', 'mate_alcohol', 'mate_clean', 'permission_to_enter']]
    user = user_data[['mbti', 'sex', 'age','noise_alarm', 'eat_together', 'share_item', 'mate_alcohol', 'mate_clean', 'permission_to_enter']]

    # 데이터 필터링
    if user_data['mate_pet'] == 1:
        is_not_user_pet = df['user_pet'] == 0
        dataset = dataset[is_not_user_pet]
    elif user_data['mate_pet'] == 0.5:
        user['pet_dog'], user['pet_cat'], user['pet_reptile_fish'], user['pet_rodent'], user['pet_bird'] = user_data['mate_pet_dog'], user_data['mate_pet_cat'], user_data['mate_pet_reptile_fish'], user_data['mate_pet_rodent'], user_data['mate_pet_bird']
        dataset[['pet_dog', 'pet_cat', 'pet_reptile_fish', 'pet_rodent', 'pet_bird']] = df[['user_pet_dog', 'user_pet_cat', 'user_pet_reptile_fish', 'user_pet_rodent', 'user_pet_bird']]

    if user_data['mate_smoking'] != 0.5:
        user['smoking'] = df.loc[0,'mate_smoking']
        dataset['smoking'] = df['user_smoking']

    if user_data['air_like_airconditioner'] != 0:
        user['air_like_airconditioner'] = df.loc[0,'air_like_airconditioner']
        dataset['air_like_airconditioner'] = df['air_like_airconditioner']

    if user_data['air_like_heater'] != 0.5:
        user['air_like_heater'] = df.loc[0,'air_like_heater']
        dataset['air_like_heater'] = df['air_like_heater']

    if user_data['noise_talking'] != 0:
        user['noise_talking'] = df.loc[0,'noise_talking']
        dataset['noise_talking'] = df['noise_talking']

    if user_data['noise_music'] != 0:
        user['noise_music'] = df.loc[0,'noise_music']
        dataset['noise_music'] = df['noise_music']

    if user_data['mate_bug_killer'] != 0:
        user['bug_killer'] = df.loc[0,'mate_bug_killer']
        dataset['bug_killer'] = df['user_bug_killer']

    if user_data['mate_cooking'] != 0:
        user['cooking'] = df.loc[0,'mate_cooking']
        dataset['cooking'] = df['user_cooking']

    distance_result = np.zeros(len(dataset))

    # 기준 사용자와 다른 사용자 간의 거리를 구한다.
    for i in range(len(dataset)):
        distance_result[i] = distance(user, dataset.iloc[i])

    # 오름차순으로 정렬하여 인덱스들의 리스트를 리턴한다.
    result_index_list = np.argsort(distance_result)[:20]
    print(result_index_list)

    return [df.loc[i,'uid_id'] for i in result_index_list]

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
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
])

MBTI_MAP = dict(
    INFP=0,
    ENFP=1,
    INFJ=2,
    ENFJ=3,
    INTJ=4,
    ENTJ=5,
    INTP=6,
    ENTP=7,
    ISFP=8,
    ESFP=9,
    ISTP=10,
    ESTP=11,
    ISFJ=12,
    ESFJ=13,
    ISTJ=14,
    ESTJ=15,
    모른다=16
)

def distance(u1, u2):
    """ 사용자 사이의 거리 리턴 """
    mbti = MBTI_DISTANCE[MBTI_MAP[u1[0]]][MBTI_MAP[u2[0]]] ** 2
    sum_ = np.sum(np.power((u2[1:]-u1[1:]),2))
    return np.sqrt(sum_ + mbti)


