from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .restapis import get_dealers_from_cf, get_request, DealerReview, analyze_review_sentiments
from django.http import HttpResponse
from datetime import datetime
from .restapis import post_request
# Create your views here.

# Home page view
def index(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'index.html', context)

# Static page view
def static_page_view(request):
    return render(request, 'djangoapp/static_page.html')

# About page view
def about_view(request):
    return render(request, 'djangoapp/about.html')

# Contact page view
def contact_view(request):
    return render(request, 'djangoapp/contact.html')

# Login view
def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, 'Login successful.')
            return redirect('djangoapp:index')  # Redirect to the index page after successful login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'djangoapp/login.html')

# Logout view
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# User registration view
def registration_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Error creating user: {e}')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'djangoapp/registration.html')

# User signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('djangoapp:index')
    else:
        form = UserCreationForm()
    return render(request, 'djangoapp/signup.html', {'form': form})

# Get dealerships view
def get_dealerships(request):
    if request.method == "GET":
        url = "https://boratemayure-8000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/dealerships/dealer-get"  # Replace with the correct URL
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concatenate all dealer's short names
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short names
        return HttpResponse(dealer_names)

# Get dealer details view
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://boratemayure-8000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/reviews/dealer-get"
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context = {'reviews': dealer_reviews}
        return render(request, 'onlinecourse/dealer_details.html', context)


# Add review view
def add_review(request, dealer_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            review = {
                "time": datetime.utcnow().isoformat(),
                "name": request.user.username,
                "dealership": dealer_id,
                "review": request.POST.get('review'),
                "purchase": request.POST.get('purchase')
            }
            json_payload = {"review": review}
            url = "https://boratemayure-8000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/reviews/dealer-post"
            response = post_request(url, json_payload, dealerId=dealer_id)

            if response.status_code == 201:
                # Review added successfully
                return HttpResponse("Review added successfully.")
            else:
                # Failed to add review
                return HttpResponse("Failed to add review.")
        else:
            # User is not authenticated
            return HttpResponse("You need to login to add a review.")

    # If the request method is not POST, redirect to the dealer details page
    return redirect('dealer_details', dealer_id=dealer_id)
