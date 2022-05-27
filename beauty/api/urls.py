from django.urls import path
from .views import *


app_name = "api"

urlpatterns = [
    path('user/', CustomUserListCreateView.as_view(), name='user-list'),
    path('user/<int:pk>/', CustomUserDetailRUDView.as_view(), name='user-detail'),
    path('user/<int:user>/order/<int:id>/',
         CustomUserOrderDetailRUDView.as_view(),
         name='specialist-order-detail'),
    path('user/<int:user>/reviews/add/', ReviewAddView.as_view(),
         name='review-add'),
]
