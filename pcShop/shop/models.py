from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 


class ProductCategory(models.Model):
    Name = models.CharField(max_length = 64) 

    def __unicode__(self):   
        return self.Name    

    class Meta:
        verbose_name_plural = 'Categories - list of all category products'

class Product(models.Model):
    Name = models.CharField(max_length = 64, help_text = 'Name of the product.', default= '')
    Manufacturer = models.CharField(max_length = 64, help_text = 'Manufacturer of the product.', default = '')
    Description = models.TextField(help_text= 'Description of the product.', default = '')
    Price = models.FloatField(default = 1, help_text= 'Price per item.')
    Number = models.IntegerField(default = 0, help_text= 'In Stock')
    Category = models.ForeignKey(ProductCategory)   
    Image = models.ImageField(upload_to='image/product/', default = 'image/product/default.jpg')
    URL = models.URLField(null = True, help_text='Address of the manufacturer.')
    AddedDate = models.DateTimeField(default = timezone.now)
    StocksDate = models.DateTimeField(blank = True, null = True, help_text = 'When was the last time was available' )
    
    def __unicode__(self):   
        return self.Name     

    def url(self):
        return '/admin/shop/product/%d/' % self.id   

    class Meta:
        verbose_name_plural = 'Products - list of all products'
        

class Order(models.Model):
    Product         = models.ForeignKey(Product,null =False, blank=False)
    Number          = models.IntegerField(default = 1)
    Date            = models.DateTimeField(default =timezone.now)
    Container       = models.ForeignKey('Basket', null = False, blank = False)

    def __unicode__(self):   
        return  'Order {0} at {1}.'.format(self.Product.Name, self.Number) 

    def url(self):
        return '/admin/shop/order/%d/' % self.id   

    def is_available(self):
        if self.Product.Number >= self.Number:
            return True
        return False

    class Meta:
        verbose_name_plural = 'Orders - list of orders for a single product'




class Basket(models.Model):   
    def __unicode__(self):
        return  'Basket'

    def is_basket(self):
        return True;

    def url(self):
        return '/admin/shop/bought/%d/' % self.id



class Bought(Basket):
    Date                = models.DateTimeField(default =timezone.now)
    ShippingInformation = models.ForeignKey('ShippingInformation', blank = False, null = False)  
    ShoppingList        = models.ForeignKey('ShoppingList', blank = False, null = False)

    def __unicode__(self): 
        return 'Bougth of: %s, item count: %d' % (self.Date.strftime("%d/%m/%Y %H:%M:%S"), self.order_set.count())

    def __str__(self):
        return self.__unicode__()  

    def is_available(self):
        for order in self.order_set.all():
            if order.is_available() == False:
                return False
        return True

    def url(self):
        return '/admin/shop/bought/%d/' % self.id 

    class Meta:
        verbose_name_plural = 'Bought - list of orders transferred to realization'
    


class ShoppingList(models.Model):
    def __unicode__(self):
        return  'Shopping list'

    class Meta:
        verbose_name_plural = 'Shopping List - a list of purchases for a single user'


class Completed(ShoppingList): 
    Date                = models.DateTimeField(default =timezone.now)
    CompletedList        = models.ForeignKey('CompletedList', blank = False, null = False)
    def __unicode__(self):
        return  'Completed order of: %s'  % (self.Date.strftime("%d/%m/%Y %H:%M:%S"))



class CompletedList(models.Model):
    def __unicode__(self):
        return  'Completed list order of'

    class Meta:
        verbose_name_plural = 'Completed - the list of completed transactions'
    
 
class UserAccount(models.Model):
    User                    = models.OneToOneField(User, on_delete=models.CASCADE, blank = False, null = False)
    Basket                  = models.OneToOneField(Basket,on_delete=models.CASCADE, blank = False, null = False)
    ShoppingList            = models.OneToOneField(ShoppingList,on_delete=models.CASCADE, blank = False, null = False)
    CompletedList           = models.OneToOneField(CompletedList,on_delete=models.CASCADE, blank = False, null = False)

    def save(self, *args, **kwargs):
        if not self.pk:
            _id = 1
            if UserAccount.objects.count()>0:
                _id = UserAccount.objects.latest('id').id+1 
            self.Basket, _          = Basket.objects.get_or_create(id= _id)
            self.ShoppingList, _    = ShoppingList.objects.get_or_create(id= _id)
            self.CompletedList, _   = CompletedList.objects.get_or_create(id= _id)
        else:
            self.Basket, _          = Basket.objects.get_or_create(id= self.id)
            self.ShoppingList, _    = ShoppingList.objects.get_or_create(id= self.id)
            self.CompletedList, _   = CompletedList.objects.get_or_create(id= self.id)  

        return super(UserAccount, self).save(*args, **kwargs)

    def __unicode__(self):  
        return self.User.username


class ShippingInformation(models.Model):
    UserAccounts = models.ForeignKey(UserAccount)
    Name = models.CharField(max_length = 64)
    Surname = models.CharField(max_length = 64)
    Address =  models.CharField(max_length = 128, help_text= 'Street, house number, postcode.')
    City = models.CharField(max_length = 64)
    Country = models.CharField(max_length = 64)
    
    def __unicode__(self):  
        return '%s %s %s %s %s' % (self.Name, self.Surname, self.Address, self.City, self.Country)


    def url(self):
        return '/admin/shop/shippinginformation/%d/' % self.id


    class Meta:
        verbose_name_plural = 'Delivery addresses'

