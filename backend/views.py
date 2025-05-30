from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse

def loginUMKM(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        # membuat login kampus menjadi satu dengan UMKM
        if user is not None:
            login(request, user)
            if UMKM.objects.filter(user=user).exists():
                return redirect('dashboard-umkm') 
            elif Kampus.objects.filter(user=user).exists():
                return redirect('dashboard-kampus')
        else:
            messages.error(request, "Username atau password salah.")
            return redirect('login-umkm')
    
    return render(request, 'umkm/auth/login.html')

def registerUMKM(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Password tidak sama.")
            return redirect('register-umkm')
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah ada.")
            return redirect('register-umkm')
        else:
            user = User.objects.create(
                username=username,
                password=make_password(password1)
            )
            new_umkm = UMKM.objects.create(user=user)
            messages.success(request, "Registrasi sukses. Sekarang kamu bisa log in.")
            return redirect('login-umkm')
    
    return render(request, 'umkm/auth/register.html')

def logoutfunc(request):    
    if UMKM.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('login-umkm')

def dashboardUMKM(request):
    umkm = UMKM.objects.get(user=request.user)
    all_kategoris = Kategori.objects.all()
    all_lowongans = Lowongan.objects.filter(umkm=umkm).order_by('-pk')

    if request.method == 'POST':
        if request.POST.get('submit_type') == 'validasi_umkm':
            nama = request.POST.get('nama').strip().upper()
            nohp = request.POST.get('nohp').strip()
            nama_umkm = request.POST.get('nama_umkm').strip().upper()
            deskripsi_umkm = request.POST.get('deskripsi')
            file = request.FILES.get('file')
            logo = request.FILES.get('logo')

            umkm.nama_penanggung_jawab = nama
            umkm.nama_umkm = nama_umkm
            umkm.deskripsi_umkm = deskripsi_umkm
            umkm.nohp_umkm = nohp
            umkm.proposal_umkm = file
            umkm.logo_umkm = logo
            umkm.has_sent = True
            umkm.save()

            return redirect('dashboard-umkm')
        
        elif request.POST.get('submit_type') == 'tambah_lowongan':
            judul_lowongan = request.POST.get('judul_lowongan').strip().upper()
            deskripsi_lowongan = request.POST.get('deskripsi_lowongan')
            alamat_lowongan = request.POST.get('alamat_lowongan').strip()
            kategoris = request.POST.getlist('kategori')
            lamaran_dibuka = request.POST.get('lamaran_dibuka')
            lamaran_ditutup = request.POST.get('lamaran_ditutup')

            new_lowongan = Lowongan.objects.create(umkm=umkm, judul_lowongan=judul_lowongan, deskripsi_lowongan=deskripsi_lowongan, alamat_lowongan=alamat_lowongan, lamaran_dibuka=lamaran_dibuka, lamaran_ditutup=lamaran_ditutup)

            for kategori in kategoris:
                kategori = Kategori.objects.filter(pk=kategori).first()
                new_detail_kategori = DetailKategori.objects.create(kategori=kategori, lowongan=new_lowongan)

            messages.success(request, 'Sukses membuat lowongan baru!')
            return redirect('dashboard-umkm')

    context = {
        'on': 'utama',
        'umkm': umkm,
        'all_kategoris': all_kategoris,
        'all_lowongans': all_lowongans,
    }
    return render(request, 'umkm/dashboard/dashboard.html', context)

def dashboardKampus(request):
    kampus = Kampus.objects.get(user=request.user)
    all_umkms = UMKM.objects.all().order_by('-pk')
    all_pending_umkms_count = UMKM.objects.filter(status=None).count()
    all_declined_umkms_count = UMKM.objects.filter(status='2').count()
    all_approved_umkms_count = UMKM.objects.filter(status='1').count()
    # dont worry! django orm is efficient enough to filter all of these without a single sweat! :D

    context = {
        'on': 'utama',
        'kampus': kampus,
        'all_umkms': all_umkms,
        'all_pending_umkms_count': all_pending_umkms_count,
        'all_declined_umkms_count': all_declined_umkms_count,
        'all_approved_umkms_count': all_approved_umkms_count,
    }
    return render(request, 'admin/dashboard/dashboard.html', context)

def umkmApprove(request, umkm_pk):
    umkm = get_object_or_404(UMKM, pk=umkm_pk)
    umkm.status = '1'
    umkm.save()
    messages.success(request, f'Sukses menerima UMKM {umkm.nama_umkm}!')
    return redirect('dashboard-kampus')

def umkmDecline(request, umkm_pk):
    umkm = get_object_or_404(UMKM, pk=umkm_pk)
    umkm.status = '2'
    umkm.save()
    messages.success(request, f'Sukses menolak UMKM {umkm.nama_umkm}!')
    return redirect('dashboard-kampus')

def view_umkm_file(request, umkm_pk):
    umkm = get_object_or_404(UMKM, pk=umkm_pk)
    return FileResponse(umkm.proposal_umkm.open(), content_type='application/octet-stream')