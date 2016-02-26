from django.shortcuts import render
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from shop.forms import ShippingInformationForm , AddToBasketForm, BuyForm
from shop.models import ShippingInformation , UserAccount, ProductCategory, Product, Order , Bought, Completed, CompletedList
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table , TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import math
cm = 2.54


pdfmetrics.registerFont(TTFont('DejaMono', 'DejaVuSansMono.ttf'))

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
    categories_list =list(ProductCategory.objects.raw("SELECT `shop_productcategory`.`id`, `shop_productcategory`.`Name` FROM `shop_productcategory`"))
    error = []
    category = []
    search = ""   
    max = 100000
    min = 0


    if 'category' in request.GET: 
        if request.GET['category'] != '':       
            category.append(request.GET['category'])
    else:
        for c in categories_list:
            category.append(c.id) 
    
    if 'search' in request.POST:
        search = request.POST['search'] 

    if 'min' in request.POST:
        min = int(request.POST['min'] )

    if 'max' in request.POST:
        max =  int(request.POST['max'] )

    if max < min:
        t = max
        max = min  
        min = t

    Product.objects.filter(Category__id__in = [1,2], Name__contains = "jakis", Price__lte = min, Price__gte = min)

    
    products_list = list(Product.objects.raw("""SELECT `shop_product`.`id`, `shop_product`.`Name`, `shop_product`.`Manufacturer`,
 `shop_product`.`Description`, `shop_product`.`Price`, `shop_product`.`Number`, `shop_product`.`Category_id`, `shop_product`.`Image`, `shop_product`.`URL`,
 `shop_product`.`AddedDate`, `shop_product`.`StocksDate` FROM `shop_product` WHERE (`shop_product`.`Name` LIKE %s AND `shop_product`.`Price` <= %s
AND `shop_product`.`Category_id` IN %s AND `shop_product`.`Price` >= %s)""", ['%'+search+'%',max, category, min]))

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
    content = render(request, 'productList.html', {'min': min, 'max':max, 'search':search, 'categories_list': categories_list, 'products_list': products_list.page(page), 'page_list': page_list})
            
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

            orders = bought.order_set.all()
             
            is_set = True    

            number = []   
                 
            for order in orders:
                if order.Product.Number >= order.Number:
                    number.append(order.Product.Number - order.Number)
                else:
                    is_set = False

            if is_set:
                index = 0
                for order in orders:
                    order.Product.Number = number[index]
                    if number[index] == 0:
                         order.Product.StocksDate = timezone.now()     

                    order.Product.save()
                    index = index +1
                       
                    

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
        #complete = userAccount.CompletedList.completed_set.get(id = com_id)
        complete=   list(ShoppingList.objects.raw("""SELECT `shop_shoppinglist`.`id`, `shop_completed`.`shoppinglist_ptr_id`, `shop_completed`.`Date`,
                                 `shop_completed`.`CompletedList_id` FROM `shop_completed` INNER JOIN 
                                  `shop_shoppinglist` ON (`shop_completed`.`shoppinglist_ptr_id` = `shop_shoppinglist`.`id`) 
                                  WHERE (`shop_completed`.`CompletedList_id` = %d AND `shop_completed`.`shoppinglist_ptr_id` = %s)""", [userAccount.CompletedList.id, com_id]))

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
        userAccount,_ = UserAccount.objects.get_or_create(User = request.user) 
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


def getfile(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="raport.pdf"' 

    elements = []

    doc = SimpleDocTemplate(response, rightMargin=0, leftMargin=1, topMargin=2 * cm, bottomMargin=0)

    data=[]
    table_tyle = []

    index = 0
    for o in Order.objects.raw("""SELECT o.`id`, p.`Name`, o.`Number`, o.`Date`, s.`Name` as n , s.`City` , s.`Surname`, s.`Address`, s.`Country`
                                 FROM `shop_order` o INNER JOIN `shop_product` p ON ( o.`Product_id` = p.`id`)
                                 INNER JOIN `shop_bought` b ON ( o.`Container_id` = b.`basket_ptr_id`)
                                 INNER JOIN `shop_shippinginformation` s ON ( b.`ShippingInformation_id` = s.`id`)
                                 WHERE o.`Container_id` IN (SELECT U0.`basket_ptr_id` FROM `shop_bought` U0 INNER JOIN
                                 `shop_shoppinglist` U1 ON (U0.`ShoppingList_id` = U1.`id`) INNER JOIN `shop_useraccount`
                                  U2 ON (U1.`id` = U2.`ShoppingList_id`) WHERE NOT (U2.`id` IS NULL))"""):
        table_tyle.append(('TEXTCOLOR',(0,index),(2,index),colors.green))
        table_tyle.append(('BACKGROUND',(0,index),(2,index),colors.beige))
        data.append(('Product','Number','Date'))
        index = index+ 1
        table_tyle.append(('BACKGROUND',(0,index),(2,index),colors.azure))
        data.append((o.Name, o.Number,o.Date.strftime("%d/%m/%Y %H:%M:%S")))       
        index = index+ 1
        table_tyle.append(('TEXTCOLOR',(0,index),(0,index),colors.green))
        table_tyle.append(('BACKGROUND',(0,index),(0,index),colors.beige))
        index = index+ 1
        table_tyle.append(('BACKGROUND',(0,index),(4,index),colors.azure))
        data.append(('Address:',))
        data.append((o.n,o.Surname, o.City, o.Address, o.Country))
        index = index+ 1

    
    table = Table(data, colWidths=100, rowHeights=20)
    table.setStyle(TableStyle(table_tyle))
    elements.append(table)

    doc.build(elements) 
    return response
    
