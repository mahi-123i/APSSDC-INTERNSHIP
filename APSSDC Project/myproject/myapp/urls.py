from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('findbus', views.findbus, name="findbus"),
    path('bookings', views.bookings, name="bookings"),
    path('cancellings', views.cancellings, name="cancellings"),
    path('seebookings', views.seebookings, name="seebookings"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('success', views.success, name="success"),
    path('signout', views.signout, name="signout"),
    path('safety',views.safety,name="safety"),
    path('buses', views.admin_buses, name='buses'),
    path('users', views.admin_users, name='users'),
    path('cities', views.admin_cities, name='cities'),
    path('books', views.admin_books, name='books'),
    path('buses/add/', views.add_bus, name='add_bus'),
    path('buses/edit/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('buses/delete/<int:bus_id>/', views.delete_bus, name='delete_bus'),
    path('cities/', views.admin_cities, name='admin_cities'),
    path('cities/add/', views.add_city, name='add_city'),
    path('cities/edit/<int:city_id>/', views.edit_city, name='edit_city'),
    path('cities/delete/<int:city_id>/', views.delete_city, name='delete_city'),
    path('profile/update/', views.profile_update, name='profileupdate'),
]
