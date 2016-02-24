from django.contrib import admin 
from shop.models import Basket, Order, Product, ProductCategory, ShippingInformation , ShoppingList, UserAccount, Bought, CompletedList
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns, include, url
from django.db.models import Q


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name')

class ProductAdmin(admin.ModelAdmin):
    search_fields   =('Name','Manufacturer','Description', 'Category__Name', 'Price', 'Number')
    fields = ('Name','Manufacturer','Description', 'Category', 'Price', 'Number', 'Image')
    list_display = ('image', 'Name', 'Manufacturer','Category', 'Price', 'Number', 'AddedDate', 'StocksDate')
    list_filter= ('Category',)

    def image(self, obj):
        return format_html('<img src="{0}" alt="{1}"  style="width:32px;height:32px;" >'.format(obj.Image.url.replace('/media', ''), obj.Name))

class OrderAdmin(admin.ModelAdmin):
    list_display = ('product','Number','Date','order')
    readonly_fields =('product','Number','Date')
    fields =  ('product','Number','Date')

    def product(self, obj):
        return  '<a href="%s">%s</a></br>' % (obj.Product.url(), obj.Product)

    def order(self, obj):
        return  '<a href="%s">%s</a></br>' % (obj.Container.url(), obj.Container) 

    product.allow_tags = True
    order.allow_tags = True

    def get_queryset(self, request):     
        b = Bought.objects.filter(~Q( ShoppingList__useraccount=None))
        return Order.objects.filter(Q(Container__id__in = b))



class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'orders_number')   
    fields = ('user','orders') 
    readonly_fields= ('user','orders',)

    def orders_number(self, obj):
        return obj.order_set.count()

    def orders(self,obj): 
        odp = ''

        for o in   obj.order_set.all():
            odp += '<a href="%s">%s</a></br>' % ( o.url(), o)     

        return odp  

    def user(self, obj):
        return obj.useraccount.User
    
  

    orders.allow_tags = True


class BoughtAdmin(admin.ModelAdmin):
    list_display     = ('User','Order_Count', 'Date','is_available')
    fields           = ('Date','Shipping_Information', 'orders','complete')  
    readonly_fields  = ('Shipping_Information','orders', 'Date','complete')

    class Media:
        js = ('/static/js/shop.js',
        )


    def Shipping_Information(self, obj):
        return  '<a href="%s">%s</a></br>' % ( obj.ShippingInformation.url(), obj.ShippingInformation)   

    def User(slef, obj):
        return obj.ShoppingList.useraccount;  

    def Order_Count(self, obj):
        return obj.order_set.all().count()

    def orders(self,obj): 
        odp = ''

        for o in   obj.order_set.all():   
            if o.is_available():     
                odp += '<a href="%s">%s</a></br>' % ( o.url(),  o)     
            else:
                odp += '<a href="%s" style="color:red" >%s     -IS NOT AVAILABLE!!!</a></br>' % ( o.url(),  o)    
        return odp  
    

    def complete(self, obj):    
        if obj.is_available(): 
            return '<button type="button" onclick="Complete(%d);">Complete</button>' % obj.id
        else:
            return '<button type="button" onclick="Complete(%d);" disabled="disabled">Complete</button>' % obj.id 

    def get_queryset(self, request):
        return super(BoughtAdmin, self).get_queryset(request).filter(~Q( ShoppingList__useraccount=None))

    



    Shipping_Information.allow_tags = True
    orders.allow_tags = True
    complete.allow_tags = True 


class ShippingInformationAdmin(admin.ModelAdmin):  
    list_display = ('id','user', '__unicode__')
    search_fields = ['Name', 'Surname', 'City','Address','Country']
    readonly_fields = ('user', 'name', 'surname', 'city', 'country')

    fieldsets = (
        (None, {
            'fields':  ('user', 'name', 'surname', 'city', 'country')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('UserAccounts','Name','Surname','City','Country'),
        }),
    )


    def user(self, obj):
        return obj.UserAccounts

    def name(self,obj):
        return obj.Name

    def surname(self, obj):
        return obj.Surname

    def city(self, obj):
        return obj.City

    def country(self, obj):
        return obj.Country
        

class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user',)


    def user(self, obj):
        return obj.useraccount

    def get_queryset(self, request):
        return super(ShoppingListAdmin, self).get_queryset(request).filter( ~Q(useraccount = None))



admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingInformation, ShippingInformationAdmin)
admin.site.register(CompletedList)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(UserAccount)
admin.site.register(Bought, BoughtAdmin)
