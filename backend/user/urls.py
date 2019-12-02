from django.urls import path
from user import views


app_name = 'user'
urlpatterns = [
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('change_password/', views.ChangePasswordView.as_view(),
         name='change_password'),
    path('password_recovery/', views.PasswordRecoveryView.as_view(),
         name='password_recovery'),
]
