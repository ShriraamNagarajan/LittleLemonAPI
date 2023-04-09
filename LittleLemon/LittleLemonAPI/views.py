from datetime import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, throttle_classes

from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

from .models import MenuItem, Order, OrderItem, Cart


from .serializers import MenuItemSerializer, ManagerSerializer, DeliverySerializer, OrderSerializer, OrderItemSerializer, CartSerializer



from django.contrib.auth.models import User, Group

from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle

# Create your views here.


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsAllowed(BasePermission):
    message = "You are not authorized to perform this action sir."
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return True
        raise PermissionDenied(self.message)
  

class OrderAllowed(BasePermission):
    message = "You are not authorized to perform this action sir."
    def has_permission(self, request, view):
        if (not request.user.groups.filter(name='Manager').exists()) and (not request.user.groups.filter(name='Delivery Crew').exists()):
            return True
        raise PermissionDenied(self.message)
  



class MenuItemView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['price', 'featured', 'category']
    search_fields = ['title']


    def get_permissions(self):

            if self.request.method in ['POST']:
                return [IsAllowed()]
            else:
                return []

@permission_classes([IsAuthenticated])
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):

        queryset = MenuItem.objects.all()
        
        serializer_class = MenuItemSerializer

        def get_permissions(self):


            if self.request.method in ['DELETE', 'PUT', 'PATCH']:
                return [IsAllowed()]
            else:
                return []

        

@permission_classes([IsAuthenticated])
class ManagerView(generics.ListCreateAPIView):

    #queryset = Group.objects.get(name="Manager")
    queryset = Group.objects.get(name='Manager').user_set.all()
    serializer_class = ManagerSerializer




    def get_permissions(self):
        return [IsAdminUser()]





@permission_classes([IsAuthenticated])
class DeleteManagerView(generics.DestroyAPIView):
    queryset = Group.objects.get(name='Manager').user_set.all()
    serializer_class = ManagerSerializer
    def get_permissions(self):
        return [IsAdminUser()]







@permission_classes([IsAuthenticated])
class DeliveryView(generics.ListCreateAPIView):

    queryset = Group.objects.get(name='Delivery Crew').user_set.all()
    serializer_class = DeliverySerializer


    def get_permissions(self):
        return [IsAdminUser()]




@permission_classes([IsAuthenticated])
class DeleteDeliveryView(generics.DestroyAPIView):
    queryset = Group.objects.get(name='Delivery Crew').user_set.all()
    serializer_class = DeliverySerializer

    def get_permissions(self):
        return [IsAdminUser()]
    



   
@permission_classes([IsAuthenticated])
class OrdersView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderItemSerializer

    ordering_fields = ['total', 'date']
    filterset_fields = ['total', 'date', 'status']
    search_fields = ['status']
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Delivery Crew').exists():
            return OrderItem.objects.filter(order__delivery_crew=user)
        elif user.groups.filter(name='Manager').exists():
            return OrderItem.objects.all()
        else:
            return OrderItem.objects.filter(order__user=user)

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.groups.filter(name='Manager').exists() and not user.groups.filter(name='Delivery Crew').exists():
            cart_items = Cart.objects.filter(user=user)
            total_price = sum(cart_item.price for cart_item in cart_items)
            order = Order.objects.create(user=user, status=0, total=total_price, date=datetime.now())
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
            cart_items.delete()
            return Response({'message': 'Order created successfully'}, status.HTTP_201_CREATED)
        return Response({"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN) 

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def updateOrders(request, pk):
    if request.method == 'PATCH':
        if request.user.groups.filter(name='Manager').exists():
            try:
                order = Order.objects.get(id=pk)

                serialized_data = {}
                if 'status' in request.data:
                    serialized_data['status'] = request.data.get('status')
                if 'delivery_crew_id' in request.data:
                    serialized_data['delivery_crew_id'] = request.data.get('delivery_crew_id')
            
                serialized_item = OrderSerializer(order, data=serialized_data, partial=True)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({"message": "Order not found."}, status.HTTP_404_NOT_FOUND)
        elif request.user.groups.filter(name='Delivery Crew').exists():
            try:
                order = Order.objects.get(id=pk)
                serialized_data = {'status': request.data.get('status')}
                serialized_item = OrderSerializer(order, data=serialized_data, partial=True)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({"message": "Order not found."}, status.HTTP_404_NOT_FOUND)
        return Response({"message": "You are not authorized to perform this action."}, status.HTTP_403_FORBIDDEN)   
    elif request.method == 'PUT':
        if request.user.groups.filter(name='Manager').exists():
            try:
                order = Order.objects.get(id=pk)
                serialized_item = OrderSerializer(order, data=request.data, partial=True)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({"message": "Order not found."}, status.HTTP_404_NOT_FOUND)
        return Response({"message": "You are not authorized to perform this action."}, status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            try:
                order = Order.objects.get(id=pk)
                order.delete()
                return Response({"message": "Order deleted successfully."}, status.HTTP_204_NO_CONTENT)
            except Order.DoesNotExist:
                return Response({"message": "Order not found."}, status.HTTP_404_NOT_FOUND)
        return Response({"message": "You are not authorized to perform this action."}, status.HTTP_403_FORBIDDEN) 

    else:
        if (not request.user.groups.filter(name='Manager').exists()) and (not request.user.groups.filter(name='Delivery Crew').exists()):
            try:
            
                order = Order.objects.get(id=pk)
                
          
                if order.user != request.user:
                    return Response({'error': 'You are not authorized to access this resource.'}, status=status.HTTP_403_FORBIDDEN)
      
                items = OrderItem.objects.filter(order=order)
                
        
                serializer = OrderItemSerializer(items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)   
        return Response({"message": "You are not authorized to perform this action."}, status.HTTP_403_FORBIDDEN)
    





@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    if (not request.user.groups.filter(name='Manager').exists()) and (not request.user.groups.filter(name='Delivery Crew').exists()):
        user = request.user

        if request.method == 'GET':
            queryset = Cart.objects.filter(user=user)
            serializer = CartSerializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            data = request.data.dict()
            data['user'] = user.id

            serializer = CartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            Cart.objects.filter(user=user).delete()
            return Response(status=204)
        

    return Response({"message": "You are not authorized to perform this action."}, status.HTTP_403_FORBIDDEN)