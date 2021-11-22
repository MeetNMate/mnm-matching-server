import pymysql
import pandas as pd
import numpy as np

def main():
    try:
        df = load_data('survey_result_211024.xlsx')
    except Exception as e:
        print("[데이터 로딩 중 에러 발생] " + e)

    try:
        df = preprocess_data(df)
    except Exception as e:
        print("[데이터 전처리 중 에러 발생] " + e)

    print(df)

    try:
        insert_data(df)
    except Exception as e:
        print("[DB에 데이터 삽입 중 에러 발생] " + e)

def load_data(path):
    df = pd.read_excel(path)
    return df

def pre_age(x):
    if '40대 이후' == str(x):
        return 1
    elif '30대' == str(x):
        return 0.8
    elif '27 ~ 29' == str(x):
        return 0.6
    elif '24 ~ 26' == str(x):
        return 0.4
    elif '20 ~ 23' == str(x):
        return 0.2
    elif '10대' == str(x):
        return 0
    else:
        return np.nan
    
def pre_mate_smoking(x):
    if '흡연자' == str(x):
        return 1
    elif '상관없음'== str(x):
        return 0.5
    elif '비흡연자' == str(x):
        return 0
    else:
        return np.nan

def pre_mate_pet(x):
    if '어떠한 동물도 안된다.' in str(x):
        return 1
    elif '어떤 동물이든 괜찮다.' in str(x):
        return 0
    else:
        return 0.5 # NaN, 그 외
    
def pre_air_like_airconditioner(x):
    if '더위를 많이 타서 에어컨을 일찍부터 튼다' in str(x) or '여름에 항상 에어컨을 켜놓는다' in str(x):
        return 1
    elif '에어컨을 틀고 못잔다' in str(x):
        return 0
    else:
        return 0.5 # Nan, 그 외

def pre_air_like_heater(x):
    if '추위를 많이 타서 난방을 일찍부터 튼다' in str(x):
        return 1
    elif '과한 난방은 답답해하는 편이다'in str(x):
        return 0
    else:
        return 0.5 # 난방에 대해 신경쓰지 않는다고 판단
    
def pre_noise_talking(x):
    if '10분 이전의 말소리(통화/게임)도 신경쓰인다' in str(x):
        return 1
    elif '10분 이상의 말소리(통화/게임)은 신경쓰인다'in str(x):
        return 0.5
    else:
        return 0
    
def pre_noise_music(x):
    if '10분 이전의 동영상/음악 소리도 신경쓰인다' in str(x):
        return 1
    elif '10분 이상의 동영상/음악 소리는 신경쓰인다'in str(x):
        return 0.5
    else:
        return 0    

def pre_user_bug_killer(x):
    if '잡는데 거리낌이 없다' in str(x):
        return 1
    elif '시키면 잡을 수 있다'in str(x):
        return 0.75
    elif '절대 못잡는다' in str(x):
        return 0
    else:
        return np.nan
    
def pre_share_item(x):
    if '말 안하고 사용해도 괜찮다' in str(x):
        return 1
    elif '사용하기 전 허락을 받으면 괜찮다'in str(x):
        return 0.75
    elif '괜찮지 않다(안된다)' in str(x):
        return 0
    else:
        return np.nan    
    
def pre_mate_alcohol(x):
    if '메이트가 술 냄새를 풍기는 것은 싫다' in str(x):
        return 1
    elif '메이트가 술을 많이 마신 것 같은 모습을 보이면 싫다'in str(x):
        return 0.66
    elif '메이트가 술주정만 하지 않으면 된다' in str(x):
        return 0.33
    elif '메이트의 술 문제는 신경쓰지 않는다' in str(x):
        return 0
    else:
        return np.nan
    
def pre_mate_clean(x):
    if '메이트의 공간까지 신경쓰인다' in str(x):
        return 1
    elif '공유하는 공간의 경우 신경쓰인다'in str(x):
        return 0.5
    elif '내 공간만 아니면 신경쓰이지 않는다' in str(x):
        return 0
    else:
        return np.nan
    
def pre_permission_to_enter(x):
    if '누구든 데려오면 안된다.' in str(x):
        return 1
    elif '미리 말만 하면 지인이 출입해도 상관없다.'in str(x):
        return 0.5
    elif '본인이 없을 때 말없이 지인이 잠깐 출입해도 상관없다.' in str(x):
        return 0
    else:
        return np.nan

def preprocess_data(df):
    # timestamp 컬럼 제거
    df = df.drop(columns='TIMESTAMP')

    # 컬럼 이름 변경
    df.columns = ['sex', 'age', 'mbti', 'user_smoking', 'mate_smoking', 'user_pet', 'user_pet_category', 'mate_pet_category', 
              'air', 'user_bug_killer', 'mate_bug_killer', 'user_cooking', 'mate_cooking', 'eat_together', 'share_item', 'noise', 'mate_alcohol', 
              'mate_clean', 'permission_to_enter']

    # uid 컬럼 추가
    df['uid'] = df.index + 1

    # 컬럼 순서 변경
    df = df[['uid', 'sex', 'age', 'mbti', 'user_smoking', 'mate_smoking', 'user_pet', 'user_pet_category', 'mate_pet_category', 
            'air', 'user_bug_killer', 'mate_bug_killer', 'user_cooking', 'mate_cooking', 'eat_together', 'share_item', 'noise', 'mate_alcohol', 
            'mate_clean', 'permission_to_enter']]

    # mbti 대문자로 변경
    df['mbti'] = df['mbti'].apply(lambda x : x.upper())
    
    # 컬럼 별 데이터 0~1 사이 값으로 변환
    df['sex'] = df['sex'].apply(lambda x : 1 if str(x) == '여자' else 0)
    df['age'] = df['age'].apply(lambda x : pre_age(x))
    df['user_smoking'] = df['user_smoking'].apply(lambda x : 1 if str(x) == '흡연자' else 0)
    df['mate_smoking'] = df['mate_smoking'].apply(lambda x : pre_mate_smoking(x))
    
    df['user_pet'] = df['user_pet'].apply(lambda x : 1 if str(x) == '그렇다' else 0)
    df['user_pet_dog'] = df['user_pet_category'].apply(lambda x : 1 if '강아지' in str(x) else 0)
    df['user_pet_cat'] = df['user_pet_category'].apply(lambda x : 1 if '고양이' in str(x) else 0)
    df['user_pet_reptile_fish'] = df['user_pet_category'].apply(lambda x : 1 if '파충류, 어류' in str(x) else 0)
    df['user_pet_rodent'] = df['user_pet_category'].apply(lambda x : 1 if '설치류' in str(x) else 0)
    df['user_pet_bird'] = df['user_pet_category'].apply(lambda x : 1 if '조류' in str(x) else 0)
    df = df.drop(columns='user_pet_category')
    
    df['mate_pet'] = df['mate_pet_category'].apply(lambda x : pre_mate_pet(x))
    df['mate_pet_dog'] = df['mate_pet_category'].apply(lambda x : 0.5 if '강아지' in str(x) or '어떤 동물이든 괜찮다.' in str(x) else 0)
    df['mate_pet_cat'] = df['mate_pet_category'].apply(lambda x : 0.5 if '고양이' in str(x) or '어떤 동물이든 괜찮다.' in str(x) else 0)
    df['mate_pet_reptile_fish'] = df['mate_pet_category'].apply(lambda x : 0.5 if '파충류, 어류' in str(x) or '어떤 동물이든 괜찮다.' in str(x) else 0)
    df['mate_pet_rodent'] = df['mate_pet_category'].apply(lambda x : 0.5 if '설치류' in str(x) or '어떤 동물이든 괜찮다.' in str(x) else 0)
    df['mate_pet_bird'] = df['mate_pet_category'].apply(lambda x : 0.5 if '조류' in str(x) or '어떤 동물이든 괜찮다.' in str(x) else 0)
    df = df.drop(columns='mate_pet_category')
    
    df['air'] = df['air'].fillna('해당하는 상황 없음')
    df['air_like_airconditioner'] = df['air'].apply(lambda x : pre_air_like_airconditioner(x))
    df['air_like_heater'] = df['air'].apply(lambda x : pre_air_like_heater(x))
    df = df.drop(columns='air')
    
    df['noise'] = df['noise'].fillna('신경쓰지 않는다.')
    df['noise_talking'] = df['noise'].apply(lambda x : pre_noise_talking(x))
    df['noise_music'] = df['noise'].apply(lambda x : pre_noise_music(x))
    df['noise_alarm'] = df['noise'].apply(lambda x : 1 if '지속적인 알람소리는 신경쓰인다' in str(x) else 0)
    df = df.drop(columns='noise')
    
    df['user_bug_killer'] = df['user_bug_killer'].apply(lambda x : pre_user_bug_killer(x))
    # mean으로 결측치 채움
    df['user_bug_killer'] = df['user_bug_killer'].fillna(df['user_bug_killer'].mean())
    df['mate_bug_killer'] = df['mate_bug_killer'].apply(lambda x : 1 if '벌레를 잡을 수 있어야만 한다' in str(x) else 0)
    
    df['user_cooking'] = df['user_cooking'].apply(lambda x : 1 if '외부 음식(포장, 배달)' in str(x) else 0)
    df['mate_cooking'] = df['mate_cooking'].apply(lambda x : 1 if '불편하다' in str(x) else 0)
    df['eat_together'] = df['eat_together'].apply(lambda x : 1 if '같이 먹는 걸 선호한다' in str(x) else 0)
    
    df['share_item'] = df['share_item'].apply(lambda x : pre_share_item(x))
    # mean으로 결측치 채움
    df['share_item'] = df['share_item'].fillna(df['share_item'].mean())
    
    df['mate_alcohol'] = df['mate_alcohol'].apply(lambda x : pre_mate_alcohol(x))
    # mean으로 결측치 채움
    df['mate_alcohol'] = df['mate_alcohol'].fillna(df['mate_alcohol'].mean())
    
    df['mate_clean'] = df['mate_clean'].apply(lambda x : pre_mate_clean(x))
    # mean으로 결측치 채움
    df['mate_clean'] = df['mate_clean'].fillna(df['mate_clean'].mean())
    
    df['permission_to_enter'] = df['permission_to_enter'].apply(lambda x : pre_permission_to_enter(x))
    
    return df

def insert_data(df):
    conn = pymysql.connect(host = 'project-mnm-matching-db.ctixol1fxh7r.ap-northeast-2.rds.amazonaws.com', 
                       port = 3306, 
                       user = 'root', 
                       password = 'milktea1121', 
                       db = 'matching')

    cursor = conn.cursor()

    # user 테이블에 삽입
    query = "INSERT INTO user (id, use_matching) VALUES (%s, true);"

    data = [x for x in df['uid']]

    cursor.executemany(query, data)

    conn.commit()

    # matching_info 테이블에 삽입
    query = "INSERT INTO matching_info (uid, sex, age, mbti, user_smoking, mate_smoking, user_pet, user_bug_killer, mate_bug_killer, user_cooking, mate_cooking, eat_together, share_item, mate_alcohol, mate_clean, permission_to_enter, user_pet_dog, user_pet_cat, user_pet_reptile_fish, user_pet_rodent, user_pet_bird, mate_pet, mate_pet_dog, mate_pet_cat, mate_pet_reptile_fish, mate_pet_rodent, mate_pet_bird, air_like_airconditioner, air_like_heater, noise_talking, noise_music, noise_alarm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    data = [tuple(x) for x in df.values] # dataframe을 executemany에 넣을 수 있는 형태로 변환

    cursor.executemany(query, data)
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()