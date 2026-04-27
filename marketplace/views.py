from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required

from.context_processors import get_cart_count,get_cart_amounts
from . models import Cart
from vendors.models import Vendor
from menu.models import Category,FoodItem
# Create your views here.

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved = True, user__is_active = True)
    vendor_count = vendors.count()
    context = {
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request,'marketplace/listings.html',context)


def vendor_detail(request,vendor_slug):
    vendor = get_object_or_404(Vendor,slug = vendor_slug)
    categories = Category.objects.filter(vendor = vendor).prefetch_related(
        Prefetch(
            'food_items',
            FoodItem.objects.filter(is_available = True)
        )
    )

        #  FOR SHOWING CART COUNT AGAINST EACH PRODUCTS

            # if request.user.is_authenticated:
            #     cart_items = Cart.objects.filter(user = request.user)
            #     cart_dict = {}
            #     for item in cart_items:
            #         cart_dict[item.fooditem.id] = item.quantity

            # for category in categories:
            #     for food in category.food_items.all():
            #         food.cart_qty = cart_dict.get(food.id,0)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user = request.user)
    else:
        cart_items = None



    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
       
    }
    return render (request,'marketplace/vendor_detail.html',context)




def add_to_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            try:
                fooditem = FoodItem.objects.get(pk=food_id)
                try:
                    check_cart = Cart.objects.get(user=request.user,fooditem = fooditem)
                    check_cart.quantity +=1
                    check_cart.save()
                    return JsonResponse({'status':'Success','message':"Quantity of fooditem increased!",'cart_counter':get_cart_count(request),'qty':check_cart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user,fooditem=fooditem,quantity = 1)
                    return JsonResponse({'status':'Success','message':"Fooditem Added to Cart!!",'cart_counter':get_cart_count(request),'qty':check_cart.quantity, 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':"This food does not exist!!"})    
        else:
            return JsonResponse({'status':'Failed','message':"Invalid Request"})
    
    else:
        return JsonResponse({'status':'login_required','message':"Please login to continue"})
    

def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            try:
                fooditem = FoodItem.objects.get(pk=food_id)
                try:
                    check_cart = Cart.objects.get(user=request.user,fooditem = fooditem)
                    if check_cart.quantity >1:
                        check_cart.quantity -=1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse({'status':'Success','cart_counter':get_cart_count(request),'qty':check_cart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message':"You do not have this item in your cart!"})    
            except:
                return JsonResponse({'status':'Failed','message':"This food does not exist!!"})    
        else:
            return JsonResponse({'status':'Failed','message':"Not ajax"})
    
    else:
        return JsonResponse({'status':'login_required','message':"Please login to continue"})


@login_required(login_url='login')
def cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user = user).order_by('created_at')

    

    context = {
        'cart_items':cart_items,

    }
    return render(request, 'marketplace/cart.html',context)


def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            try:
                cartitem = Cart.objects.get(user=request.user,id=cart_id)
                cartitem.delete()
                return JsonResponse({'status':'Success','message':'Cart item has been deleted!','cart_counter':get_cart_count(request), 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'Cart item does not exist'})
            
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required','message':"Please login to continue"})
