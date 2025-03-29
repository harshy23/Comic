from django.shortcuts import render

from .models import Product , Cart , Cart_item,Transaction
from .serializers import ProductSerializer , DescriptionSerializer , CartSerializer , CartitemSerializer , DataCartSerializer ,Userserializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from django.conf import settings
import requests
import uuid
import paypalrestsdk


# BASE_URL = "http://localhost:5173"
BASE_URL = settings.REACT_BASE_URL

# Create your views here.
@api_view(["GET"])
def products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products , many=True)
    return Response(serializer.data)

@api_view(["GET"])
def Prod_detail(request , slug):
    product =Product.objects.filter(slug =slug)
    serializer = DescriptionSerializer(product , many = True)
    return Response(serializer.data)

@api_view(["POST"])
def add_cart(request):
    try:
        cart_code = request.data.get("cart_code")
        product_id = request.data.get("product_id")
    
        cart , created = Cart.objects.get_or_create(cart_code = cart_code)
        product = Product.objects.get(id = product_id)
    
        cart_item , created = Cart_item.objects.get_or_create(cart_id = cart ,product = product)
        cart_item.quantity = 1
        cart_item.save()
    
        # serializer_cart = CartSerializer(cart) 
        serilaizer_cartitem = CartitemSerializer(cart_item)
    
        return Response({"Cart_item":serilaizer_cartitem.data ,"message":"Cartitem created succesfully"}, status=201)
    except Exception as e:
        return Response({"error":str(e)}, status = 400)

@api_view(["GET"])
def product_in_cart(request):
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")

    cart = Cart.objects.get(cart_code=cart_code)  
    product = Product.objects.get(id=product_id)

    product_exists_in_cart = Cart_item.objects.filter(cart_id=cart, product=product).exists()

    return Response({"product_in_cart":product_exists_in_cart})

@api_view(["GET"])
def num_of_items(request):
    cart_code = request.query_params.get("cart_code")
    cart = Cart.objects.get(cart_code= cart_code ,pay=False)
    serializer =  DataCartSerializer(cart)
    return Response(serializer.data)

@api_view(["GET"])
def cartpage(request):
    cart_code = request.query_params.get("cart_code")
    cart = Cart.objects.get(cart_code= cart_code,pay=False)
    serializer =  CartSerializer(cart) 
    return Response(serializer.data)

@api_view(["PATCH"])
def updatequantity(request):
    try:
        cartitem_id = request.data.get("cartitem_id")
        quantity=request.data.get("quantity")
        quantity = int(quantity)
        cart_item = Cart_item.objects.get(id= cartitem_id)
        cart_item.quantity = quantity
        cart_item.save()
        serilize = CartitemSerializer(cart_item)
        return Response({"data":serilize.data , "message":"your Cart has been updated"})
    except Excpetion as e:
        return Response({'error':str(e)} ,status = 400)

@api_view(["POST"])
def delte_item(request):
    item_id = request.data.get("item_id")
    cart_item = Cart_item.objects.get(id= item_id)
    cart_item.delete()

    return Response(status = status.HTTP_204_NO_CONTENT)

    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_username(request):
    user = request.user
    return Response({"username":user.username})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_userinfo(request):
    user =request.user
    serialize = Userserializer(user)
    return Response(serialize.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    if request.user:
        try:
            tx_ref = str(uuid.uuid4())
            cart_code=request.data.get("cart_code")
            cart = Cart.objects.get(cart_code = cart_code )
            user = request.user
            amount = sum([item.quantity * item.product.price for item in cart.items.all()])
            tax = Decimal("4.00")
            total_amount = amount+tax
            currency ="USD"
            redirect_url =f"{BASE_URL}/payment-status/"

            transaction = Transaction.objects.create(

                ref = tx_ref,
                cart=cart,
                amount = total_amount,
                currency=currency,
                user = user,
                status = 'pending'
            )
            flutterwave_payload =	{
			    "tx_ref":tx_ref,
			    "amount": str(total_amount),
			    "currency": currency,
			    "redirect_url":redirect_url,
			    "customer": {
			    	"email":user.email,
			    	"name": user.username,
			    	"phonenumber": user.phone,
			    },
			    "customizations": {
			    	"title": 'Flutterwave Standard Payment'
			    }
		    }

            headers= {
				"Authorization": f"Bearer {settings.FLUTTERWAVE_SECERET_KEY }",
				'Content-Type': 'application/json',
			}

            response = requests.post(
                'https://api.flutterwave.com/v3/payments',
                json=flutterwave_payload ,
                headers=headers
            )

            if response.status_code == 200:
                return Response(response.json() ,status = status.HTTP_200_OK)
            else:
                return Response(response.json(),status = response.status_code)
        # except exceptions as e:#includes all error
        except requests.exceptions.RequestException as e:#Request-related error occurred:
            return Response({"error":str(e)}, status = status.HTTP_500_INTERNAL_SERER_ERROR)

@api_view(["POST"])
def payment_callback(request):
    status =request.GET.get("status")
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    user = request.user

    if status == "successful":
        headers ={
            "Authorization" : f"Bearer {settings.FLUTTERWAVE_SECERET_KEY}"
        }

        response = requests.get(f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify", headers=headers)
        try:
            response_data = response.json()
        except ValueError:
            return Response({'error': 'Invalid response from Flutterwave'}, status=500)
            
        if response_data['status'] == 'success':
            transaction = Transaction.objects.get(ref = tx_ref)

            # confirm  transaction details

            if (response_data['data']['status'] == "successful"
            and float(response_data['data']['amount']) == float(transaction.amount)
            and response_data['data']['currency'] == transaction.currency) :
                transaction.status = 'completed'
                transaction.save()

                cart = transaction.cart
                cart.paid = True
                cart.user = user
                cart.save()

                return Response({'message':"Payement succesfull" , 'submessage':"you have successfully made payment"})
            else:
                return Response({'message':"Payement verification failed" , 'submessage':"your payment verification failed"})

        else:
            return Response({'message':"failed to verify transaction with fluterwave" , 'submessage':"we could make your paymentt"})

    else:
        return Response({'message':"Payement was not successful"} , status = 400)



paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" or "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_paypal_payment(request):
    if request.user.is_authenticated:
        try:
            tx_ref = str(uuid.uuid4())
            cart_code = request.data.get("cart_code")
            cart = Cart.objects.get(cart_code=cart_code)
            user = request.user
            amount = sum([item.quantity * item.product.price for item in cart.items.all()])
            tax = Decimal("4.00")
            total_amount = amount + tax
            currency = "USD"

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"{BASE_URL}/payment-status?paymentStatus=success&ref={tx_ref}",
                    "cancel_url": f"{BASE_URL}/payment-status?paymentStatus=cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Cart Items",
                            "sku": "cart",
                            "price": str(total_amount),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(total_amount),
                        "currency": "USD",
                    },
                    "description": "Payment for cart items."
                }]
            })

            transaction, created = Transaction.objects.get_or_create(
                ref=tx_ref,
                cart=cart,
                amount=total_amount,
                currency=currency,
                user=user,
                status='pending'
            )

            if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = str(link.href)
                        return Response({"approval_url": approval_url})
            else:
                return Response({"error": payment.error}, status=400)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        except paypalrestsdk.exceptions.ConnectionError as e:
            return Response({"error": str(e)}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@api_view(["POST"])
def paypal_payment_callback(request):
    payment_id =request.query_params.get("paymentId")
    payer_id = request.query_params.get("PayerID")
    ref = request.query_params.get("ref")

    user = request.user

    print("refff",ref)

    transaction = Transaction.objects.get(ref=ref)

    if payment_id and payer_id:
        # fetch payment object using paypal sdk
        payment =paypalrestsdk.Payment.find(payment_id)

        transaction.status ="completed"
        transaction.save()
        cart=transaction.cart
        cart.paid =True
        cart.user = user
        return Response({'message':"Payment succesfull" ,'submessage':"you have succesfully made payment"})

    else:
        return Response({"error":"invalid payment details"},status =400)




















