from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.http import *
from django.db import IntegrityError

from accounts.models import UserProfile
from . models import Vendor,OpeningHour
from accounts . forms import UserProfileForm
from . forms import VendorForm,OpeningHourForm
from menu.models import Category,FoodItem
from menu.forms import CategoryForm,FoodItemForm
# Create your views here.

def get_vendor(request):
    vendor = Vendor.objects.get(user = request.user)
    return vendor

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    profile = get_object_or_404(UserProfile,user = request.user)
    vendor = get_object_or_404(Vendor,user = request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST,request.FILES,instance=profile)
        vendor_form = VendorForm(request.POST,request.FILES,instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request,"Profile Updated")
            return redirect('v_profile')
        else:
            messages.error(request,"An error occurred")
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form':profile_form,
        'vendor_form':vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request,'vendors/v_profile.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor = vendor).order_by("created_at")
    # food_items = FoodItem.objects.filter(vendor = vendor)

    context = {
        'categories':categories,
        # 'food_items':food_items,
    }
    return render(request,'vendors/menu_builder.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk):
    vendor = get_vendor(request)
    category = get_object_or_404(Category,pk=pk)
    food_items = FoodItem.objects.filter(category = category,vendor = vendor)

    context = {
        'food_items':food_items,
        'category':category,
    }

    return render(request,'vendors/fooditems_by_category.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name) + '-' + str(category.id)
            category.save()
            messages.success(request,'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form':form,
    }
    return render (request,'vendors/add_category.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            messages.success(request,'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form':form,
        'category':category,
    }
    return render(request,'vendors/edit_category.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category deleted successfully!')
    return redirect('menu_builder')
 

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.save()
            food_item.slug = slugify(food_title) + '-' + str(food_item.id)
            food_item.save()
            messages.success(request,"Food Item has been added successfully!")
            return redirect('fooditems_by_category', food_item.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields.get('category').queryset = Category.objects.filter(vendor = get_vendor(request))
    context = {
        'form':form
    }
    return render(request,'vendors/add_food.html',context)

def edit_food(request,pk):
    food = get_object_or_404(FoodItem,pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            food_item.save()
            messages.success(request,"Food Item has been edited successfully!")
            return redirect('fooditems_by_category', food_item.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor = get_vendor(request))
    context = {
        'form':form,
        'food':food,
    }
    return render(request,'vendors/edit_food.html',context)

def delete_food(request,pk):
    food = get_object_or_404(FoodItem,pk=pk)
    food.delete()
    messages.success(request,"Food Item has been deleted successfully!")
    return redirect('fooditems_by_category', food.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor = get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form':form,
        'opening_hours':opening_hours
    }
    return render(request,'vendors/opening_hours.html',context)

def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHour.objects.create(vendor = get_vendor(request),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status':'success','id':hour.id,'day':day.get_day_display(),'is_closed':'Closed'}        
                    else:
                        response = {'status':'success','id':hour.id,'day':day.get_day_display(),'from_hour':hour.from_hour,'to_hour':hour.to_hour}
                
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status':'failed', 'message':from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
        else:
            return JsonResponse("Invalid Request")
        
    return HttpResponse('opening_hours')

def remove_opening_hours(request,pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = OpeningHour.objects.get(pk=pk)
            hour.delete()
            response = {'status':'success','id':pk}
            return JsonResponse(response)
            
        else:
            return JsonResponse("Invalid Request")