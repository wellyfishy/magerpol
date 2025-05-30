from django.urls import path, include
from .views import *

urlpatterns = [
    path('login-umkm', loginUMKM, name='login-umkm'),
    path('register-umkm', registerUMKM, name='register-umkm'),
    path('umkm-dashboard', dashboardUMKM, name='dashboard-umkm'),
]
