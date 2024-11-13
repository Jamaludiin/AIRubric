from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm


# Create your views here.

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # contains the field users should fill
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created for {username}')
            return redirect('users-login') # same the one belwo, but this is short, the name blog-login is in the urls.py of the blog app
            #return render(request,'blog/login.html',{'title': 'Authentication'}) 3 this is also optional
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form}) # return the form again cos it failed




def user_login(request):
    # check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        #Authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('app-home') # Redirect to the home page after successful login
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'users/login.html')


def user_logout(request):
    logout(request) 
    messages.success(request, "You Have Been Logged Out....")
    return redirect('blog-home') # Redirect to the home page after successful login


