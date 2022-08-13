from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {} 
    if request.method == "POST":
        user = request.POST['user']
        password = request.POST['password']
        user = authenticate(username=user, password=password)

        # If user is valid
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # Failed Login
            resp =  redirect('djangoapp:index')
            resp['Location'] += '?msg=login_failed'
            return resp
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    resp =  redirect('djangoapp:index')
    resp['Location'] += '?msg=logout&user=' + request.user.username
    logout(request)
    return resp

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    return render(request, 'djangoapp/registration.html', context)

def signup_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['user']
        password = request.POST['password']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user_exist = False

        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))

        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name,
                                            last_name=last_name,password=password)
            login(request, user)
            return redirect('djangoapp:index')

        else:
            resp =  redirect('djangoapp:register')
            resp['Location'] += '?signin=exist'
            logout(request)
            return resp

    else:
        return redirect('djangoapp:register')



# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":          
        url = "https://164bc8d6.us-south.apigw.appdomain.cloud/api/dealership"                 
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name

        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    url = "https://164bc8d6.us-south.apigw.appdomain.cloud/api/review"
    
    # Get dealers from the URL
    reviews = get_dealer_reviews_from_cf(url,dealer_id)
    context['reviews'] = reviews
    context['dealer'] = dealer_id
    # Concat all dealer's short name
    dealer_details = ' '.join([dealer.review for dealer in reviews])
    # Return a list of dealer short name
    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):

    if request.method == "POST":
        if request.user.is_authenticated:
            url = "https://fa921fb7.us-south.apigw.appdomain.cloud/api/review"
            url2 = "https://fa921fb7.us-south.apigw.appdomain.cloud/api/dealership"

            car = CarModel.objects.get(id=request.POST['car'])
            dealer = get_dealer_by_id(url2, dealer_id)

            if request.POST['purchasecheck'] == "on":
                purchase = True
            else:
                purchase = False

            payload = {
                'review': {
                    "car_make": car.model_id.name,
                    "car_model": car.name,
                    "car_year": car.year.year,
                    "dealership": dealer_id,
                    "name": dealer.full_name,
                    "purchase": purchase,
                    "purchase_date": request.POST['purchasedate'],
                    "review": request.POST['content']
                }
            }
            
            json_result = post_request(url, payload)
            review = json_result

            context = {}
            context['dealer'] = dealer
            context['cars'] = list(CarModel.objects.all())
            context['created'] = True
            return render(request, 'djangoapp/add_review.html', context)
            
        else:
            raise PermissionDenied("Only auth users can post.")
    else:
        context = {}
        url = "https://fa921fb7.us-south.apigw.appdomain.cloud/api/dealership"
        context['dealer'] = get_dealer_by_id(url, dealer_id)
        context['cars'] = list(CarModel.objects.all())
        print(context['cars'])
        return render(request, 'djangoapp/add_review.html', context)
        
