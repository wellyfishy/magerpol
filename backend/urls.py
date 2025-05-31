from django.urls import path, include
from .views import *

urlpatterns = [
    path('', loginMahasiswa, name='login-mahasiswa'),
    path('mahasiswa', dashboardMhs, name='dashboard-mahasiswa'),
    path('mahasiswa/<int:lowongan_pk>/ajukan', mahasiswaAjukan, name='mahasiswa-ajukan'),
    path('mahasiswa/edit-profil', editProfileMhs, name='edit-profile-mahasiswa'),
    path('login-umkm', loginUMKM, name='login-umkm'),
    path('register-umkm', registerUMKM, name='register-umkm'),
    path('umkm-dashboard', dashboardUMKM, name='dashboard-umkm'),
    path('lowongan-detail/<int:lowongan_pk>', lowonganDetailUMKM, name='lowongan-detail'),
    path('lowongan-detail/<int:lowongan_pk>/detail/<int:mahasiswa_pk>/approve', mahasiswaApprove, name='mahasiswa-approve'),
    path('lowongan-detail/<int:lowongan_pk>/detail/<int:mahasiswa_pk>/decline', mahasiswaDecline, name='mahasiswa-decline'),
    path('kampus-dashboard', dashboardKampus, name='dashboard-kampus'),
    path('kampus-mahasiswa', dashboardKampusMahasiswa, name='kampus-mahasiswa'),
    path('kampus-mahasiswa/<int:mhs_pk>/cv', view_mahasiswa_cv, name='view-mahasiswa-cv'),
    path('kampus-dashboard/<int:umkm_pk>/approve', umkmApprove, name='umkm-approve'),
    path('kampus-dashboard/<int:umkm_pk>/decline', umkmDecline, name='umkm-decline'),
    path('kampus-dashboard/<int:umkm_pk>/file', view_umkm_file, name='view-umkm-file'),
    path('logout', logoutfunc, name='logout'),
    path('ajax/proses-semua-cv/', proses_cv_mahasiswa, name='proses_semua_cv'),
]
