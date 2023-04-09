from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import Category, MenuItem, Cart, Order, OrderItem
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']



class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category', 'category_id']
        depth=1



class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)

        # Assign the user to the Manager group
        manager_group = Group.objects.get(name='Manager')
        user.groups.add(manager_group)

        return user
    




class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)

        # Assign the user to the Manager group
        delivery_group = Group.objects.get(name='Delivery Crew')
        user.groups.add(delivery_group)

        return user
    

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

class OrderSerializer(serializers.ModelSerializer):
    user = CustomerSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    delivery_crew = DeliverySerializer(read_only=True)
    delivery_crew_id = serializers.IntegerField(write_only=True)
   
    class Meta:
        model = Order
        fields = ['user', 'user_id', 'delivery_crew', 'delivery_crew_id', 'status', 'total', 'date']



class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'order_id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        depth=1





class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    #price = serializers.SerializerMethodField(method_name = 'calculate_price')
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id']


    # def calculate_price(self, product:Cart):
    #     return product.quantity * product.unit_price

     