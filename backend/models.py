from django.db import models
from django.contrib.auth.models import User

class UMKM(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_umkm = models.CharField(max_length=100, null=True, blank=True)
    deskripsi_umkm = models.TextField(null=True, blank=True)   
    nohp_umkm = models.CharField(max_length=20, null=True, blank=True)
    logo_umkm = models.ImageField(upload_to='logo/', null=True, blank=True)

class Lowongan(models.Model):
    STATUS = [
        ('1', 'Mencari'),
        ('2', 'Tutup'),
    ]
    umkm = models.ForeignKey(UMKM, on_delete=models.CASCADE, null=True, blank=True)
    deskripsi_lowongan = models.TextField(null=True, blank=True)
    alamat_lowongan = models.CharField(max_length=200, null=True, blank=True)
    status_lowongan = models.CharField(choices=STATUS, null=True, blank=True)


