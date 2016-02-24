from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout,authenticate, login
from shop.models import UserAccount
from shop.forms import RegisterForm
from django.contrib.auth.models import User


def index(request):  
    return redirect('Shop');


def _login(request):  
    if request.user.is_authenticated():
        return redirect('Shop');
  
    if request.method == 'GET':
        if 'redirect' in request.GET:
            return  render(request, 'login.html', {'redirect': request.GET['redirect']}) 
        else:
            return  render(request, 'login.html', {'register': RegisterForm()}) 
    else:
        if 'username' not in request.POST:
            error = 'Not specified username.';
            return render(request, 'login.html', {'error': error}) 

        if 'password' not in request.POST:
            error = 'Not specified password.'
            return render(request, 'login.html', {'error': error})           


        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            
            UserAccount.objects.get_or_create(User = user)           

            if user.is_active:  
                if 'redirect' in request.POST:
                    if request.POST['redirect'] is not None:
                        return redirect(request.POST['redirect'])

                return redirect('Shop')
            else:
                return redirect('Active')
        else:
            error = 'Bad username or password.'
            return render(request, 'login.html', {'error': error, 'register': RegisterForm()}) 

def _register(request):
    if request.user.is_authenticated():
        return redirect('Shop');

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid:

            _username = request.POST['username']
            _password = request.POST['password']
            _email = request.POST['email'] 

            if User.objects.filter(email= _email).exists():
                return render(request, 'login.html', {'error': ['Account with this address already exists.',], 'register': RegisterForm()})   

            if User.objects.filter(username = _username).exists():
                return render(request, 'login.html', {'error': ['Account with that name already exists.',], 'register': RegisterForm()}) 

            user = User.objects.create_user(_username,_email,_password)
            user.is_active = False
            user.save()  
            return render(request, 'login.html', {'message': ['Account created correctly, please login.',], 'register': RegisterForm()})      
        else:
            return render(request, 'login.html', {'error': ['Complete all fields correctly.',], 'register': RegisterForm()})    

    return redirect('Login')
    

def _logout(request):
    if  request.user.is_authenticated():      
        logout(request)    
    return redirect('Shop')
    
        