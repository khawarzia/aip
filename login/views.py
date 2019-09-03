from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from .models import infor
from datetime import date,timedelta
from django.core.mail import EmailMessage
import random

def login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    template = 'login.html'
    if request.method == 'POST':
        a = authenticate(username=request.POST['username'],password=request.POST['password'])
        if a is not None:
            auth.login(request,a)
            return redirect('/confirm')
    return render(request,template)

def logout(request):
    auth.logout(request)
    return redirect('/')

def signup(request):
    template = 'signup.html'
    if request.user.is_authenticated:
        return redirect('/dashboard')
    if request.method == 'POST':
        un = request.POST['username']
        objs = User.objects.all()
        for i in objs:
            if i.username == un:
                return redirect('/loggin')
        pack = request.POST['package']
        a = User.objects.create_user(
            un,
            request.POST['email'],
            request.POST['password']
        )
        a.first_name = request.POST['first_name']
        a.last_name = request.POST['last_name']
        a.save()
        auth.login(request,a)
        linkaccount(request,a,pack)
        if infor.objects.get(user=a).started == True:
            return redirect('/dashboard')
        return redirect('/checkout')
    return render(request,template)

def confirm(request):
    template = 'confirmation.html'
    objs = infor.objects.all()
    context = {}
    for i in objs:
        if i.user == request.user and i.started == False:
            context['message'] = 'a'
        if i.user == request.user and i.started == True:
            context['message'] = 'b'
    return render(request,template,context)

def changepass(request):
    template = 'dataentry.html'
    if request.method == 'POST':
        a = User.objects.get(username = request.user.username)
        a.set_password(request.POST['new_password'])
        a.save()
        return redirect('/confirm')
    return render(request,template)

def forgot(request):
    template = 'dataentry.html'
    form = forgotpassword1(request.POST)
    if request.method == 'POST':
        a = request.POST['username']
        userobjs = User.objects.all()
        lis = []
        for i in userobjs:
            lis.append(i.username)
        if a not in lis:
            return redirect('/main')
        b = User.objects.get(username = a)
        c = infor.objects.get(user = a)
        mail = EmailMessage(
            'Forgot password'
            'Your password change key is : ' + c.passwordkey,
            to = [b.email]
        )
        form = forgotpassword2(request.POST)
        if request.method == 'POST':
            d = request.POST['key_from_mail']
            e = request.POST['new_password']
            if d == c.passwordkey:
                c.passwordkey = randomizer()
                c.save()
                b.set_password(e)
                b.save()
                return redirect('/loggin')
            context = {'form':form}
            return render(request,template,context)
    context = {'form':form}
    return render(request,template,context)

def linkaccount(request,a,pack):
    objs = infor.objects.all()
    for i in objs:
        if i.package == pack and i.user == None:
            i.passwordkey = randomizer()
            i.user = a
            if pack == 'Starter   Free':
                i.price = 0
                i.started = True
                i.start = date.today()
                b = timedelta(days = 90)
                i.end = i.start + b
                i.save()    
            if pack == 'Gold   $29.99':
                i.price = 29.99
            if pack == 'Platinum   $299.99':
                i.price = 299.99
            i.save()
            b = infor(
                package = pack
            )
            b.save()
            break
    return 

def randomizer():
    a = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']
    c = ''
    for i in range(0,9):
        c = c + a[random.randint(0,len(a)-1)]
    return c