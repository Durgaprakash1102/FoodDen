from atexit import register
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
from cafe.models import *
from django.core.files.storage import FileSystemStorage
from datetime import date, datetime, timedelta, timezone
import json, ast
from itertools import groupby
from django.utils import timezone

from django.db.models import Sum


User = get_user_model()

def index(request):
   
    return render(request, 'index.html')

def menu(request):
    context = {}

    menu_items = menu_item.objects.all().order_by('list_order')
    items_by_category = {}

    for key, group in groupby(menu_items, key=lambda x: x.category):
        items_by_category[key] = list(group)

    context = {'items_by_category': items_by_category}

    return render(request, 'menu.html', context)


import json

def all_orders(request):
    context = {}
    orders = order.objects.all().order_by('-order_time')
    order_by_table = {}

    for key, group in groupby(orders, key=lambda x: x.table):
        order_by_table[key] = list(group)

    for table, orders in order_by_table.items():
        for ord in orders:
            items_json_str = ord.items_json
            if items_json_str:
                try:
                    ord.items_json = json.loads(items_json_str)
                except json.JSONDecodeError:
                    # Handle the case where JSON is malformed
                    ord.items_json = {}  # or some default value or log the error

    context = {'order_by_table': order_by_table}

    return render(request, 'all_orders.html', context)


def offers(request):
    return render(request, 'offers.html')


def reviews(request):

    if request.method == 'POST':
        fname = request.user.first_name
        lname = request.user.last_name
        cmt = request.POST.get('comment')
        date_today = date.today()

        review = rating(name=fname + ' ' + lname,
                        comment=cmt,
                        r_date=date_today)
        review.save()

    all_reviews = rating.objects.all().order_by('-r_date')
    context = {}
    context['reviews'] = all_reviews

    return render(request, 'reviews.html', context)


def profile(request):
    if request.user.is_anonymous:
        messages.error(request, 'Please Login first!!')
        return redirect('login')
    return render(request, 'profile.html')


def footer(request):
   
    return render(request, 'templates/footer.html')

    

from .models import Category, menu_item  # Import the MenuItem model

def manage_menu(request):
    if request.method == 'POST' and request.FILES.get('img'):
        if request.user.is_anonymous:
            messages.error(request, 'Please Login to continue!')
            return redirect('login')
        if not (request.user.is_superuser or request.user.cafe_manager):
            messages.error(request, 'Only Staff members are allowed!')
            return redirect('menu')
        else:
            name = request.POST.get('name')
            price = request.POST.get('price')
            desc = request.POST.get('desc')
            cat_id = request.POST.get('cat')
            img = request.FILES['img']

            try:
                category = Category.objects.get(id=cat_id)
            except Category.DoesNotExist:
                messages.error(request, 'Invalid category selected!')
                return redirect('manage_menu')

            dish = menu_item(
                name=name,
                price=price,
                desc=desc,
                category=category,
                pic=img,
                list_order=category.list_order
            )
            dish.save()
            messages.success(request, 'Dish added successfully!')
            return redirect('menu')

    categories = Category.objects.all()
    return render(
        request,
        'manage_menu.html',
        {'categories': categories}
    )


def delete_dish(request, item_id):

    dish = get_object_or_404(menu_item, id=item_id)
    if request.user.is_superuser:
        if request.method == 'POST':
            dish.delete()
            messages.success(request, 'Dish removed successfully!')
            return redirect('menu')
    else:
        messages.error(request, 'Only admins are allowed!')
        return redirect('menu')






from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from .models import  User
from .models import order  # Update the import statement


# def cart(request):
#     if request.method == 'POST':
#         if request.user.is_anonymous:
#             name = 'Unknown'
#             phone = 'Unknown'
#             # user_id = None  # Set user_id to None for anonymous users
#         else:
#             name = f"{request.user.first_name} {request.user.last_name}"
#             phone = request.user.phone
#             # user_id = request.user.user_id  # Get the user ID of the logged-in user
#             # print("User ID:", user_id)  # Print the user ID here

#         items_json = request.POST.get('items_json')
#         table_number = request.POST.get('table_value')
#         total = float(request.POST.get('price'))

#         now = datetime.now()
#         now_ist = now + timedelta(hours=5, minutes=30)

#         if table_number == 'null':
#             table_number = 'Take Away'

#         new_order = order(
#             name=name,
#             phone=phone,
#             items_json=items_json,
#             table=table_number,
#             order_time=now_ist,
#             price=total,
#             # user_id=user_id  # Associate the order with the user
#         )
#         new_order.save()

#         request.session['cart_total'] = total

#         if request.user.is_anonymous:
#             messages.success(request, 'Order Placed!! Thanks for ordering. You can sign up to save your information!!')
#             return redirect('/')
#         else:
#             usr = User.objects.get(phone=phone)
#             usr.order_count += 1
#             usr.save()
#             messages.success(request, 'Order Placed!! Thanks for ordering')
#             return redirect('my_orders')

#     return render(request, 'cart.html')

def cart(request):
    if request.method == 'POST':
        if request.user.is_anonymous:
            name = 'Unknown'
            phone = 'Unknown'
        else:
            name = f"{request.user.first_name} {request.user.last_name}"
            phone = request.user.phone
        items_json = request.POST.get('items_json')
        table_number = request.POST.get('table_value')
        total = float(request.POST.get('price'))

        now = datetime.now()
        now_ist = now + timedelta(hours=5, minutes=30)

        if table_number == 'null':
            table_number = 'Take Away'

        new_order = order(
            name=name,
            phone=phone,
            items_json=items_json,
            table=table_number,
            order_time=now_ist,
            price=total,
        )
        new_order.save()

        request.session['cart_total'] = total

        # Return the order ID in the response
        return JsonResponse({'order_id': new_order.order_id})
    
    return render(request, 'cart.html')











from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from itertools import groupby

@login_required
def my_orders(request):
    phone = request.user.phone
    context = {}

    # Get orders for the current user
    orders = order.objects.filter(phone=phone)

    # Dictionary to store orders grouped by table
    order_by_table = {}

    # Group orders by table
    for key, group in groupby(orders, key=lambda x: x.table):
        order_by_table[key] = list(group)

    # Mark orders placed before today as expired and today's orders as recent
    today = timezone.now().date()
    for table, orders in order_by_table.items():
        for ord in orders:
            # Check if the order time is before today
            if ord.order_time.date() < today:
                ord.is_expired = True  # Mark the order as expired
            elif ord.order_time.date() == today:
                ord.is_recent = True  # Mark the order as recent

            # Ensure items_json is not empty or None before attempting to load it
            if ord.items_json:
                try:
                    ord.items_json = json.loads(ord.items_json)
                except json.JSONDecodeError:
                    ord.items_json = {}  # Handle the case where the JSON is invalid
            
        # Sort orders by order time in descending order
        orders.sort(key=lambda x: x.order_time, reverse=True)

    context = {'order_by_table': order_by_table}

    return render(request, 'my_orders.html', context)


def Login(request):
    user_id = None  # Initialize user_id as None
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(phone=phone, password=password)
        
        if user is not None:
            login(request, user)
            # user_id = user.user_id  # Fetch the user_id after authentication
            messages.success(request, 'Logged in successfully!')
            return redirect('profile')

        else:
            messages.error(request, 'Login failed, Invalid Credentials!')
            return redirect('login')
 
    return render(request, 'login.html', {'user_id': user_id}) 

def Logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully !')
    return redirect('login')





def signup(request):
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('number')
        pass_word = request.POST.get('password')
        c_pass_word = request.POST.get('cpassword')
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Mobile number already registered. Please Login to continue.')
            return redirect('login')

        # # Generate user ID dynamically
        # last_user = User.objects.last()
        # if last_user:
        #     last_user_id = int(last_user.user_id) if last_user.user_id.isdigit() else 0
        #     new_user_id = f"{last_user_id + 1:03d}"
        # else:
        #     new_user_id = "001"

        my_user = User.objects.create_user(phone=phone, password=pass_word, first_name=fname, last_name=lname)
        messages.success(request, 'User created successfully!')
        return redirect('login')

    return render(request, 'signup.html')




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import order, bill
from datetime import datetime, timedelta
import json
import ast

# def generate_bill(request):
#     if request.method == 'GET':
#         order_id = request.GET.get('order_id')

#         if not order_id:
#             return HttpResponseBadRequest("Order ID is required")

#         try:
#             order_instance = get_object_or_404(order, order_id=order_id, bill_clear=False)
#         except ValueError:
#             return HttpResponseBadRequest("Invalid Order ID")

#         total_bill = 0
#         now = datetime.now()
#         now_ist = now + timedelta(hours=5, minutes=30)

#         bill_items = []
#         c_name = ''
#         c_phone = ''

#         if order_instance.price.isdigit():  # Check if price is a valid integer
#             total_bill += int(order_instance.price)
#             order_instance.bill_clear = True
#             order_instance.save()

#             bill_items.append({
#                 'order_items': order_instance.items_json,
#             })
#             c_name = order_instance.name
#             c_phone = order_instance.phone

#         order_dict = {}
#         for item in bill_items:
#             for key, value in item.items():
#                 order_items = json.loads(value)
#                 for pr_key, pr_value in order_items.items():
#                     order_dict[pr_value[1].lower()] = [
#                         pr_value[0], (pr_value[2] * pr_value[0])
#                     ]

#         # Create a new bill record
#         new_bill = bill.objects.create(
#             order_items=order_dict,
#             name=c_name,
#             bill_total=total_bill,
#             phone=c_phone,
#             bill_time=now_ist
#         )

#         context = {
#             'order_dict': order_dict,
#             'bill_total': total_bill,
#             'name': c_name,
#             'phone': c_phone,
#             'inv_id': new_bill.id,
#         }
#         return render(request, 'generate_bill.html', context)
#     else:
#         # Handle POST request if needed
#         pass

def generate_bill(request):
    if request.method == 'GET':
        order_id = request.GET.get('order_id')

        if not order_id:
            return HttpResponseBadRequest("Order ID is required")

        # Fetch the order instance with the given ID, ensure bill is not cleared
        order_instance = get_object_or_404(order, order_id=order_id, bill_clear=False)

        try:
            total_bill = float(order_instance.price)
        except ValueError:
            return HttpResponseBadRequest("Invalid price value")

        # Mark the order as cleared and save
        order_instance.bill_clear = True
        order_instance.save()

        bill_items = json.loads(order_instance.items_json)

        order_dict = {}
        for item, details in bill_items.items():
            order_dict[item] = [details[0], details[2] * details[0]]

        now_ist = datetime.now() + timedelta(hours=5, minutes=30)

        # Create a new bill
        new_bill = bill.objects.create(
            order_items=order_dict,
            name=order_instance.name,
            bill_total=total_bill,
            phone=order_instance.phone,
            bill_time=now_ist
        )

        context = {
            'order_dict': order_dict,
            'bill_total': total_bill,
            'name': order_instance.name,
            'phone': order_instance.phone,
            'inv_id': new_bill.id,
        }
        return render(request, 'generate_bill.html', context)
    else:
        return HttpResponseBadRequest("Invalid request method")

def view_bills(request):
    if request.user.is_anonymous:
        messages.error(request, 'You must be an admin user to view this!')
        return redirect('')

    # Get all bill records and order by bill_time in descending order
    all_bills = bill.objects.all().order_by('-bill_time')

    for b in all_bills:
        b.order_items = ast.literal_eval(b.order_items)

    context = {'bills': all_bills}
    return render(request, 'bills.html', context)


def view_bills(request):

    if request.user.is_anonymous:
        messages.error(request, 'You Must be an admin user to view this!')
        return redirect('')

    all_bills = bill.objects.all().order_by('-bill_time')

    for b in all_bills:
        b.order_items = ast.literal_eval(b.order_items)

    context = {'bills': all_bills}

    return render(request, 'bills.html', context)

def category(request):
    categories = Category.objects.all()
    items_by_category = {}

    for category_obj in categories:
        items_by_category[category_obj] = menu_item.objects.filter(category=category_obj)

    if request.method == 'POST' and request.FILES.get('image'):
        name = request.POST.get('name')
        description = request.POST.get('description')
        order = request.POST.get('order')
        image = request.FILES['image']

        if Category.objects.filter(name=name).exists():
            messages.error(request, 'Category already exists!')
            return redirect('category')

        category_obj = Category(name=name, description=description, image=image, list_order=order)
        category_obj.save()
        messages.success(request, 'Category added successfully!')
        return redirect('manage_menu')
    categories = Category.objects.all()

    return render(request, 'category.html', {'categories': categories})

from django import template
from .models import menu_item 

register = template.Library()



@register.filter(name='get_category_items')
def category_items(category):
    # Assuming menu_item has 'price' and 'image' fields along with other necessary fields
    return menu_item.objects.filter(category=category).values('name', 'price', 'image')



@register.filter(name='my_custom_filter')
def my_custom_filter(value):
    # Filter logic here
    return modified_value


def menu(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'messages': messages.get_messages(request)
    }
    return render(request, 'menu.html', context)


def item_details(request, item_id):
    item = get_object_or_404(menu_item, id=item_id)
    return render(request, 'item_details.html', {'item': item})

def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = menu_item.objects.filter(category=category)
    return render(request, 'category_items.html', {'category': category, 'items': items})



from django.shortcuts import redirect, render


def contact(request):
    return render(request, 'contactus.html')

from django.shortcuts import redirect, render

def about(request):
    return render(request, 'aboutus.html')

def gallery(request):
    return render(request,'gallery.html')


# def payment(request):
#     return render(request, 'payment.html')

import razorpay
from django.conf import settings
from .models import order

# def payment(request):
#     razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
    
#     # Razorpay order details
#     order_amount = request.session.get('cart_total', 0) * 100  # amount in paise (50000 = 500 INR)
#     order_currency = 'INR'
#     order_receipt = 'order_rcptid_11'
    
#     # Create order
#     razorpay_order = razorpay_client.order.create({
#         'amount': order_amount,
#         'currency': order_currency,
#         'receipt': order_receipt
#     })
    
#     context = {
#         'razorpay_order_id': razorpay_order['id'],
#         'razorpay_merchant_key': settings.RAZORPAY_TEST_KEY_ID,
#         'amount': order_amount,
#         'currency': order_currency
#     }
    
#     return render(request, 'payment.html', context)

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import order

def payment(request):
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
    
    # Razorpay order details
    order_amount = request.session.get('cart_total', 0) * 100  # amount in paise (50000 = 500 INR)
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'
    
    # Create order
    razorpay_order = razorpay_client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt
    })
    
    # Store the Razorpay order ID in the session or any other persistent storage
    request.session['razorpay_order_id'] = razorpay_order['id']
    
    context = {
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_TEST_KEY_ID,
        'amount': order_amount / 100,
        'currency': order_currency
    }
    
    return render(request, 'payment.html', context)
import logging

def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        orderid = request.POST.get('order_id')

        # Log received parameters for debugging
        logging.debug(f"Received payment_id: {payment_id}")
        logging.debug(f"Received razorpay_order_id: {razorpay_order_id}")
        logging.debug(f"Received razorpay_signature: {razorpay_signature}")

        # Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
        
        # Signature verification
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            # Verifying the signature for payment authenticity
            razorpay_client.utility.verify_payment_signature(params_dict)
            logging.debug("Signature verification successful")

            # Fetch the order and update its status
            orderdata = order.objects.get(order_id=orderid)
            orderdata.razorpay_payment_id = payment_id
            orderdata.razorpay_order_id = razorpay_order_id
            orderdata.razorpay_signature = razorpay_signature
            orderdata.order_status = 'Success'
            orderdata.razorpay_payment_status = 'Paid'
            orderdata.save()
            
            return JsonResponse({'status': 'success', 'message': 'Payment and order updated successfully.'})
        
        except razorpay.errors.SignatureVerificationError as e:
            logging.error(f"Signature verification failed: {str(e)}")
            return JsonResponse({'status': 'failure', 'message': f'Signature verification failed: {str(e)}'})
        except order.DoesNotExist:
            return JsonResponse({'status': 'failure', 'message': 'Order not found.'})
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'failure', 'message': 'An error occurred: ' + str(e)})
    
    return JsonResponse({'status': 'failure', 'message': 'Invalid request.'})


from django.shortcuts import redirect
from .models import order


def cash_on_delivery(request):
    order_id = request.GET.get('order_id')

    # If no order_id, return an error message
    if not order_id:
        return render(request, 'error.html', {'message': 'Order ID not provided.'})

    # Fetch the order using order_id
    try:
        order_data = get_object_or_404(order, order_id=order_id)
    except order.DoesNotExist:
        return render(request, 'error.html', {'message': 'Order not found.'})

    # Assuming `cart_total` is stored in the session
    cart_total = request.session.get('cart_total', 0)

    # Update the order details
    order_data.payment_method = 'Cash on Delivery'
    order_data.order_status = 'Pending'
    order_data.total_amount = cart_total
    order_data.save()

    # Render the cash_on_delivery.html template
    return render(request, 'cash_on_delivery.html', {'order': order_data})
    