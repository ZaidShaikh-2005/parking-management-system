from django.db import models
from django.contrib.auth.models import User
import uuid


# ------------------ CUSTOMER ------------------
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    customer_id = models.AutoField(primary_key=True)

    f_name = models.CharField(max_length=100)
    m_name = models.CharField(max_length=100, blank=True, null=True)
    l_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)   # ✅ FIX

    def __str__(self):
        return f"{self.f_name} {self.l_name}"


# ------------------ PHONE (MULTIVALUED) ------------------
class CustomerPhone(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="phone_numbers")
    phone_no = models.CharField(max_length=15)

    def __str__(self):
        return self.phone_no


# ------------------ STAFF ------------------
class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)

    f_name = models.CharField(max_length=100)
    m_name = models.CharField(max_length=100, blank=True, null=True)
    l_name = models.CharField(max_length=100)

    role = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.f_name} {self.l_name}"


# ------------------ PARKING LOT ------------------
CATEGORY_CHOICES = (
   ('B', 'Basement'),
   ('O', 'Open'),
)

class ParkingLot(models.Model):
    title = models.CharField(max_length=200)

    selling_price = models.FloatField(verbose_name="Parking Price")
    discounted_price = models.FloatField()

    description = models.TextField()

    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)

    product_image = models.ImageField(upload_to='productimg', null=True, blank=True)

    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    # ✅ AUTO COUNT SLOTS
    @property
    def total_slots(self):
        return self.parking_slots.count()


# ------------------ CART ------------------
class Cart(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   product = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
   quantity = models.PositiveIntegerField(default=1)

   def __str__(self):
      return str(self.id)

   @property
   def total_cost(self):
      return self.quantity * self.product.discounted_price


# ------------------ ORDER ------------------
STATUS_CHOICES = (
   ('Pending', 'Pending'),   # ✅ FIX
   ('Accepted','Accepted'),
   ('Packed','Packed'),
   ('On The Way','On The Way'),
   ('Delivered','Delivered'),
   ('Cancel', 'Cancel')
)

class OrderPlaced(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
   product = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
   quantity = models.PositiveIntegerField(default=1)
   ordered_date = models.DateTimeField(auto_now_add=True)
   status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

   def __str__(self):
       return f"{self.user} - {self.product}"

   @property
   def total_cost(self):
      return self.quantity * self.product.discounted_price


# ------------------ PARKING SLOT ------------------
class ParkingSlot(models.Model):
    parking_lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.CASCADE,
        related_name="parking_slots"
    )

    slot_number = models.PositiveIntegerField()
    floor_number = models.IntegerField(null=True, blank=True)

    slot_type = models.CharField(max_length=50, blank=True)

    is_occupied = models.BooleanField(default=False)

    booking_source = models.CharField(
        max_length=20,
        choices=(
            ('ONLINE', 'Online Payment'),
            ('WHATSAPP', 'WhatsApp Booking'),
        ),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.parking_lot.title} - Slot {self.slot_number}"

    # ✅ UNIQUE SLOT PER LOT
    class Meta:
        unique_together = ('parking_lot', 'slot_number')


# ------------------ BOOKING TOKEN ------------------
class BookingToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.token

# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MaxValueValidator, MinValueValidator
# from django.contrib import admin
# import uuid

# STATE_CHOICES = (
#      ("Andhra Pradesh","Andhra Pradesh"),
#      ("Arunachal Pradesh ","Arunachal Pradesh "),
#      ("Assam","Assam"),
#      ("Bihar","Bihar"),
#      ("Chhattisgarh","Chhattisgarh"),
#      ("Goa","Goa"),
#      ("Gujarat","Gujarat"),
#      ("Haryana","Haryana"),
#      ("Himachal Pradesh","Himachal Pradesh"),
#      ("Jammu and Kashmir ","Jammu and Kashmir "),
#      ("Jharkhand","Jharkhand"),
#      ("Karnataka","Karnataka"),
#      ("Kerala","Kerala"),
#      ("Madhya Pradesh","Madhya Pradesh"),
#      ("Maharashtra","Maharashtra"),
#      ("Manipur","Manipur"),
#      ("Meghalaya","Meghalaya"),
#      ("Mizoram","Mizoram"),
#      ("Nagaland","Nagaland"),
#      ("Odisha","Odisha"),
#      ("Punjab","Punjab"),
#      ("Rajasthan","Rajasthan"),
#      ("Sikkim","Sikkim"),
#      ("Tamil Nadu","Tamil Nadu"),
#      ("Telangana","Telangana"),
#      ("Tripura","Tripura"),
#      ("Uttar Pradesh","Uttar Pradesh"),
#      ("Uttarakhand","Uttarakhand"),
#      ("West Bengal","West Bengal"),
#      ("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),
#      ("Chandigarh","Chandigarh"),
#      ("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),
#      ("Daman and Diu","Daman and Diu"),
#      ("Lakshadweep","Lakshadweep"),
#      ("National Capital Territory of Delhi","National Capital Territory of Delhi"),
#      ("Puducherry","Puducherry")
# )
# class Customer(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=200, null=True)
#     locality = models.CharField(max_length=200, null=True)
#     city = models.CharField(max_length=50, null=True)
#     zipcode = models.IntegerField(null=True)
#     state = models.CharField(choices=STATE_CHOICES, max_length=50, null=True)

#     def __str__(self):
#         return str(self.id)

# CATEGORY_CHOICES = (
#    ('B', 'Basement'),
#    ('O', 'Open'),
# )
# class Product(models.Model):
#     title = models.CharField(max_length=200, null=True)

#     selling_price = models.FloatField(
#         null=True,
#         verbose_name="Parking Price"
#     )

#     discounted_price = models.FloatField(null=True)

#     description = models.TextField(null=True)

#     # keep field, but hide its meaning
#     brand = models.CharField(
#         max_length=100,
#         null=True,
#         blank=True,
#         verbose_name="(Not Used)"
#     )

#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, null=True)

#     product_image = models.ImageField(
#         upload_to='productimg',
#         null=True,
#         verbose_name="Parking Area Image"
#     )

#     def __str__(self):
#         return f"Slot {self.id}"

#     class Meta:
#         verbose_name = "Parking Slot"
#         verbose_name_plural = "Parking Slots"

# class Cart(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
#    quantity = models.PositiveIntegerField(default=1, null=True)
   
#    def __str__(self):
#       return str(self.id)
#    class Meta:
#         verbose_name = "Booking"
#         verbose_name_plural = "Bookings"

#    @property
#    def total_cost(self):
#       return self.quantity * self.product.discounted_price

# STATUS_CHOICES = (
#    ('Accepted','Accepted'),
#    ('Packed','Packed'),
#    ('On The Way','On The Way'),
#    ('Delivered','Delivered'),
#    ('cancel', 'Cancel')
# )

# class OrderPlaced(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
#    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
#    quantity = models.PositiveIntegerField(default=1, null=True)
#    ordered_date = models.DateTimeField(auto_now_add=True, null=True)
#    status = models.CharField(max_length=100, choices=STATUS_CHOICES,default='Pending', null=True)
#    class Meta:
#         verbose_name = "Booked_Slots"
#         verbose_name_plural = "Booked Slots"

   
#    @property
#    def total_cost(self):
#       return self.quantity * self.product.discounted_price

# class ParkingSlot(models.Model):
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="parking_slots"
#     )
#     slot_number = models.PositiveIntegerField()
#     is_occupied = models.BooleanField(default=False)

#     booking_source = models.CharField(
#         max_length=20,
#         choices=(
#             ('ONLINE', 'Online Payment'),
#             ('WHATSAPP', 'WhatsApp Booking'),
#         ),
#         null=True,
#         blank=True
#     )

#     def __str__(self):
#         return f"{self.product.title} - Slot {self.slot_number}"


# class BookingToken(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     slot = models.ForeignKey('ParkingSlot', on_delete=models.CASCADE)
#     token = models.CharField(max_length=50, unique=True, editable=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         if not self.token:
#             self.token = uuid.uuid4().hex[:10].upper()  # UNIQUE CODE
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.token}"
