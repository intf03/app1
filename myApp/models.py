from django.db import models

# Create your models here.
from django.db import models
class Products(models.Model):
    id = models.AutoField('id', primary_key = True)
    type = models.CharField('商品类型', max_length=255, default='')
    title = models.CharField('商品名称', max_length=255, default='')
    price = models.CharField('商品价格', max_length=255, default='')
    buy_len = models.CharField('商品销量', max_length=255, default='')
    img_src = models.CharField('商品图片', max_length=2555, default='')
    name = models.CharField('店铺名', max_length=255, default='')
    address = models.CharField('地址', max_length=255, default='')
    isFreeDelivery = models.CharField('是/否包邮', max_length=255, default='')
    href = models.CharField('详情链接', max_length=2555, default='')
    nameHref = models.CharField('店铺详情链接', max_length=2555, default='')

    class Meta:
        db_table = "products"

class User(models.Model):
    id = models.AutoField('id', primary_key = True)
    username = models.CharField('用户名', max_length=255, default='')
    password = models.CharField('密码', max_length=255, default='')
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = "user"