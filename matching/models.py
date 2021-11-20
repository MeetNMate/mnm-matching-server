from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    use_matching = models.BooleanField(default=True)

    class Meta:
        db_table = 'user'

class MatchingInfo(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, related_name="matching_info", on_delete=models.CASCADE, db_column="uid")
    sex = models.IntegerField()
    age = models.FloatField()
    mbti = models.CharField(max_length=10)
    user_smoking = models.IntegerField()
    mate_smoking = models.FloatField()
    user_pet = models.IntegerField()
    user_pet_dog = models.IntegerField(default=0)
    user_pet_cat = models.IntegerField(default=0)
    user_pet_reptile_fish = models.IntegerField(default=0)
    user_pet_rodent = models.IntegerField(default=0)
    user_pet_bird = models.IntegerField(default=0)
    mate_pet = models.FloatField()
    mate_pet_dog = models.FloatField(default=0)
    mate_pet_cat = models.FloatField(default=0)
    mate_pet_reptile_fish = models.FloatField(default=0)
    mate_pet_rodent = models.FloatField(default=0)
    mate_pet_bird = models.FloatField(default=0)
    air_like_airconditioner = models.FloatField()
    air_like_heater = models.FloatField()
    noise_talking = models.FloatField()
    noise_music = models.FloatField()
    noise_alarm = models.IntegerField()
    user_bug_killer = models.FloatField()
    mate_bug_killer = models.IntegerField()
    user_cooking = models.IntegerField()
    mate_cooking = models.IntegerField()
    eat_together = models.IntegerField()
    share_item = models.FloatField()
    mate_alcohol = models.FloatField()
    mate_clean = models.FloatField()
    permission_to_enter = models.FloatField()

    class Meta:
        db_table = 'matching_info'

class MatchingResult(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, related_name="matching_result", on_delete=models.CASCADE, db_column="uid")
    mate_list = models.CharField(max_length=1000)
    update_at = models.DateTimeField()

    class Meta:
        db_table = 'matching_result'
