from django.urls import path
from . import views

urlpatterns = [
    path("products" , views.products,name="products"),
    path("Prod_detail/<slug:slug>" , views.Prod_detail , name="Prod_detail"),
     path("add_cart/" , views.add_cart, name="add_item"),
     path("product_in_cart" , views.product_in_cart, name="add_itemproduct_in_cart"),
     path("num_of_items" ,views.num_of_items ,name="num_of_items"),
     path("cartall",views.cartpage,name="cartpage"),
     path("updatequantity/" , views.updatequantity,name="updatequantity"),
     path("delte_item/",views.delte_item,name="delte_item"),
     path("get_username",views.get_username,name="get_username"),
     path("get_userinfo",views.get_userinfo,name="get_userinfo"),
     path("new_user/",views.new_user,name="new_user"),
     path("initiate_payment/",views.initiate_payment,name="initiate_payment"),
     path("payment_callback/" , views.payment_callback , name="payment_callback"),
     path("initiate_paypal_payment/",views.initiate_paypal_payment,name="initiate_paypal_payment"),
     path("paypal_payment_callback/" ,views.paypal_payment_callback,name='paypal_payment_callback'),

]

# fetching product in frontend from backend sothses is the endpoint =  http://127.0.0.1:8000/products