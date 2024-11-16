from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from account.models import User


@login_required
def home(request):
    
    return render(request, "home.html", {
        "users": User.objects.all()
    })


