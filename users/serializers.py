from rest_framework.serializers import ModelSerializer, Serializer
from . models import User, Notes
from rest_framework import serializers


# Register User Serializer
class UserRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'password', 'is_superuser']


# Login Serializer
class UserLoginSerializer(ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password']


# User Detail Serializer
class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email']


# User Update Serializer
class UserUpdateSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'name', 'email']


# Note Serializer
class NoteSerializer(ModelSerializer):

    class Meta:
        model = Notes
        fields = ['id', 'title', 'desc', 'tag']

