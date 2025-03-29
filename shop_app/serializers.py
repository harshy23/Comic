from rest_framework import serializers  
from .models import Product , Cart ,Cart_item
from django.contrib.auth import get_user_model

class ProductSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Product  
        fields = ["id", "name", "slug", "image", "description", "Category", "price"]

class DescriptionSerializer(serializers.ModelSerializer):
    similar_products = serializers.SerializerMethodField()#this means that this field doesnt get originate from "product" model , it will be gerenetred from method(function) inside class
    class Meta:  
        model = Product  
        fields = ["id", "name", "slug", "image", "description", "Category", "price","similar_products"]

    def get_similar_products(self,product):

        products = Product.objects.filter(Category=product.Category).exclude(id=product.id)
        serializer =  ProductSerializer(products, many=True)
        return serializer.data


class DataCartSerializer(serializers.ModelSerializer):
    number_of_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "number_of_items"]

    def get_number_of_items(self, cart):
        number_of_items = sum([item.quantity for item in cart.items.all()])
        return number_of_items
class CartitemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    # cart_id = CartSerializer(read_only = True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart_item
        # fields =["id","cart_id","product","quantity"]
        fields =["id","product","quantity","total"]
    def get_total(self,cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total

class CartSerializer(serializers.ModelSerializer):
    items = CartitemSerializer(read_only=True,many=True)
    number_of_prod = DataCartSerializer(read_only =True)
    sum_total =serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields =["id","sum_total","items","number_of_prod","cart_code","user","creted_on" ,"updtaed_on"]
    def get_sum_total(self,cart):
        sum_total =sum([item.quantity *item.product.price for item in cart.items.all()])
        return sum_total
    
class Newcartitemserializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()
    product= ProductSerializer(read_only = True)
    class Meta:
        model = Cart_item
        fields=["id","product","quantity","order_id","order_date"]

    def get_order_id(self,cart_item):
        cart_no = cart_item.cart_id.cart_code
        return cart_no

    def get_order_date(self,cart_item):
        date =cart_item.cart_id.creted_on
        return date


class Userserializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields =["id","city","state","address","phone","username","first_name","last_name","email","city","state","address","items" ]

    def get_items(self,user):
        cart_items = Cart_item.objects.filter(cart_id__user = user,cart_id__pay = True)[:10]
        serialised_item = Newcartitemserializer(cart_items,many = True)
        return  serialised_item.data





