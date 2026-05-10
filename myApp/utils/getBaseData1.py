from myApp.models import *

def getAllProducts():
    return  Products.objects.all()