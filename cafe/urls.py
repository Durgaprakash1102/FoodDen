from django.contrib import admin
from django.urls import path, include
from cafe import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('', views.index, name='index'),
    path('menu', views.menu, name='menu'),
    path('delete_dish/<int:item_id>/', views.delete_dish, name='delete_dish'),
    path('offers', views.offers, name='offers'),
    path('reviews', views.reviews, name='reviews'),
    path('profile', views.profile, name='profile'),
    path('categories/<int:category_id>/', views.category_items, name='category_items'),

    path('category/', views.category, name='category'),
      path('menu/', views.menu, name='menu'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
    path('item/<int:item_id>/', views.item_details, name='item_details'),
    path('manage_menu/', views.manage_menu, name='manage_menu'),
    path('all_orders', views.all_orders, name='all_orders'),
    path('manage_menu', views.manage_menu, name='manage_menu'),
    path('cart', views.cart, name='cart'),
    # path('checkout', views.checkout, name='checkout'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('payment', views.payment, name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('cash_on_delivery/', views.cash_on_delivery, name='cash_on_delivery'),
    path('login', views.Login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.Logout, name='logout'),
    path('generate_bill', views.generate_bill, name='generate_bill'),
    path('view_bills', views.view_bills, name='view_bills'),
    path('footer', views.footer, name='footer'), 
    path('contactus/', views.contact, name='contactus'),
    path('aboutus/', views.about, name='aboutus'),
    path('gallery/', views.gallery, name='gallery'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
                          
