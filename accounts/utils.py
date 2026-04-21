def get_redirectURL(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
    elif user.role == 2:
        redirectUrl = 'custDashboard'
    else:
        redirectUrl = '/admin'
    return redirectUrl