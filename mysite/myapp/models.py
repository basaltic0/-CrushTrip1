from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from multiselectfield import MultiSelectField 

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender=models.CharField(blank=True, null=True,max_length=1, choices=[
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ])
    preferred_travel=MultiSelectField(max_choices=5,max_length=200,choices=[
        ('Nature','自然風光'),
        ('Hike','健行'),
        ('Beach','海灘度假'),
        ('City','城市觀光'),
        ('Cultural','文化探索'),
        ('Food','美食旅遊'),
        ('Backpack','背包旅行'),
        ('Luxury','奢華旅行'),
        ('History','歷史遺跡'),
        ('Shopping','購物旅遊'),
        ('Self','自駕遊'),
        ('Night','夜生活探索'),
        ('Slow','慢旅行'),
        ('Indoor','室內主題樂園'),
        ('Music','音樂與藝術節慶旅遊'),
        ('Farm','農場體驗與鄉村旅遊'),
        ])

    travel_partner = models.CharField(max_length=10, choices=[
        ('same', '同性'),
        ('different', '異性'),
        ('any', '都可以'),
    ], default='any')

    preferred_age_range = models.CharField(max_length=20, choices=[
        ('18-25', '18-25 歲'),
        ('26-35', '26-35 歲'),
        ('36-45', '36-45 歲'),
        ('46-60', '46-60 歲'),
        ('any', '不限'),
    ], default='any')


    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username


    class Meta:
        db_table = "CustomUser"

class crawlers_osusume(models.Model):
    parent_title  = models.CharField(max_length=50)
    heading = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    
    # online = models.ForeignKey('Online', default=1, on_delete=models.CASCADE, db_constraint=False)

class crawlers_main(models.Model):
    area = models.CharField(max_length=50)
    parent_title = models.CharField(max_length=50, default='空')
    heading = models.TextField()
    content = models.TextField()
    img = models.URLField(null=True)
    # online = models.ForeignKey('Online', default=1, on_delete=models.CASCADE, db_constraint=False)

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    spot = models.ForeignKey(crawlers_main, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'spot')  # 不重複加入