from django.shortcuts import render,HttpResponse
from django.contrib import messages
from users.models import UserRegistrationModel
from users.algorithms.TMSCode import TMSCalculation
from .algo.diseasCode import PreProcessCode

import numpy as np
import matplotlib
#matplotlib.use("Agg")
def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        elif usrid == 'Admin' and pswd == 'Admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.success(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})


def AdminHome(request):
    return render(request, 'admins/AdminHome.html')


def ViewRegisteredUsers(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/RegisteredUsers.html', {'data': data})


def AdminActivaUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/RegisteredUsers.html', {'data': data})

def AdminTMS(request):
    obj = TMSCalculation()

    status = obj.startProcess()
    tmsResult = set(status)
    print("Status is ", tmsResult)
    return render(request, "admins/AdminViewTMSResults.html", {"tms": tmsResult})

def AdminConfusionMetrics(request):
    obj = PreProcessCode()
    result = obj.startProcess()
    print("Result is ",result)
    return render(request,"admins/AdminFinalResults.html",result)