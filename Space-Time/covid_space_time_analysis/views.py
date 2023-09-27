
from django.http import HttpResponse
from django.shortcuts import render
from . import dashboard

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required



def hello(requests):
    return render(requests,'plotly/dashboard.html')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_url')
    else:
        form = UserCreationForm()
    return render(request,'authentication/register.html',{'form':form})