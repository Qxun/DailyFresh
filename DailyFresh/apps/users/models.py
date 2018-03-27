from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.models import BaseModel


# Create your models here.



class User(AbstractUser, BaseModel):
    """用户"""

    class Meta:
        db_table = "df_users"


<<<<<<< HEAD
class AreaInfo(models.Model):
    title = models.CharField(max_length=20)
    aParent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'df_area'


=======
>>>>>>> 665b20e7f457edc4d588b7fe3b5281f4e73363e5
class Address(BaseModel):
    """地址"""
    user = models.ForeignKey(User, verbose_name="所属用户")
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, verbose_name="邮政编码")
<<<<<<< HEAD
    province = models.ForeignKey(AreaInfo, related_name='province', null=True)
    city = models.ForeignKey(AreaInfo, related_name='city', null=True)
    district = models.ForeignKey(AreaInfo, related_name='district', null=True)
    isDefault = models.BooleanField(default=False)
=======
>>>>>>> 665b20e7f457edc4d588b7fe3b5281f4e73363e5

    class Meta:
        db_table = "df_address"
