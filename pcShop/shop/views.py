from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from shop.forms import ShippingInformationForm , AddToBasketForm, BuyForm
from shop.models import ShippingInformation , UserAccount, ProductCategory, Product, Order , Bought, Completed, CompletedList
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required



def active(request):
    if request.user.is_authenticated() == False:
        return redirect('Login');

    if request.user.is_active:
        return redirect('Shop');

    else:
        if request.method == 'GET':
            return render(request,'active.html', {'form': ShippingInformationForm(request.POST)})
        else:
            form = ShippingInformationForm(request.POST)
            
            if form.is_valid():
                userAccount = UserAccount.objects.get(User = request.user)            

                shipInfo = ShippingInformation(**form.cleaned_data)
                shipInfo.UserAccounts = userAccount
                shipInfo.save()
                request.user.is_active = True 
                request.user.save()                              
                
                return redirect('Shop')
            else:
                return render(request,'active.html', {'form': ShippingInformationForm(request.POST)})          
            
    

def shop(request):
    categories_list = ProductCategory.objects.all()     
    error = []
  
    if 'category' in request.GET:
        category = None
        try:
            _id = int(request.GET['category'])
            category = ProductCategory.objects.get(id = _id)
        except ValueError:
            error.append('Bad index category.')           
    
        if category is not None:
            products_list = Product.objects.filter( Category= category)
        else:
            products_list = Product.objects.all()
    else:
        products_list = Product.objects.all()    

    products_list = Paginator(products_list,20)   
    page = 1

    if 'page' in request.GET:
        try:
            if products_list.num_pages >= int(request.GET['page']) and int(request.GET['page']) >0 :
                page =  int(request.GET['page'])
        except ValueError:
            error.append('Bad index page.')      

    
    page_list = []
    page_list.append(1)

    for index in range(page-5, page+5):
        if index >1 and index < products_list.num_pages:
            page_list.append(index)       

    if  products_list.num_pages != 1:
        page_list.append(products_list.num_pages)
    content = render(request, 'productList.html', { 'categories_list': categories_list, 'products_list': products_list.page(page), 'page_list': page_list})
            
    return render(request,'index.html', {'error_list': error, 'content': content.content} )


def product(request, product_id):
    try:
        prod = Product.objects.get(id = product_id)

        count = '1'

        if 'count' in request.GET:
            count = request.GET['count']
        
        form = AddToBasketForm(initial={'Product': product_id, 'Count': count})      
        
        content = render(request,'product.html', {'product': prod, 'form': form})
        return render(request, 'index.html', { 'content': content.content})
    except ObjectDoesNotExist:    
        return HttpResponseNotFound("Product not found")
        

def basket(request):
    if request.user.is_authenticated() == False:
        if request.method == 'POST':        
            form = AddToBasketForm(request.POST)
            if form.is_valid():                 
                return redirect('/login/?redirect=/shop/product/%s/?count=%s&' % (form.cleaned_data['Product'], form.cleaned_data['Count']))              
        return redirect('Login')
    if request.user.is_active == False:
        return redirect('Active')
    else: 
        error = []
        userAccount = UserAccount.objects.get(User = request.user)  
        if request.method == 'POST':        
            form = AddToBasketForm(request.POST)
            if form.is_valid():                
                try:
                    product = Product.objects.get(id = form.cleaned_data['Product'])  
                    order = Order(Product = product, Number = form.cleaned_data['Count'],  Container = userAccount.Basket)
                    order.save()    
                    return redirect('Basket')
                except  ObjectDoesNotExist:
                    return HttpResponseNotFound("Product not found")   
            else:
                error.append('Something went wrong')     

        content = render(request, 'basket.html',{'order_list': userAccount.Basket.order_set.all(), 'shinf_list': userAccount.shippinginformation_set.all() }) 
        
        return render(request,'index.html', {'error_list': error, 'content': content.content})
                           

def buy(request):
    if request.user.is_authenticated() == False:
        return redirect('Login')

    if request.user.is_active == False:
        return redirect('Active')
    else:
        if request.method == 'POST':    
            form = BuyForm(request.POST)
            if form.is_valid():
                try:
                    userAccount = UserAccount.objects.get(User = request.user) 
  
                    if request.POST['button'] == 'Buy':  

                        shinf = userAccount.shippinginformation_set.get(id= int(form.cleaned_data['ShippingInformation']))
                        shopList = userAccount.ShoppingList 

                        bought = Bought(ShippingInformation= shinf, ShoppingList = userAccount.ShoppingList )
                        bought.save()   


                        for _id in request.POST.getlist('Orders'):                      
                            order = userAccount.Basket.order_set.get(id = int(_id))
                            order.Container =  bought
                            order.save()     

                        if bought.order_set.count() == 0:
                            bought.delete()  
        
                    if request.POST['button'] == 'Delete':
                        for _id in request.POST.getlist('Orders'):                      
                            order = userAccount.Basket.order_set.get(id = int(_id))
                            order.delete()  
                            
                except  ObjectDoesNotExist:
                    return HttpResponseNotFound('Object not found') 
            else:
                return HttpResponse("Something went wrong")                    
                                
    
    return redirect('Basket')
        
def bought(request):
    if request.user.is_authenticated() == False:
        return redirect('Login')  
    if request.user.is_active == False:
        return redirect('Active')
    
    userAccount = UserAccount.objects.get(User = request.user)    

    if request.method == 'POST':
        if 'Bought' in request.POST:
            userAccount.ShoppingList.bought_set.get(id = request.POST['Bought']).delete()
            return redirect('Bought')

    bought_list = userAccount.ShoppingList.bought_set.all()      
  
    content = render(request, 'boughtList.html', { 'bought_list': bought_list})
    
    return render(request,'index.html', {'content': content.content})

def boughtdetail(request, bought_id):
    if request.user.is_authenticated() == False:
        return redirect('Login')
    if request.user.is_active == False:
        return redirect('Active')
    
    error_list = []

    try:
        userAccount = UserAccount.objects.get(User = request.user)  
        bought = userAccount.ShoppingList.bought_set.get(id = bought_id)

        if request.method == 'POST':
            if 'Count' in request.POST and 'Order' in request.POST:
                order = bought.order_set.get(id= request.POST['Order'])
                order.Number = int(request.POST['Count'])
                order.save()

                return redirect('BoughtDetail', bought_id = bought_id)
            
            if 'ShippingInformation' in request.POST:
                ship = userAccount.shippinginformation_set.get(id = request.POST['ShippingInformation'])
                bought.ShippingInformation = ship
                bought.save()
                return redirect('BoughtDetail', bought_id = bought_id)

        content = render(request, 'bought.html', {'bought':bought, 'order_list': bought.order_set.all(), 'shinf_list': userAccount.shippinginformation_set.filter(~Q(id = bought.ShippingInformation.id))})
        return render(request,'index.html', {'error_list': error_list, 'content': content.content })
    except  ObjectDoesNotExist:
        error_list.append('Object not found')

    return render(request,'index.html', {'error_list': error_list})


def completed(request):
    if request.user.is_authenticated() == False:
        return redirect('Login')
    if request.user.is_active == False:
        return redirect('Active')

    userAccount = UserAccount.objects.get(User = request.user)    
    completed_list = userAccount.CompletedList.completed_set.all()         

    content = render(request, 'completedList.html', {'completed_list': completed_list})

    return render(request,'index.html', {'content': content.content })

@staff_member_required
def boughtComplet(request):
    if request.user.is_authenticated() == False:
        return HttpResponse('/admin/')

    if 'bought_id' in request.POST:
        try:
            bought = Bought.objects.get(id= request.POST['bought_id'])
            userAccount = bought.ShoppingList.useraccount
            com = Completed(CompletedList = userAccount.CompletedList)
            com.save()

            bought.ShoppingList = com     
            bought.save()      
            
        except  ObjectDoesNotExist:
            return HttpResponse('')
            


    return HttpResponse('/admin/shop/bought/')

    

def completeddetail(request, com_id):
    if request.user.is_authenticated() == False:
        return redirect('Login') 
    if request.user.is_active == False:
        return redirect('Active')    

    error_list = []
    userAccount = UserAccount.objects.get(User = request.user)   
    try:
        complete = userAccount.CompletedList.completed_set.get(id = com_id)

        content =render(request, 'completed.html', {'completed':complete})
        return render(request,'index.html', {'error_list': error_list, 'content': content.content })
    except  ObjectDoesNotExist:                                                                                                                                                                       
        error_list.append('Object not found')

    return render(request,'index.html', {'error_list': error_list})


def options(request):
    if request.user.is_authenticated() == False:
        return redirect('Login')   

    if request.user.is_active == False:
        return redirect('Active') 

    error_list = []
    content = None
    form= ShippingInformationForm()
 
    try:
        userAccount = UserAccount.objects.get(User = request.user)              

        if request.method == 'POST': 

            if 'shinf_if' in request.POST:
                userAccount.shippinginformation_set.get(id = request.POST['shinf_if']).delete()                                                                             
                return redirect('Options') 
            else:
                form = ShippingInformationForm(request.POST)
                if form.is_valid():
                    shipInfo = ShippingInformation(**form.cleaned_data)
                    shipInfo.UserAccounts = userAccount
                    shipInfo.save()
                    return redirect('Options') 
                else:
                    error_list.append('Complete all fields correctly')            

    except  ObjectDoesNotExist:                                                                                                                                                                       
        error_list.append('Error')

    shinf_list = userAccount.shippinginformation_set.all() 
    content = render(request, 'options.html', { 'shinf_list': shinf_list , 'form': form})

    return render(request,'index.html', {'error_list': error_list, 'content': content.content})