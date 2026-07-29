from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from .forms import CustomerProfileForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from itertools import chain
from django.core.signing import Signer, BadSignature
from threading import Thread
from .forms import RegisterUserForm
from .mqtt_client import publish_booking, publish_gate_open_success
from .models import ParkingLot, Cart
signer = Signer()

from django.contrib.auth.decorators import login_required

@login_required
def payment_done(request):
    user = request.user

    cart = Cart.objects.filter(user=user)

    if not cart.exists():
        return redirect('home')

    customer = Customer.objects.filter(user=user).first()

    for c in cart:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=c.product,
            quantity=c.quantity,
            status='Accepted'
        )

    cart.delete()

    return redirect('orders')


@login_required
def remove_cart(request):
    prod_id = request.GET.get('prod_id')

    Cart.objects.filter(
        product_id=prod_id,
        user=request.user
    ).delete()

    amount = sum([
        p.quantity * p.product.discounted_price
        for p in Cart.objects.filter(user=request.user)
    ])

    return JsonResponse({
        'amount': amount,
        'totalamount': amount + 70
    })

# ------------------ HOME ------------------

class ProductView(View):
    def get(self, request):
        totalitem = 0

        all_slots = ParkingLot.objects.all()

        print("DEBUG DATA:", all_slots)   # 🔥 ADD THIS

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()

        return render(request, 'app/home.html', {
            'all_slots': all_slots,
            'totalitem': totalitem
        })


# ------------------ DETAIL ------------------
class ProductDetailView(View):
    def get(self, request, pk):
        product = ParkingLot.objects.get(pk=pk)
        slots = ParkingSlot.objects.filter(parking_lot=product)

        return render(request, 'app/productdetail.html', {
            'product': product,
            'slots': slots,
            'total_slots': slots.count(),
            'occupied_slots': slots.filter(is_occupied=True).count(),
            'available_slots': slots.filter(is_occupied=False).count(),
        })


# ------------------ CART ------------------
@login_required
def add_to_cart(request):
    product = ParkingLot.objects.get(id=request.GET.get('prod_id'))
    Cart.objects.create(user=request.user, product=product)
    return redirect('/cart')


@login_required
def show_cart(request):
    cart = Cart.objects.filter(user=request.user)

    amount = sum([p.quantity * p.product.discounted_price for p in cart])
    totalamount = amount + 70 if cart else 0

    if cart:
        return render(request, 'app/addtocart.html', {
            'carts': cart,
            'amount': amount,
            'totalamount': totalamount
        })
    else:
        return render(request, 'app/emptycart.html')


# ------------------ CART UPDATE ------------------
def plus_cart(request):
    prod_id = request.GET.get('prod_id')
    c = Cart.objects.filter(product_id=prod_id, user=request.user).first()

    if c:
        c.quantity += 1
        c.save()

    amount = sum([p.quantity * p.product.discounted_price for p in Cart.objects.filter(user=request.user)])

    return JsonResponse({
        'quantity': c.quantity,
        'amount': amount,
        'totalamount': amount + 70
    })


def minus_cart(request):
    prod_id = request.GET.get('prod_id')
    c = Cart.objects.filter(product_id=prod_id, user=request.user).first()

    if c:
        c.quantity -= 1
        if c.quantity <= 0:
            c.delete()
        else:
            c.save()

    amount = sum([p.quantity * p.product.discounted_price for p in Cart.objects.filter(user=request.user)])

    return JsonResponse({
        'quantity': c.quantity if c else 0,
        'amount': amount,
        'totalamount': amount + 70
    })


# ------------------ PROFILE ------------------
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            Customer.objects.create(
                user=request.user,
                f_name=form.cleaned_data['f_name'],
                m_name=form.cleaned_data['m_name'],
                l_name=form.cleaned_data['l_name'],
                email=form.cleaned_data['email']
            )
            messages.success(request, 'Profile Updated')

        return render(request, 'app/profile.html', {'form': form})


# ------------------ ADDRESS ------------------
@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)

    return render(request, 'app/address.html', {
        'add': add,
        'active': 'btn-primary'
    })


# ------------------ CHECKOUT ------------------
@login_required
def checkout(request):
    user = request.user

    cart_items = Cart.objects.filter(user=user)
    add = Customer.objects.filter(user=user)

    amount = sum([item.total_cost for item in cart_items])
    totalamount = amount + 70 if amount > 0 else 0

    booking_token = None

    if cart_items.exists():
        product = cart_items.first().product

        slot = ParkingSlot.objects.filter(
            parking_lot=product,
            is_occupied=False
        ).first()

        if slot:
            booking_token = signer.sign(slot.id)

    return render(request, 'app/checkout.html', {
        'cart_items': cart_items,
        'add': add,
        'amount': amount,
        'totalamount': totalamount,
        'booking_token': booking_token,
    })


# ------------------ ORDERS ------------------
@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)

    return render(request, 'app/orders.html', {
        'order_placed': op
    })


# ------------------ BASEMENT ------------------
def basement(request, data=None):

    if data is None:
        lots = ParkingLot.objects.filter(category='B')
    elif data == 'below':
        lots = ParkingLot.objects.filter(category='B', discounted_price__lt=800)
    elif data == 'above':
        lots = ParkingLot.objects.filter(category='B', discounted_price__gt=800)

    return render(request, 'app/basement.html', {
        'lots': lots
    })


# ------------------ OPEN PARKING ------------------
def open_parking(request, data=None):

    if data is None:
        lots = ParkingLot.objects.filter(category='O')
    elif data == 'below':
        lots = ParkingLot.objects.filter(category='O', discounted_price__lt=800)
    elif data == 'above':
        lots = ParkingLot.objects.filter(category='O', discounted_price__gt=800)

    return render(request, 'app/open_parking.html', {
        'lots': lots
    })


# ------------------ ADMIN CONFIRM ------------------
@login_required(login_url='/admin/login/')
def admin_confirm_booking(request):
    token = request.GET.get('token')
    action = request.GET.get('action')

    try:
        slot_id = signer.unsign(token)
    except BadSignature:
        return HttpResponse("Invalid link")

    slot = get_object_or_404(ParkingSlot, id=slot_id)

    cart_item = Cart.objects.filter(product=slot.parking_lot).first()
    if not cart_item:
        return HttpResponse("No customer")

    customer = cart_item.user

    if action == "yes":
        if slot.is_occupied:
            return HttpResponse("Already occupied")

        slot.is_occupied = True
        slot.save()

        Thread(
            target=publish_booking,
            kwargs={"product": slot.parking_lot.title, "slot": slot.slot_number},
            daemon=True
        ).start()

        BookingToken.objects.create(user=customer, slot=slot)

        return render(request, 'app/booking_confirmed.html', {'slot': slot})

    return render(request, 'app/booking_rejected.html')


# ------------------ GATE ENTRY ------------------
def gate_entry(request):
    message = None
    status = None

    if request.method == "POST":
        token = request.POST.get("token")

        try:
            t = BookingToken.objects.get(token=token)

            Thread(
                target=publish_gate_open_success,
                kwargs={"token": t.token, "slot": t.slot.slot_number},
                daemon=True
            ).start()

            t.delete()
            message = "ACCESS GRANTED"
            status = "success"

        except:
            message = "INVALID TOKEN"
            status = "error"

    return render(request, "app/gate.html", {
        "message": message,
        "status": status
    })


# ------------------ LOGOUT ------------------
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('home')


# ------------------ REGISTER USER ------------------
class RegisterUserView(View):

    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            messages.error(request, "Registration failed!")

        return render(request, 'app/customerregistration.html', {'form': form})

# from django.shortcuts import render, redirect, get_object_or_404
# from django.views import View
# from .models import *
# from .forms import RegisterUserForm, CustomerProfileForm
# from django.views.generic import CreateView
# from django.contrib import messages
# from django.db.models import Q
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# from django.contrib.auth import logout
# from itertools import chain
# from django.core.signing import Signer, BadSignature
# from django.shortcuts import render, get_object_or_404, redirect
# from .models import ParkingSlot
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Cart, ParkingSlot
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import ParkingSlot
# from django.http import HttpResponse
# from django.core.signing import Signer
# from django.contrib.auth.models import User
# from .mqtt_client import publish_booking
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import BookingToken
# from .mqtt_client import publish_gate_open_success

# signer = Signer()

# from django.http import JsonResponse
# from app.models import ParkingSlot

# def slot_status_api(request, product_id):
#     slots = ParkingSlot.objects.filter(product_id=product_id)
#     data = []

#     for slot in slots:
#         data.append({
#             "slot": slot.slot_number,
#             "occupied": slot.is_occupied
#         })

#     return JsonResponse(data, safe=False)



# class ProductView(View):
#     def get(self, request):
#         totalitem = 0

#         basement = Product.objects.filter(category='B')
#         open_parking = Product.objects.filter(category='O')

#         # Combine both querysets
#         all_slots = list(chain(basement, open_parking))

#         if request.user.is_authenticated:
#             totalitem = Cart.objects.filter(user=request.user).count()

#         return render(request, 'app/home.html', {
#             'all_slots': all_slots,
#             'totalitem': totalitem
#         })
    
# class ProductDetailView(View):
#     def get(self, request, pk):
#         product = Product.objects.get(pk=pk)
#         slots = ParkingSlot.objects.filter(product=product)

#         total_slots = slots.count()
#         occupied_slots = slots.filter(is_occupied=True).count()
#         available_slots = slots.filter(is_occupied=False).count()

#         return render(request, 'app/productdetail.html', {
#             'product': product,
#             'slots': slots,
#             'total_slots': total_slots,
#             'occupied_slots': occupied_slots,
#             'available_slots': available_slots,
#         })


# @login_required
# def add_to_cart(request):
#     user=request.user
#     product_id = request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     Cart(user=user, product=product).save()
#     return redirect('/cart')

# @login_required
# def show_cart(request):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = Cart.objects.filter(user=request.user).count()

#     user = request.user
#     cart = Cart.objects.filter(user=user)

#     amount = 0.0
#     shipping_amount = 70.0

#     for p in cart:
#         amount += p.quantity * p.product.discounted_price

#     totalamount = amount + shipping_amount if cart else 0

#     if cart:
#         return render(request, 'app/addtocart.html', {
#             'carts': cart,
#             'amount': amount,
#             'totalamount': totalamount,
#             'totalitem': totalitem
#         })
#     else:
#         return render(request, 'app/emptycart.html')



# def logout_view(request):
#     # Log the user out
#     logout(request)
    
#     # Show a success message
#     messages.info(request, 'You have been logged out successfully.')
    
#     # Redirect to the home page or any other page after logout
#     return redirect('home')  # Replace 'home' with the name of your homepage URL

# def plus_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET['prod_id']
#         c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
#         c.quantity+=1
#         c.save()
#         amount = 0.0
#         shipping_amount = 70.0
#         cart_product = [p for p in Cart.objects.all()if p.user == request.user]
#         for p in cart_product:
#             tempamount = (p.quantity * p.product.discounted_price)
#             amount += tempamount

#         data = {
#             'quantity': c.quantity,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         }
#         return JsonResponse(data)

# def minus_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET['prod_id']
#         c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
#         c.quantity-=1
#         c.save()
#         amount = 0.0
#         shipping_amount = 70.0
#         cart_product = [p for p in Cart.objects.all()if p.user == request.user]
#         for p in cart_product:
#             tempamount = (p.quantity * p.product.discounted_price)
#             amount += tempamount

#         data = {
#             'quantity': c.quantity,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         }
#         return JsonResponse(data)

# @login_required
# def remove_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET.get('prod_id')

#         Cart.objects.filter(
#             product_id=prod_id,
#             user=request.user
#         ).delete()

#         amount = 0.0
#         shipping_amount = 70.0

#         cart_product = Cart.objects.filter(user=request.user)
#         for p in cart_product:
#             amount += p.quantity * p.product.discounted_price

#         return JsonResponse({
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         })
# def plus_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET.get('prod_id')

#         c = Cart.objects.filter(
#             product_id=prod_id,
#             user=request.user
#         ).first()

#         if c:
#             c.quantity += 1
#             c.save()

#         amount = 0.0
#         shipping_amount = 70.0
#         for p in Cart.objects.filter(user=request.user):
#             amount += p.quantity * p.product.discounted_price

#         return JsonResponse({
#             'quantity': c.quantity,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         })

# def minus_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET.get('prod_id')

#         c = Cart.objects.filter(
#             product_id=prod_id,
#             user=request.user
#         ).first()

#         if c:
#             c.quantity -= 1
#             if c.quantity <= 0:
#                 c.delete()
#             else:
#                 c.save()

#         amount = 0.0
#         shipping_amount = 70.0
#         for p in Cart.objects.filter(user=request.user):
#             amount += p.quantity * p.product.discounted_price

#         return JsonResponse({
#             'quantity': c.quantity if c else 0,
#             'amount': amount,
#             'totalamount': amount + shipping_amount
#         })

# @login_required
# def buy_now(request, product_id):
#     product = get_object_or_404(Product, id=product_id)  # Get the product based on product_id
#     shipping_amount = 70.0  # Set the shipping amount
#     total_amount = product.discounted_price + shipping_amount  # Calculate the total amount
    
#     # Pass the product and total amount to the template
#     return render(request, 'app/buynow.html', {
#         'product': product,
#         'total_amount': total_amount
#     })


# @login_required
# def address(request):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     add = Customer.objects.filter(user=request.user)
#     return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})

# @login_required
# def orders(request):
#     totalitem = 0 
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     op = OrderPlaced.objects.filter(user=request.user)
#     return render(request, 'app/orders.html', {'order_placed':op, 'totalitem':totalitem})


# def mobile(request, data=None):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     if data == None:
#         mobiles = Product.objects.filter(category= 'B')
#     # elif data == 'Remi' or data == 'Samsung':
#     #     mobiles = Product.objects.filter(category= 'FB').filter(brand=data)
#     elif data == 'below':
#          mobiles = Product.objects.filter(category= 'B').filter(discounted_price__lt=800)
#     elif data == 'above':
#          mobiles = Product.objects.filter(category= 'B').filter(discounted_price__gt=800)
#     return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem':totalitem})

# # new view created  
# def tennis(request, data=None):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     if data == None:
#         tennis_items = Product.objects.filter(category='T')  # Make sure 'Tennis' is the correct category in your Product model
#     elif data == 'below':
#         tennis_items = Product.objects.filter(category='T').filter(discounted_price__lt=800)
#     elif data == 'above':
#         tennis_items = Product.objects.filter(category='T').filter(discounted_price__gt=800)
#     return render(request, 'app/tennis.html', {'mobiles': tennis_items, 'totalitem': totalitem})

# def cricket(request, data=None):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     if data == None:
#         cricket_items = Product.objects.filter(category='O')  # Make sure 'Cricket' is the correct category in your Product model
#     elif data == 'below':
#         cricket_items = Product.objects.filter(category='O').filter(discounted_price__lt=800)
#     elif data == 'above':
#         cricket_items = Product.objects.filter(category='O').filter(discounted_price__gt=800)
#     return render(request, 'app/cricket.html', {'mobiles': cricket_items, 'totalitem': totalitem})

# def kits(request, data=None):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     if data == None:
#         kits = Product.objects.filter(category='K')  # Make sure 'Cricket' is the correct category in your Product model
#     elif data == 'below':
#         kits = Product.objects.filter(category='K').filter(discounted_price__lt=800)
#     elif data == 'above':
#         kits = Product.objects.filter(category='K').filter(discounted_price__gt=800)
#     return render(request, 'app/kits.html', {'mobiles': kits, 'totalitem': totalitem})

# def refreshment(request, data=None):    
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     if data == None:
#         cricket_items = Product.objects.filter(category='R')  # Make sure 'Cricket' is the correct category in your Product model
#     elif data == 'below':
#         cricket_items = Product.objects.filter(category='R').filter(discounted_price__lt=800)
#     elif data == 'above':
#         cricket_items = Product.objects.filter(category='R').filter(discounted_price__gt=800)
#     return render(request, 'app/refreshment.html', {'mobiles': cricket_items, 'totalitem': totalitem})

# class RegisterUserView (View):
#     def get(self, request):
#         form = RegisterUserForm()
#         return render(request, 'app/customerregistration.html', {'form':form})
#     def post(self, request):
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             messages.success(request, 'Congratulation!! Sucessfully Registered')
#             form.save()
#         return render(request, 'app/customerregistration.html', {'form':form})

# @login_required
# def checkout(request):
#     totalitem = Cart.objects.filter(user=request.user).count()
#     user = request.user

#     add = Customer.objects.filter(user=user)
#     cart_items = Cart.objects.filter(user=user)

#     amount = 0.0
#     shipping_amount = 70.0

#     for item in cart_items:
#         amount += item.total_cost

#     totalamount = amount + shipping_amount if amount > 0 else 0

#     booking_token = None

#     if cart_items.exists():
#         # 🔥 GET FIRST FREE SLOT OF THAT PRODUCT
#         product = cart_items.first().product
#         slot = ParkingSlot.objects.filter(
#             product=product,
#             is_occupied=False
#         ).first()

#         if slot:
#             booking_token = signer.sign(slot.id)

#     return render(request, 'app/checkout.html', {
#         'add': add,
#         'cart_items': cart_items,
#         'amount': amount,
#         'totalamount': totalamount,
#         'totalitem': totalitem,
#         'booking_token': booking_token,
#     })


# @login_required
# def payment_done(request):
#     totalitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#     user = request.user
#     custid = request.GET.get('custid')
#     customer = Customer.objects.get(id=custid)
#     cart = Cart.objects.filter(user=user)
#     for c in cart:
#         OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
#         c.delete()
#     return redirect("orders")

# @method_decorator(login_required, name='dispatch')
# class ProfileView(View):
#     def get(self, request):
#         form = CustomerProfileForm()
#         return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
#     def post(self, request):
#         form = CustomerProfileForm(request.POST)
#         if form.is_valid(): 
#             usr = request.user
#             name = form.cleaned_data['name']
#             locality = form.cleaned_data['locality']
#             city = form.cleaned_data['city']
#             state = form.cleaned_data['state']
#             zipcode = form.cleaned_data['zipcode']
#             reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
#             reg.save()
#             messages.success(request, 'Congratulations!! Profile Updated Sucessfully')
#         return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

# # @login_required
# # def whatsapp_book_slot(request, slot_id):
# #     slot = get_object_or_404(ParkingSlot, id=slot_id)

# #     if slot.is_occupied:
# #         messages.error(request, "This slot is already occupied.")
# #         return redirect('home')

# #     # Book slot WITHOUT payment
# #     slot.is_occupied = True
# #     slot.booking_source = 'WHATSAPP'
# #     slot.save()

# #     messages.success(
# #         request,
# #         f"Slot {slot.slot_number} booked successfully via WhatsApp!"
# #     )
# #     return redirect('orders')

# # def admin_confirm_slot(request, slot_id):
# #     token = request.GET.get("token")
# #     slot = get_object_or_404(ParkingSlot, id=slot_id)

# #     try:
# #         signer.unsign(token)
# #     except BadSignature:
# #         return render(request, "app/invalid_link.html")

# #     if request.method == "POST":
# #         if "confirm" in request.POST:
# #             slot.is_occupied = True
# #             slot.save()
# #             return render(request, "app/confirmed.html", {"slot": slot})

# #         if "reject" in request.POST:
# #             return render(request, "app/rejected.html", {"slot": slot})

# #     return render(request, "app/admin_confirm.html", {"slot": slot})
# # -------------------------------------------------------------------------------------------------------------------
# from django.core.signing import BadSignature
# from threading import Thread


# @login_required(login_url='/admin/login/')
# def admin_confirm_booking(request):
#     token = request.GET.get('token')
#     action = request.GET.get('action')

#     if not token or not action:
#         return HttpResponse("❌ Invalid booking link")

#     try:
#         slot_id = signer.unsign(token)
#     except BadSignature:
#         return HttpResponse("❌ Tampered or invalid link")

#     slot = get_object_or_404(ParkingSlot, id=slot_id)

#     # 🔴 GET CUSTOMER FROM CART (CRITICAL)
#     cart_item = Cart.objects.filter(product=slot.product).first()
#     if not cart_item:
#         return HttpResponse("❌ No customer found for this booking")

#     customer = cart_item.user

#     # 🔴 FINAL SAFETY CHECK (THIS WAS THE BUG SOURCE)
#     user_email = customer.email
#     if not user_email:
#         return HttpResponse("❌ Customer email not found")

#     if action == "yes":

#         if slot.is_occupied:
#             return HttpResponse("⚠ Slot already occupied")

#         # ✅ OCCUPY SLOT
#         slot.is_occupied = True
#         slot.booking_source = "WHATSAPP"
#         slot.save()

#         # 🔥 MQTT BOOK (NON-BLOCKING)
#         Thread(
#             target=publish_booking,
#             kwargs={
#                 "product": slot.product.title,
#                 "slot": slot.slot_number
#             },
#             daemon=True
#         ).start()

#         # ✅ CREATE TOKEN FOR CUSTOMER
#         booking_token = BookingToken.objects.create(
#             user=customer,
#             slot=slot
#         )

#         # ✅ SEND EMAIL (GUARANTEED TO USER)
#         send_mail(
#             subject="🎟 Smart Parking Booking Confirmed",
#             message=f"""
# Hello {customer.username},

# Your parking slot has been successfully booked ✅

# 📍 Area: {slot.product.title}
# 🚗 Slot Number: {slot.slot_number}
# 🔐 Booking Token: {booking_token.token}

# Please show this token at the parking entry.

# Thank you,
# Smart Parking Team
# """,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[user_email],   # 🔥 ONLY CUSTOMER
#             fail_silently=False
#         )

#         # ✅ DELETE CUSTOMER CART ITEM
#         Cart.objects.filter(user=customer, product=slot.product).delete()

#         return render(
#             request,
#             'app/booking_confirmed.html',
#             {
#                 'slot': slot,
#                 'token': booking_token.token,
#                 'customer': customer.username
#             }
#         )

#     if action == "no":
#         return render(
#             request,
#             'app/booking_rejected.html',
#             {'slot': slot}
#         )

#     return HttpResponse("❌ Invalid action")
# # @login_required(login_url='/admin/login/')
# # def admin_confirm_booking(request):
# #     token = request.GET.get('token')
# #     action = request.GET.get('action')

# #     if not token or not action:
# #         return HttpResponse("❌ Invalid booking link")

# #     try:
# #         slot_id = signer.unsign(token)
# #     except BadSignature:
# #         return HttpResponse("❌ Tampered or invalid link")

# #     slot = get_object_or_404(ParkingSlot, id=slot_id)

# #     if action == "yes":

# #         # 🔥 MQTT BOOK — ALWAYS FIRE ON FIRST CONFIRM
# #         first_time_booking = not slot.is_occupied

# #         if slot.is_occupied:
# #             return HttpResponse("⚠ Slot already occupied")

# #         # ✅ OCCUPY SLOT
# #         slot.is_occupied = True
# #         slot.booking_source = "WHATSAPP"
# #         slot.save()

# #         # 🔥 MQTT (NON BLOCKING) — GUARANTEED
# #         if first_time_booking:
# #             Thread(
# #                 target=publish_booking,
# #                 kwargs={
# #                     "product": slot.product.title,
# #                     "slot": slot.slot_number
# #                 },
# #                 daemon=True
# #             ).start()

# #         # ✅ CREATE UNIQUE TOKEN (AS IT IS)
# #         booking_token = BookingToken.objects.create(
# #             user=request.user,
# #             slot=slot
# #         )

# #         # ✅ SEND EMAIL (AS IT IS)
# #         send_mail(
# #             subject="🎟 Smart Parking Booking Confirmed",
# #             message=f"""
# # Hello {request.user.username},

# # Your parking slot has been successfully booked ✅

# # 📍 Area: {slot.product.title}
# # 🚗 Slot Number: {slot.slot_number}
# # 🔐 Booking Token: {booking_token.token}

# # Please show this token at the parking entry.

# # Thank you,
# # Smart Parking Team
# # """,
# #             from_email=settings.EMAIL_HOST_USER,
# #             recipient_list=[request.user.email],
# #             fail_silently=False
# #         )

# #         # ✅ DELETE CART (AS IT IS)
# #         Cart.objects.filter(user=request.user, product=slot.product).delete()

# #         return render(
# #             request,
# #             'app/booking_confirmed.html',
# #             {
# #                 'slot': slot,
# #                 'token': booking_token.token
# #             }
# #         )

# #     if action == "no":
# #         return render(request, 'app/booking_rejected.html', {'slot': slot})

# #     return HttpResponse("❌ Invalid action")
# # -------------------------------------------------------------------------------------------------------

# # from django.core.signing import BadSignature

# # def admin_confirm_booking(request):
# #     token = request.GET.get('token')
# #     action = request.GET.get('action')

# #     if not token or not action:
# #         return HttpResponse("❌ Invalid booking link")

# #     try:
# #         slot_id = signer.unsign(token)
# #     except BadSignature:
# #         return HttpResponse("❌ Tampered or invalid link")

# #     slot = get_object_or_404(ParkingSlot, id=slot_id)

# #     if action == "yes":
# #         if slot.is_occupied:
# #             return HttpResponse("⚠ Slot already occupied")

# #         # ✅ OCCUPY SLOT
# #         slot.is_occupied = True
# #         slot.save()

# #         # 🔥 MQTT PUBLISH (ADDED – NO LOGIC CHANGE)
# #         publish_booking(
# #             product=slot.product.title,   # "Open"
# #             slot=slot.slot_number          # 2
# #         )

# #         # ✅ DELETE CART ITEM FOR THIS SLOT'S PRODUCT
# #         Cart.objects.filter(product=slot.product).delete()

# #         return render(
# #             request,
# #             'app/booking_confirmed.html',
# #             {'slot': slot}
# #         )

# #     if action == "no":
# #         return render(
# #             request,
# #             'app/booking_rejected.html',
# #             {'slot': slot}
# #         )

# #     return HttpResponse("❌ Invalid action")


# def gate_entry(request):
#     message = None
#     status = None

#     if request.method == "POST":
#         entered_token = request.POST.get("token")

#         try:
#             token_obj = BookingToken.objects.get(token=entered_token)

#             # ✅ TOKEN VALID
#             status = "success"
#             message = "✅ TOKEN VERIFIED — GATE OPENING"

#             # 🔥 MQTT — NON BLOCKING (FIX)
#             Thread(
#                 target=publish_gate_open_success,
#                 kwargs={
#                     "token": token_obj.token,
#                     "slot": token_obj.slot.slot_number
#                 },
#                 daemon=True
#             ).start()

#             # ❌ DELETE TOKEN (ONE-TIME USE)
#             token_obj.delete()

#         except BookingToken.DoesNotExist:
#             status = "error"
#             message = "❌ INVALID OR ALREADY USED TOKEN — ACCESS DENIED"

#     return render(request, "app/gate.html", {
#         "message": message,
#         "status": status
#     })