from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify


from accounts.models import UserProfile
from . models import Vendor
from accounts . forms import UserProfileForm
from . forms import VendorForm
from menu.models import Category,FoodItem
from menu.forms import CategoryForm
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
    print(food_items)
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
            category.slug = slugify(category_name)
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


def delete_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category deleted successfully!')
    return redirect('menu_builder')