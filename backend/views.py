from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse, JsonResponse
import openpyxl
import openai
from openai import OpenAI
import fitz
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
import os

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_API_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
def summarize_text(text):
    payload = {"inputs": text[:1000]}  # batasi 1000 karakter
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        res = response.json()
        if isinstance(res, list) and "summary_text" in res[0]:
            return res[0]["summary_text"]
        else:
            return "Ringkasan gagal dibuat (format response tidak dikenali)"
    else:
        return f"Ringkasan gagal: {response.status_code} {response.text}"
    
def calculate_score(summary):
    keywords = [
        'pengalaman', 'pengalaman kerja', 'projek', 'project',
        'keahlian', 'skill', 'kemampuan', 'sertifikat', 'sertifikasi',
        'organisasi', 'magang', 'internship', 'penghargaan', 'prestasi'
    ]

    summary_lower = summary.lower()
    score = 2 
    matched_keywords = []

    for kw in keywords:
        if kw in summary_lower:
            score += 1.5
            matched_keywords.append(kw)

    length = len(summary)
    if length > 300:
        score += 3
    elif length > 150:
        score += 2
    elif length > 80:
        score += 1

    score = round(min(score, 10), 1)
    return score

def loginUMKM(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

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

def loginMahasiswa(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if Mahasiswa.objects.filter(user=user).exists():
                return redirect('dashboard-mahasiswa')
            else:
                return redirect('login-mahasiswa')
        else:
            messages.error(request, "Username atau password salah.")
            return redirect('login-mahasiswa')
    
    return render(request, 'mahasiswa/auth/login.html')

def dashboardMhs(request):
    mahasiswa = Mahasiswa.objects.get(user=request.user)
    all_lowongans = Lowongan.objects.filter().order_by('-pk')
    for lowongan in all_lowongans:
        lowongan.kategori = DetailKategori.objects.filter(lowongan=lowongan)

    context = {
        'on': 'home',
        'mahasiswa': mahasiswa,
        'all_lowongans': all_lowongans,
    }
    return render(request, 'mahasiswa/dashboard/dashboard.html', context)

def editProfileMhs(request):
    mahasiswa = Mahasiswa.objects.get(user=request.user)

    if request.method == 'POST':
        if request.POST.get('submit_type') == 'profile-save':
            mahasiswa.nama_mahasiswa = request.POST.get('nama').strip().upper()
            mahasiswa.nohp_mahasiswa = request.POST.get('nohp').strip()
            mahasiswa.user.email = request.POST.get('email').strip()
            mahasiswa.profile = request.FILES.get('image')
            mahasiswa.save()
            mahasiswa.user.save()
        elif request.POST.get('submit_type') == 'cv':
            mahasiswa.cv = request.FILES.get('cv')
            mahasiswa.save()

        return redirect('edit-profile-mahasiswa')

    context = {
        'on': 'edit-profil',
        'mahasiswa': mahasiswa,
    }
    return render(request, 'mahasiswa/dashboard/edit-profile.html', context)

def mahasiswaAjukan(request, lowongan_pk):
    lowongan = Lowongan.objects.get(pk=lowongan_pk)
    mahasiswa = Mahasiswa.objects.get(user=request.user)
    mahasiswa.lowongan = lowongan
    mahasiswa.status = '2'
    mahasiswa.save()
    return redirect('dashboard-mahasiswa')

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
    elif Kampus.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('login-umkm')
    elif Mahasiswa.objects.filter(user=request.user).exists():
        logout(request)
        return redirect('login-mahasiswa')

def dashboardUMKM(request):
    umkm = UMKM.objects.get(user=request.user)
    all_kategoris = Kategori.objects.all()
    all_lowongans = Lowongan.objects.filter(umkm=umkm).order_by('-pk')
    for lowongan in all_lowongans:
        lowongan.selected_kategoris = DetailKategori.objects.filter(lowongan=lowongan)
        lowongan.kategoris = []
        for kategori in lowongan.selected_kategoris:
            lowongan.kategoris.append(kategori.kategori)

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
            mulai_magang = request.POST.get('mulai_magang')
            selesai_magang = request.POST.get('selesai_magang')

            new_lowongan = Lowongan.objects.create(umkm=umkm, judul_lowongan=judul_lowongan, deskripsi_lowongan=deskripsi_lowongan, alamat_lowongan=alamat_lowongan, lamaran_dibuka=lamaran_dibuka, lamaran_ditutup=lamaran_ditutup, mulai_magang=mulai_magang, selesai_magang=selesai_magang)

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

def baca_cv_dan_proses(cv_path):
    text = ""
    with fitz.open(cv_path) as doc:
        for page in doc:
            text += page.get_text()
    summary = summarize_text(text)
    score = calculate_score(summary)
    return summary, score

def proses_cv_mahasiswa(request):
    lowongan_pk = request.GET.get('lowongan_id')
    if not lowongan_pk:
        return JsonResponse({'error': 'Missing lowongan_pk'}, status=400)

    try:
        lowongan = Lowongan.objects.get(pk=lowongan_pk)
        all_mahasiswas = Mahasiswa.objects.filter(lowongan=lowongan)
    except Lowongan.DoesNotExist:
        return JsonResponse({'error': 'Lowongan not found'}, status=404)

    hasil_ai = []

    for mhs in all_mahasiswas:
        if mhs.cv and os.path.exists(mhs.cv.path):
            try:
                summary, score = baca_cv_dan_proses(mhs.cv.path)
            except Exception as e:
                summary = f"Gagal membaca CV: {str(e)}"
                score = 0
        else:
            summary = "CV tidak tersedia."
            score = 0

        hasil_ai.append({
            'id': mhs.pk,
            'nama': mhs.nama_mahasiswa,
            'nim': mhs.nim,
            'summary': summary,
            'score': score,
        })

    return JsonResponse({'data': hasil_ai})

def lowonganDetailUMKM(request, lowongan_pk):
    umkm = UMKM.objects.get(user=request.user)
    lowongan = Lowongan.objects.get(pk=lowongan_pk)
    all_mahasiswas = Mahasiswa.objects.filter(lowongan=lowongan)

    # hasil_ai = []
    # for mhs in all_mahasiswas:
    #     if mhs.cv:
    #         try:
    #             summary, score = baca_cv_dan_proses(mhs.cv.path)
    #         except Exception as e:
    #             summary = f"Gagal membaca CV: {str(e)}"
    #             score = 0
    #     else:
    #         summary = "CV tidak tersedia."
    #         score = 0
    #     hasil_ai.append((mhs, summary, score))

    context = {
        'on': 'utama',
        'umkm': umkm,
        'lowongan': lowongan,
        'all_mahasiswas': all_mahasiswas,
        # 'hasil_ai': hasil_ai,
    }
    return render(request, 'umkm/dashboard/lowongan-detail.html', context)




def mahasiswaApprove(request, lowongan_pk, mahasiswa_pk):
    umkm = UMKM.objects.get(user=request.user)
    lowongan = Lowongan.objects.get(pk=lowongan_pk)
    mahasiswa = Mahasiswa.objects.get(pk=mahasiswa_pk)
    
    mahasiswa.status = '3'
    mahasiswa.save()

    return redirect('lowongan-detail', lowongan_pk=lowongan_pk)

def mahasiswaDecline(request, lowongan_pk, mahasiswa_pk):
    umkm = UMKM.objects.get(user=request.user)
    lowongan = Lowongan.objects.get(pk=lowongan_pk)
    mahasiswa = Mahasiswa.objects.get(pk=mahasiswa_pk)

    mahasiswa.status = '1'
    mahasiswa.lowongan = None
    mahasiswa.save()

    return redirect('lowongan-detail', lowongan_pk=lowongan_pk)

def dashboardKampus(request):
    kampus = Kampus.objects.get(user=request.user)
    all_umkms = UMKM.objects.filter(has_sent=True).order_by('-pk')
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

def dashboardKampusMahasiswa(request):
    kampus = Kampus.objects.get(user=request.user)
    all_mahasiswas = Mahasiswa.objects.all()
    all_kategoris = Kategori.objects.all()

    if request.method == 'POST':
        if request.POST.get('submit_type') == 'tambah_mahasiswa_manual':
            nim_mahasiswa = request.POST.get('nim_mahasiswa').strip()
            nama_mahasiswa = request.POST.get('nama_mahasiswa').strip().upper()
            nohp_mahasiswa = request.POST.get('nohp_mahasiswa').strip()
            jurusan = request.POST.get('kategori')  

            if Mahasiswa.objects.filter(nim=nim_mahasiswa).exists():
                messages.error(request, f'Mahasiswa dengan NIM {nim_mahasiswa} sudah ada!')
                return redirect('kampus-mahasiswa')
            else:
                jurusan = Kategori.objects.get(pk=jurusan)
                new_user = User.objects.create_user(username=nim_mahasiswa, password=nim_mahasiswa)
                new_mahasiswa = Mahasiswa.objects.create(user=new_user, nim=nim_mahasiswa, nama_mahasiswa=nama_mahasiswa, nohp_mahasiswa=nohp_mahasiswa, jurusan=jurusan)
                messages.success(request, f'Mahasiswa dengan NIM {nim_mahasiswa} berhasil di tambahkan!')
                return redirect('kampus-mahasiswa')
            
        elif request.POST.get('submit_type') == 'tambah_mahasiswa_excel':
            excel_file = request.FILES.get('excel_file')
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, 'Format file harus .xlsx')
                return redirect('kampus-mahasiswa')

            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                try:
                    nim, nama, kategori_judul = row
                    kategori = Kategori.objects.filter(judul_kategori__icontains=kategori_judul).first()
                    new_mahasiswa = Mahasiswa.objects.create(
                        nim=nim,
                        nama_mahasiswa=nama,
                        jurusan=kategori
                    )
                    new_user = User.objects.create_user(username=nim, password=str(nim))
                    new_mahasiswa.user = new_user
                    new_mahasiswa.save()
                except Exception as e:
                    messages.warning(request, f'Gagal import baris: {row}, error: {e}')
            messages.success(request, 'Excel berhasil diimpor.')
            return redirect('kampus-mahasiswa')
            
    context = {
        'on': 'mahasiswa',
        'all_kategoris': all_kategoris,
        'all_mahasiswas': all_mahasiswas
    }
    return render(request, 'admin/dashboard/mahasiswa.html', context)

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

def view_mahasiswa_cv(request, mhs_pk):
    mahasiswa = get_object_or_404(Mahasiswa, pk=mhs_pk)
    return FileResponse(mahasiswa.cv.open(), content_type='application/octet-stream')

def dashboardMahasiswa(request):
    return render(request, 'mahasiswa/dashboard/dashboard.html')