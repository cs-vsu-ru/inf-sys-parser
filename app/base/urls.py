from django.urls import path

from .views import *

urlpatterns = [path('echo/', EchoView.as_view())]
