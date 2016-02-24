from django import forms



class ShippingInformationForm(forms.Form):
    Name            = forms.CharField(label = 'Your name', max_length = 64, min_length = 2)
    Surname         = forms.CharField(label = 'Your surname', max_length = 64,min_length = 2)
    Address         = forms.CharField(label = 'Your address', max_length = 64,min_length = 2)
    City            = forms.CharField(label = 'Your City', max_length = 64, min_length = 2)
    Country         = forms.CharField(label = 'Your Country', max_length = 64, min_length = 2)


class AddToBasketForm(forms.Form):
    Count           =  forms.IntegerField(min_value= 1)
    Product         =  forms.IntegerField(widget=forms.HiddenInput(), min_value = 1)

class BuyForm(forms.Form):
    ShippingInformation  = forms.IntegerField()
