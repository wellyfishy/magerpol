from django.db import models
from django.contrib.auth.models import User

class UMKM(models.Model):
    STATUS = [
        ('1', 'Diterima'),
        ('2', 'Ditolak')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_penanggung_jawab = models.CharField(max_length=100, null=True, blank=True)
    nama_umkm = models.CharField(max_length=100, null=True, blank=True)
    deskripsi_umkm = models.TextField(null=True, blank=True)   
    nohp_umkm = models.CharField(max_length=20, null=True, blank=True)
    logo_umkm = models.ImageField(upload_to='logo/', null=True, blank=True)
    proposal_umkm = models.FileField(upload_to='proposal/', null=True, blank=True)
    has_sent = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS, null=True, blank=True)

class Lowongan(models.Model):
    STATUS = [
        ('1', 'Mencari'),
        ('2', 'Tutup'),
    ]
    umkm = models.ForeignKey(UMKM, on_delete=models.CASCADE, null=True, blank=True)
    judul_lowongan = models.CharField(max_length=50, null=True, blank=True)
    deskripsi_lowongan = models.TextField(null=True, blank=True)
    alamat_lowongan = models.CharField(max_length=200, null=True, blank=True)
    status_lowongan = models.CharField(choices=STATUS, null=True, blank=True, default='1')

class Kampus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


