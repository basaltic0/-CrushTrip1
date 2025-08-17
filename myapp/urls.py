from myapp import views
from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, ListView
from django.contrib.auth.views import LogoutView
from .views import generate_itinerary


urlpatterns = [   
    path('index/', views.index, name='index'),#進入首頁    
    # path('gallery_view/', views.gallery_view, name='gallery_view'),#進入首頁    
    path('register/', views.register_view, name='register'),#註冊頁面
    path('login/', views.login_view, name='login'),#登入頁面
    path('logout/', views.custom_logout, name='logout'),#登出頁面
    path('member/', views.member_view, name='member'),#會員資訊
    path('cart/', views.cart_view, name='cart'),#購物車頁面
    path('cart/add/', views.cart_add_view, name='cart_add'),#API處理
    path('index/add/', views.index_add_view, name='index_add'),#API處理
    path('cart/remove/', views.cart_remove_view, name='cart_remove'),
    path('spots/<str:parent_title>/', views.spots_view, name='spots'),#客製化行程頁面
    path('spot/<str:parent_title>/', views.spot_detail_view, name='spot_detail'),#客製化行程子頁
    path('spots/', views.spots_view, name='spots'),#客製化行程頁面
    path('activate/<uid>/<token>/', views.activate, name='activate'),#信箱驗證
    path('forgot-username/', views.forgot_username_view, name='forgot_username'),#忘記帳號
    path('send-message/', views.send_contact_message, name='send_message'),#首頁傳送訊息
    path("profile/update/", views.update_profile, name="update_profile"),  # 更新會員資料    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),#忘記密碼
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),#密碼更新
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),#密碼確認
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),#密碼完成
    path("generate-itinerary/", generate_itinerary), #設定GPT路由
    path('send-itinerary/', views.send_itinerary, name='send_itinerary'),#打包寄送
    path('cr/', views.cr,name = "cr"),#主要城市
    path('cr3/', views.cr3,name = "cr3"),#熱門景點
    path('cons/<str:parent_title>/', views.cons_detail, name='cons_detail'),#子頁內容
    path('debug-avatar/', views.debug_avatar, name='debug_avatar'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)#存放大頭貼
