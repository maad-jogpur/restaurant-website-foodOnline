from . models import Cart
from menu.models import FoodItem


def get_cart_count(request):

    if request.user.is_authenticated:
        count = 0
        cartitem = Cart.objects.filter(user=request.user)
        if cartitem:
            for item in cartitem:
                count+=item.quantity

    else:
        count = 0
    return dict(cart_count = count)

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user = request.user)

        for item in cart_items:
            subtotal += item.fooditem.price * item.quantity

        grand_total = subtotal + tax
    
    return dict(subtotal = subtotal, tax=tax, grand_total = grand_total)
    
    