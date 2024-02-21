from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User,Bus,Book,City
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm,BusForm,CityForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse




def home(request):
        return render(request, 'myapp/home.html')

@login_required(login_url='signin')
def findbus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if bus_list:
            return render(request, 'myapp/list.html', locals())
        else:
            context["error"] = "Sorry no buses availiable"
            return render(request, 'myapp/findbus.html', context)
    else:
        return render(request, 'myapp/findbus.html')



@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        seats_r = int(request.POST.get('no_seats'))
        bus = Bus.objects.get(id=id_r)
        if bus:
            if bus.rem >= seats_r:
                name_r = bus.bus_name
                cost = seats_r * bus.price
                source_r = bus.source
                dest_r = bus.dest
                nos_r = Decimal(bus.nos)
                price_r = bus.price
                date_r = bus.date
                time_r = bus.time
                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = bus.rem - seats_r
                Bus.objects.filter(id=id_r).update(rem=rem_r)
                book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                           source=source_r, busid=id_r,
                                           dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                           status='BOOKED')

                # Send booking confirmation email to the user's email address
                subject = "Booking Confirmation"
                message = f"""
                Your booking details:
                Bus name: {name_r}
                Starting point: {source_r}
                Destination point: {dest_r}
                Number of seats: {seats_r}
                Price: {price_r}
                Cost: {cost}
                Date: {date_r}
                Time: {time_r}
                """
                
                # Send the email using Django's send_mail function
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email_r],
                    fail_silently=False,
                )

                # Pass the booking details to the template for displaying the confirmation
                return render(request, 'myapp/bookings.html', locals())

            else:
                context["error"] = "Sorry, select fewer number of seats."
                return render(request, 'myapp/findbus.html', context)
        else:
            context["error"] = "Sorry, the selected bus does not exist."
            return render(request, 'myapp/findbus.html', context)

    else:
        return render(request, 'myapp/findbus.html')



@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            bus = Bus.objects.get(id=book.busid)
            rem_r = bus.rem + book.nos
            Bus.objects.filter(id=book.busid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            messages.success(request, "Booked Bus has been cancelled successfully.")
            return redirect(seebookings)
        except Book.DoesNotExist:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findbus.html')


@login_required(login_url='signin')
def seebookings(request):
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)

    if book_list.exists():
        context = {
            'book_list': book_list,
        }
        return render(request, 'myapp/booklist.html', context)
    else:
        context = {
            'error': "Sorry, no buses booked.",
        }
        return render(request, 'myapp/findbus.html', context)


def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        confirm_password_r = request.POST.get('confirm_password')
        first_name_r = request.POST.get('first_name')
        last_name_r = request.POST.get('last_name')

        # Check if the username already exists
        if User.objects.filter(username=name_r).exists():
            context["error"] = "This username has already been taken. Please choose a different username."
            return render(request, 'myapp/signup.html', context)

        # Check if the email address already exists
        if User.objects.filter(email=email_r).exists():
            context["error"] = "An account with this email address already exists."
            return render(request, 'myapp/signup.html', context)

        if password_r != confirm_password_r:
            context["error"] = "Passwords do not match."
            return render(request, 'myapp/signup.html', context)

        try:
            user = User.objects.create_user(
                username=name_r, email=email_r, password=password_r, 
                first_name=first_name_r, last_name=last_name_r
            )
            login(request, user)
            return render(request, 'myapp/thank.html')
        except Exception as e:
            context["error"] = "Unable to create the account. Please try again."
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html', context)



def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            if user.is_staff:
                # Admin user, redirect to admin:index
                return render(request,'myapp/home.html',context)
            else:
                # Regular user, redirect to findbus
                return redirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)



def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)


    

def safety(request):
    return render(request,'myapp/safety.html')


@login_required(login_url='signin')
def admin_buses(request):
    if request.user.is_staff:
        buses = Bus.objects.all()
        form = BusForm()
        if request.method == 'POST':
            form = BusForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('buses')
        return render(request, 'myapp/buslist.html', {'buses': buses, 'form': form})
    else:
        return redirect('success')

def edit_bus(request, bus_id):
    if request.user.is_staff:
        bus = Bus.objects.get(pk=bus_id)
        form = BusForm(instance=bus)
        if request.method == 'POST':
            form = BusForm(request.POST, instance=bus)
            if form.is_valid():
                form.save()
                return redirect('buses')
        return render(request, 'myapp/edit_bus.html', {'bus': bus, 'form': form})
    else:
        return redirect('success')

def delete_bus(request, bus_id):
    if request.user.is_staff:
        bus = Bus.objects.get(pk=bus_id)
        if request.method == 'POST':
            bus.delete()
            return redirect('buses')
        return render(request, 'myapp/delete_bus.html', {'bus': bus})
    else:
        return redirect('success')

def add_bus(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buses')  # Redirect after successful form submission
    else:
        form = BusForm()  # Create a new form instance for GET request
    
    return render(request, 'myapp/add_bus.html', {'form': form})

@login_required(login_url='signin')
def admin_users(request):
    if request.user.is_staff:
        users = User.objects.all()
        return render(request, 'myapp/userlist.html', {'users': users})
    else:
        return redirect('success')


@login_required(login_url='signin')
def admin_cities(request):
    if request.user.is_staff:
        cities = City.objects.all()
        return render(request, 'myapp/citylist.html', {'cities': cities})
    else:
        return redirect('success')

@login_required(login_url='signin')
def edit_city(request, city_id):
    if request.user.is_staff:
        city = City.objects.get(pk=city_id)
        if request.method == 'POST':
            form = CityForm(request.POST, instance=city)
            if form.is_valid():
                form.save()
                return redirect('admin_cities')
        else:
            form = CityForm(instance=city)
        return render(request, 'myapp/edit_city.html', {'form': form})
    else:
        return redirect('success')

@login_required(login_url='signin')
def delete_city(request, city_id):
    if request.user.is_staff:
        city = City.objects.get(pk=city_id)
        city.delete()
        return redirect('admin_cities')
    else:
        return redirect('success')

@login_required(login_url='signin')
def add_city(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = CityForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_cities')
        else:
            form = CityForm()
        return render(request, 'myapp/add_city.html', {'form': form})
    else:
        return redirect('success')

@login_required(login_url='signin')
def admin_books(request):
    if request.user.is_staff:
        books = Book.objects.all()
        return render(request, 'myapp/bookinglist.html', {'books': books})
    else:
        return redirect('success')
    
@login_required
def profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the updated password
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
        return redirect('findbus')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'myapp/profileupdate.html', {'form': form})


