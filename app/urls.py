from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm

urlpatterns = [

    # ---------------- HOME ----------------
    path('', views.ProductView.as_view(), name="home"),

    # ---------------- PRODUCT ----------------
    path('product-detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # ---------------- CART ----------------
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart, name='pluscart'),
    path('minuscart/', views.minus_cart, name='minuscart'),
    path('removecart/', views.remove_cart, name='removecart'),

    # ---------------- USER ----------------
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),

    # ---------------- PARKING ----------------
    path('basement/', views.basement, name='basement'),
    path('basement/<str:data>/', views.basement, name='basementdata'),

    path('open/', views.open_parking, name='open_parking'),
    path('open/<str:data>/', views.open_parking, name='open_parking_data'),

    # ---------------- AUTH ----------------
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='app/login.html',
        authentication_form=LoginForm
    ), name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('registration/', views.RegisterUserView.as_view(), name='customerregistration'),

    # ---------------- PASSWORD ----------------
    path('passwordchange/', auth_views.PasswordChangeView.as_view(
        template_name='app/passwordchange.html',
        form_class=MyPasswordChangeForm,
        success_url='/passwordchangedone/'
    ), name='passwordchange'),

    path('passwordchangedone/', auth_views.PasswordChangeView.as_view(
        template_name='app/passwordchangedone.html'
    ), name='passwordchangedone'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='app/password_reset.html',
        form_class=MyPasswordResetForm
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='app/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='app/password_reset_confirm.html',
        form_class=MySetPasswordForm
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='app/password_reset_complete.html'
    ), name='password_reset_complete'),

    # ---------------- CHECKOUT ----------------
    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/', views.payment_done, name='paymentdone'),

    # ---------------- ADMIN BOOKING ----------------
    path('admin-confirm-booking/', views.admin_confirm_booking, name='admin-confirm-booking'),

    # ---------------- GATE ----------------
    path('gate/', views.gate_entry, name='gate_entry'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# from django.urls import path
# from app import views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views
# from .forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
# # from .views import booking_page, book_slot

# urlpatterns = [
#     path('', views.ProductView.as_view(), name="home"),

#     path('product-detail/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

#     path('add-to-cart/', views.add_to_cart, name='add-to-cart'),

#     path('cart/', views.show_cart, name='showcart'),

#     path('pluscart/', views.plus_cart, name='pluscart'),

#     path('minuscart/', views.minus_cart, name='minuscart'),

#     path('removecart/', views.remove_cart, name='removecart'),

#     # path('buy/', views.buy_now, name='buy-now'),

#     path('buy/<int:product_id>/', views.buy_now, name='buy-now'),

#     path('profile/', views.ProfileView.as_view(), name='profile'),

#     path('address/', views.address, name='address'),

#     path('orders/', views.orders, name='orders'),

#     path('mobile/', views.mobile, name='mobile'),

#     path('mobile/<slug:data>', views.mobile, name='mobiledata'),

# # adding new links
#     path('tennis/', views.tennis, name='tennis'),

#     path('tennis/<slug:data>', views.tennis, name='tennisdata'),
        
#     path('cricket/', views.cricket, name='cricket'),

#     path('cricket/<slug:data>', views.cricket, name='cricketdata'),

#     path('kits/', views.kits, name='kits'),

#     path('kits/<slug:data>', views.kits, name='kitsdata'),

#     path('refreshment/', views.refreshment, name='refreshment'),

#     path('refreshment/<slug:data>', views.refreshment , name='refreshmentdata'),

#     path('accounts/login/', auth_views.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),

#     # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
#     path('logout/', views.logout_view, name='logout'),  # Custom logout view

#     path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name='passwordchange'),

#     path('passwordchangedone/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),

#     path('password-reset/', auth_views.PasswordResetView.as_view(template_name= 'app/password_reset.html', form_class=MyPasswordResetForm), name='password_reset'),

#     path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name= 'app/password_reset_done.html'), name='password_reset_done'),

#     path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name= 'app/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),

#     path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name= 'app/password_reset_complete.html'), name='password_reset_complete'),

#     path('checkout/', views.checkout, name='checkout'),

#     path('paymentdone/', views.payment_done, name='paymentdone'),

#     path('registration/', views.RegisterUserView.as_view(), name='customerregistration'),

#     # path(
#     # 'admin-confirm/slot/<int:slot_id>/',
#     # views.admin_confirm_slot,
#     # name='admin-confirm'),

#     path('admin-confirm-booking/', views.admin_confirm_booking, name='admin-confirm-booking'),

#     path('api/slots/<int:product_id>/', views.slot_status_api, name='slot_status_api'),

#     path('gate/', views.gate_entry, name='gate_entry'),

# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
