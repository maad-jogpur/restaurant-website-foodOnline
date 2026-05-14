from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q

from vendors.models import Vendor

def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng,lat
    elif 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
    else:
        return None

def home(request):
    if get_or_set_current_location(request) is not None:
     
        pnt = GEOSGeometry('POINT(%s %s)' %get_or_set_current_location(request))
    
        vendors = Vendor.objects.filter(user_profile__location__distance_lte = (pnt,D(km=300))
        ).annotate(distance = Distance(pnt,'user_profile__location')).order_by('distance')
        
        for v in vendors:
            v.km = round( v.distance.km, 1)
            # v.km = v.distance.km
    else:
        vendors = Vendor.objects.filter(is_approved = True, user__is_active = True)[:8]
    context = {
        'vendors':vendors
    }
    return render(request,'home.html',context)
