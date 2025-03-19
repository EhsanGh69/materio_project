from django.shortcuts import render

def custom_404(request, exception=None):
    return render(request, 'panel/404.html', status=404)

def custom_403(request, exception):
    return render(request, 'panel/403.html', status=403)

def custom_500(request):
    return render(request, 'panel/500.html', status=500)