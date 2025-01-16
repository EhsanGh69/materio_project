from django.shortcuts import render

def custom_404(request, exception=None):
    return render(request, 'panel/404.html', status=404)