from myapp import views
from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from django.views.generic import TemplateView, ListView

from django.views.decorators.cache import cache_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path('cart/api/', views.cart_api, name='cart_api'),
    # path('cart/remove/', views.cart_remove_view, name='cart_remove'),
    path('myapp/',include('myapp.urls'))

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
