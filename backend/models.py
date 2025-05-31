from django.db import models
from django.contrib.auth.models import User
from datetime import date

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
    lamaran_dibuka = models.DateField(null=True, blank=True)
    lamaran_ditutup = models.DateField(null=True, blank=True)
    is_publish = models.BooleanField(default=True)
    mulai_magang = models.DateField(null=True, blank=True)
    selesai_magang = models.DateField(null=True, blank=True)

    def get_status(self):
        today = date.today()

        if self.status_lowongan == '1':
            if self.lamaran_dibuka and today < self.lamaran_dibuka:
                return "Mendatang"
            elif self.lamaran_dibuka and self.lamaran_ditutup and self.lamaran_dibuka <= today <= self.lamaran_ditutup:
                return "Mencari"
            else:
                return "Tutup"
        else:
            return "Tutup"

class Kategori(models.Model):
    judul_kategori = models.CharField(max_length=50, null=True, blank=True)

class DetailKategori(models.Model):
    kategori = models.ForeignKey(Kategori, null=True, blank=True, on_delete=models.CASCADE)
    lowongan = models.ForeignKey(Lowongan, null=True, blank=True, on_delete=models.CASCADE, related_name='details')

class Kampus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

class Mahasiswa(models.Model):
    STATUS = [
        ('1', 'Nganggur'),
        ('2', 'Mengajukan'),
        ('3', 'Sedang Magang')
    ]
    profile = models.FileField(upload_to='profile/', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nim = models.CharField(unique=True, null=True, blank=True, max_length=50)
    nama_mahasiswa = models.CharField(max_length=50, null=True, blank=True)
    nohp_mahasiswa = models.CharField(null=True, blank=True, max_length=20)
    lowongan = models.ForeignKey(Lowongan, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, null=True, blank=True, choices=STATUS, default='1')
    jurusan = models.ForeignKey(Kategori, null=True, blank=True, on_delete=models.SET_NULL)
    cv = models.FileField(upload_to='cv/', null=True, blank=True)
    surat_pengajuan = models.FileField(upload_to='pengajuan/', null=True, blank=True)

    def __str__(self):
        return f'{self.nim}'
    


