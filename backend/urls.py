from django.urls import path, include
from .views import *

urlpatterns = [
    path('login-umkm', loginUMKM, name='login-umkm'),
    path('register-umkm', registerUMKM, name='register-umkm'),
    path('umkm-dashboard', dashboardUMKM, name='dashboard-umkm'),
    path('kampus-dashboard', dashboardKampus, name='dashboard-kampus'),
    path('kampus-dashboard/<int:umkm_pk>/approve', umkmApprove, name='umkm-approve'),
    path('kampus-dashboard/<int:umkm_pk>/decline', umkmDecline, name='umkm-decline'),
    path('kampus-dashboard/<int:umkm_pk>/file', view_umkm_file, name='view-umkm-file'),
    path('logout', logoutfunc, name='logout')
]
