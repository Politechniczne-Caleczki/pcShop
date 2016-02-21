from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout,authenticate, login
from shop.models import UserAccount


def index(request):  
    return redirect('Shop');


def _login(request):    
    if request.method == 'GET':
        if 'redirect' in request.GET:
            return  render(request, 'login.html', {'redirect': request.GET['redirect']}) 
        else:
            return  render(request, 'login.html') 
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
            return render(request, 'login.html', {'error': error}) 

def _logout(request):
    if  request.user.is_authenticated():      
        logout(request)    
    return redirect('Shop')
    
        