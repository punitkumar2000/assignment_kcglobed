from . import views
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls.static import static

urlpatterns = [
    path('my_admin/', admin.site.urls, name='my_admin'),
    re_path(r'^admins$', views.admins_api),
    re_path(r'^admins/$', views.admins_api),
    re_path(r'^signup$', views.signupapi),
    re_path(r'^signup/$', views.signupapi),
    re_path(r'^login$', views.loginapi),
    re_path(r'^login/$', views.loginapi),
    re_path(r'^logout$', views.logoutapi),
    re_path(r'^logout/$', views.logoutapi),

    re_path(r'^search', views.searchApi),
    re_path(r'^search/$', views.searchApi),
    re_path(r'^get_product_details$', views.productsApi_admin),
    re_path(r'^get_product_details/$', views.productsApi_admin),
    re_path(r'^add_product$', views.productsApi_admin),
    re_path(r'^add_product/$', views.productsApi_admin),
    re_path(r'^update_product$', views.productsApi_admin),
    re_path(r'^update_product/$', views.productsApi_admin),
    re_path(r'^delete_product$', views.productsApi_admin),
    re_path(r'^delete_product/$', views.productsApi_admin),

    re_path(r'^get_cart_products$', views.cartApi),
    re_path(r'^get_cart_products/$', views.cartApi),
    re_path(r'^cart_product_add$', views.cartApi),
    re_path(r'^cart_product_add/$', views.cartApi),
    re_path(r'^update_cart$', views.cartApi),
    re_path(r'^update_cart$/$', views.cartApi),
    re_path(r'^clear_cart$', views.cartApi),
    re_path(r'^clear_cart/$', views.cartApi),

    re_path(r'^track_all_order_details$', views.buyorderApi),
    re_path(r'^track_all_order_details/$', views.buyorderApi),
    re_path(r'^buy_order$', views.buyorderApi),
    re_path(r'^buy_order/$', views.buyorderApi),
    re_path(r'^confirm_order/$', views.buyorderApi),
    re_path(r'^track_order/$', views.trackorderApi),
    re_path(r'^update_order_status$', views.trackorderApi),
    re_path(r'^update_order_status/$', views.trackorderApi)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
