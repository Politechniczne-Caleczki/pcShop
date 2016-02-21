from django.contrib import admin 
from shop.models import Basket, Order, Product, ProductCategory, ShippingInformation , ShoppingList, UserAccount, Bought
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns, include, url


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name')

class ProductAdmin(admin.ModelAdmin):
    fields = ('Name','Manufacturer','Description', 'Category', 'Price', 'Number', 'Image')
    list_display = ('image', 'Name', 'Manufacturer','Category', 'Price', 'Number', 'AddedDate', 'StocksDate')

    def image(self, obj):
        return format_html('<img src="{0}" alt="{1}"  style="width:32px;height:32px;" >'.format(obj.Image.url.replace('/media', ''), obj.Name))

class OrderAdmin(admin.ModelAdmin):
    list_display = ('Product','Number','Date')

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
    fields = ('Date','Shipping_Information', 'orders','complete')  
    readonly_fields= ('Shipping_Information','orders', 'Date','complete')

    class Media:
        js = ('/static/js/shop.js',
        )


    def Shipping_Information(self, obj):
        return  '<a href="%s">%s</a></br>' % ( obj.ShippingInformation.url(), obj.ShippingInformation)     

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



    Shipping_Information.allow_tags = True
    orders.allow_tags = True
    complete.allow_tags = True 


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(ShippingInformation)

admin.site.register(ShoppingList)
admin.site.register(UserAccount)
admin.site.register(Bought, BoughtAdmin)
