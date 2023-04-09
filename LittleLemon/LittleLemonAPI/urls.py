from django.urls import path, include
from . import views


urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.DeleteManagerView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeleteDeliveryView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.updateOrders),
    path('cart/menu-items', views.cart_menu_items),
    
]