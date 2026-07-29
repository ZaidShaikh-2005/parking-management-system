from django.contrib import admin
from .models import Customer, CustomerPhone, Staff, ParkingLot, Cart, OrderPlaced, ParkingSlot, BookingToken


# --------------------
# Customer Phone Inline
# --------------------
class CustomerPhoneInline(admin.TabularInline):
    model = CustomerPhone
    extra = 1


# --------------------
# Customer
# --------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'f_name', 'l_name', 'email', 'user')
    search_fields = ('f_name', 'l_name', 'email')
    inlines = [CustomerPhoneInline]


# --------------------
# Staff
# --------------------
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'f_name', 'l_name', 'role', 'contact')
    search_fields = ('f_name', 'l_name', 'role')
    list_filter = ('role',)


# --------------------
# Parking Lot
# --------------------
@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'location', 'total_slots')
    search_fields = ('title', 'location')
    list_filter = ('category',)


# --------------------
# Cart
# --------------------
@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')


# --------------------
# Orders
# --------------------
@admin.register(OrderPlaced)
class OrderPlacedAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'status', 'ordered_date')
    list_filter = ('status',)


# --------------------
# Parking Slot (FIXED ✅)
# --------------------
@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('parking_lot', 'slot_number', 'is_occupied')
    list_filter = ('parking_lot', 'is_occupied')
    ordering = ('parking_lot', 'slot_number')
    list_editable = ('is_occupied',)


# --------------------
# Booking Token
# --------------------
@admin.register(BookingToken)
class BookingTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'user', 'slot', 'created_at')
    search_fields = ('token', 'user__username')
    list_filter = ('created_at',)