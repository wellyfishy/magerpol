from django.shortcuts import render, redirect

def loginUMKM(request):
    if request.method == 'POST':
        return redirect('dashboard-umkm')
    
    return render(request, 'umkm/auth/login.html')

def registerUMKM(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        return redirect('login-umkm')
    
    return render(request, 'umkm/auth/register.html')

def dashboardUMKM(request):
    return render(request, 'umkm/dashboard.html')