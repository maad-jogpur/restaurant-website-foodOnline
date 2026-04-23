from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
# Create your views here.

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    return render(request,'vendors/v_profile.html')