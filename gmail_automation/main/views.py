from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user = request.user.username
        is_logged_in = True
    else:
        is_logged_in = False
        user = None
    return render(request, 'main/home.html',
                  {
                      'username': user,
                      'is_logged_in': is_logged_in,
                  })
