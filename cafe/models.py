from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
# Create your models here.


class User(AbstractUser):
    email = None
    username = None
    phone = models.CharField(max_length=10, unique=True)
    phone_verified = models.BooleanField(default=False)
    cafe_manager = models.BooleanField(default=False)
    order_count = models.IntegerField(default=0)
    # user_id = models.CharField(('user ID'), max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
# def save(self, *args, **kwargs):
#         if not self.user_id:
#             last_user = User.objects.all().order_by('id').last()
#             if last_user and last_user.user_id:
#                 last_user_id = int(last_user.user_id) if last_user.user_id.isdigit() else 0
#                 new_user_id = f"{last_user_id + 1:03d}"
#             else:
#                 new_user_id = "001"
#             self.user_id = new_user_id
        
class menu_item(models.Model):  # Rename the model to MenuItem
    item_id = models.AutoField
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default='')
    desc = models.CharField(max_length=250)
    pic = models.ImageField(upload_to='fimage')
    price = models.CharField(max_length=4, default='0')
    list_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class rating(models.Model):

    name = models.CharField(max_length=30)
    comment = models.CharField(max_length=250)
    r_date = models.DateField()

    def __str__(self):
        return f"{self.name}\'s review"


class order(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=10, default='')
    table = models.CharField(max_length=15, default='take away')
    price = models.CharField(max_length=20, default='0')
    order_time = models.DateTimeField()
    bill_clear = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, default='Online')
    order_status = models.CharField(max_length=20, default='Pending')

    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=True)

     # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    razorpay_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    razorpay_currency = models.CharField(max_length=10, default='INR')
    razorpay_payment_status = models.CharField(max_length=20, default='Pending')
    refund_status = models.CharField(max_length=20, default='No Refund')

    def __str__(self):
        return self.name

    


class bill(models.Model):
    order_items = models.CharField(max_length=5000)
    name = models.CharField(default='', max_length=50)
    bill_total = models.IntegerField()
    phone = models.CharField(max_length=10)
    bill_time = models.DateTimeField()

from django.db import models

class Category(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly adding id field
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    list_order = models.IntegerField()

    def __str__(self):
        return self.name
