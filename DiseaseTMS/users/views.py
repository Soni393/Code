from django.shortcuts import render,HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from .algorithms.DiseaseInsights import IdentifyDiseaseInsights
from .algorithms.ViewUserData import GetCleanedData
from .algorithms.UserDataMultinomialNB import DiseaseDiagnosis
from .algorithms.TMSCode import TMSCalculation
from django.conf import settings
import pandas as pd

import matplotlib
#matplotlib.use("Agg")
# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})
def UserHome(request):

    return render(request, 'users/UserHome.html', {})

def UserDiseasPredictions(request):
    obj = IdentifyDiseaseInsights()
    predict,scre = obj.preProcess()
    return render(request,"users/ViewPredictionResults.html",{"predict":predict,"score":scre})

def UserViewData(request):
    obj = GetCleanedData()
    data = obj.viewCleanedData()
    data = data.to_html
    return render(request,"users/ViewCleandedData.html",{"data":data})

def UserViewDataMultinomialNB(request):
    obj = DiseaseDiagnosis()
    score_NB, score_prob, score_NB_dict, score_Prob_dict = obj.startNBProcess()
    return render(request , "users/ViewUsersNbData.html",{'score_NB':score_NB, 'score_prob':score_prob, 'score_NB_dict':score_NB_dict, 'score_Prob_dict':score_Prob_dict})

def UserViewTMSResults(request):
    status =[]
    obj = TMSCalculation()
    status.clear()
    status = obj.startProcess()
    tmsResult = set(status)
    print("Status is ",tmsResult)
    return render(request,"users/UserViewTMSResults.html",{"tms":tmsResult})