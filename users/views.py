from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import jwt
import string,random
from .serializers import UserRegisterSerializer, UserLoginSerializer, \
                        UserDetailSerializer, NoteSerializer, UserUpdateSerializer
from .models import User, UserToken, Notes
from . utils import Authenticate
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# User Register View
class UserRegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # serializer validation
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": serializer.errors,
                                  "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=serializer.validated_data['email']).exists():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": "User Email Already Registered",
                                  "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                # store user data into database
                serializer.save()
                return Response(data={"status": status.HTTP_201_CREATED,
                                      "message": "User is Registered",
                                      "data": serializer.data},
                                status=status.HTTP_201_CREATED)
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "message": serializer.errors,
                                      "data":{}},
                                status=status.HTTP_201_CREATED)


# User Login API
class UserLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        # serializer validation
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": serializer.errors,
                                  "data":{}},
                            status= status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # check email and password
        if not User.objects.filter(email=email, password=password).exists():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                    "message": "The credentials you entered are not valid. Please try again.",
                                    "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email, password=password).exists():
            user = User.objects.filter(email=email, password=password).last()

            # token generate logic
            letters = string.ascii_letters
            random_string = ''.join(random.choice(letters) for i in range(15))
            payload = {'id': user.id, 'email': email, 'random_string': random_string }
            encoded_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            # store token in database
            UserToken.objects.create(user=user, token=encoded_token)
            serializer = UserDetailSerializer(user)

            return Response(data={"status": status.HTTP_200_OK,
                                    "message": "User successfully login, Token Generated.",
                                    "data": {'id': user.id,
                                         'token': encoded_token,
                                         'user_data':serializer.data}},
                            status= status.HTTP_200_OK)
        else:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                    "message": "The email address or password you entered is invalid. Please try again.",
                                    "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)


# User List View
class ListUserView(GenericAPIView):
    serializer_class = UserDetailSerializer

    # List of all Users
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser == True:
            users_obj = User.objects.all().order_by('created_at')
        else:
            users_obj = User.objects.filter(is_superuser=False).order_by('created_at')

        # apply pagginiation on users list
        if not users_obj:
            users_data = {'count': 0,
                          'users_list': []}
        else:
            result = list(users_obj)
            count = len(result)
            p = Paginator(result, 5)
            page_number = request.GET.get('page')
            try:
                users_obj = p.get_page(page_number)
            except PageNotAnInteger:
                users_obj = p.page(1)
            except EmptyPage:
                users_obj = p.page(p.num_pages)

            serializer = self.get_serializer(users_obj, many=True)

            users_data = {'count': count,
                          'users_list': serializer.data}

        return Response(data={"status": status.HTTP_200_OK,
                              "message": "Users list",
                              "data": users_data},
                        status=status.HTTP_200_OK)


# User Detail, Update and Delete View
class DetailUpdateDeleteUserView(GenericAPIView):

    # for delete user from database
    def delete(self, request, id):
        user = request.user
        # validation for user delete account
        if id == user.id:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": "You are not allowed to delete Your user account",
                                  "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.is_superuser:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": "You are not allowed to delete this User.",
                                  "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            delete_user = User.objects.get(id=id)
        except:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'User is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)
        delete_user.delete()
        return Response(data={"status": status.HTTP_200_OK,
                              "message": "User data deleted successfully",
                              "data": {}},
                        status=status.HTTP_200_OK)

    # update user
    def put(self, request, id):
        # get user from id
        try:
            user = User.objects.get(id=id)
        except:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'User is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)

        if not id == request.user.id and request.user.is_superuser == False:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": "You are not allowed to Edit this User.",
                                  "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            # check for email validation
            if User.objects.filter(email=serializer.validated_data['email']).exclude(email=user.email).exists():
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "message": "User Email Already Registered",
                                      "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)

            # update user data and store in database
            serializer.save()
            return Response(data={"status": status.HTTP_200_OK,
                                  "message": "User data updated successfully",
                                  "data": serializer.data},
                            status=status.HTTP_200_OK)

        return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                              "message": serializer.errors,
                              "data": {}},
                        status=status.HTTP_400_BAD_REQUEST)

    # Detail user
    def get(self,request,id):

        # get detail of user from database
        try:
            user = User.objects.get(id=id)
        except:
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'User is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)

        if not id == request.user.id and request.user.is_superuser == False:
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": "You are not allowed to Get this User.",
                                  "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDetailSerializer(user)

        return Response(data={"status": status.HTTP_200_OK,
                                "message": "User data get successfully",
                                "data": serializer.data},
                        status= status.HTTP_200_OK)


# logout User
class LogoutView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        try:
            token = Authenticate(self, request)
            try:
                # user token delete from user token model in database
                user_token = UserToken.objects.get(user=request.user, token=token)
                user_token.delete()
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "message": 'Already Logged Out.',
                                      "data":{}},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response(data={"status": status.HTTP_200_OK,
                                  "message": "User Logged Out.",
                                  "data":{}},
                            status=status.HTTP_200_OK)
        except:
            return Response(data={"status":status.HTTP_400_BAD_REQUEST,
                                  "message":'Already Logged Out.',
                                  "data":{}},
                            status=status.HTTP_400_BAD_REQUEST)


# Create and List Note
class CreateAndListNoteView(GenericAPIView):
    serializer_class = NoteSerializer

    # List of all Notes
    def get(self, request, *args, **kwargs):
        user = self.request.user
        # list of all notes created by login user
        Notes_obj = Notes.objects.filter(user=user).order_by('created_at')

        # apply pagginiation on notes list
        if not Notes_obj:
            notes_data = {'count': 0,
                            'notes_list': []}
        else:
            result = list(Notes_obj)
            count = len(result)
            p = Paginator(result, 5)
            page_number = request.GET.get('page')
            try:
                Notes_obj = p.get_page(page_number)
            except PageNotAnInteger:
                Notes_obj = p.page(1)
            except EmptyPage:
                Notes_obj = p.page(p.num_pages)

            serializer = self.get_serializer(Notes_obj, many=True)

            notes_data = {'count': count,
                            'notes_list': serializer.data}

        return Response(data={"status": status.HTTP_200_OK,
                              "message": "Note list",
                              "data": notes_data},
                        status=status.HTTP_200_OK)

    # Create notes
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # serializer validation
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": serializer.errors,
                                  "data": {} },
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                # create note in database
                user = request.user
                serializer.validated_data['user'] = user
                serializer.save()
                return Response(data={"status": status.HTTP_201_CREATED,
                                      "message": "Notes Created Successfully",
                                      "data": serializer.data},
                                status=status.HTTP_201_CREATED)
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "message": serializer.errors,
                                      "data": {} },
                                status=status.HTTP_400_BAD_REQUEST)


# Update, Delete And Detail Note
class UpdateDeleteDetailNoteView(GenericAPIView):
    serializer_class = NoteSerializer

    # Detail Note
    def get(self, request, id):
        # check note id is available or not in database table
        if not Notes.objects.filter(id=id, user=request.user):
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'Note is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)

        # get detail of note from database
        note = Notes.objects.get(id=id, user=request.user)
        serializer = self.get_serializer(note)

        return Response(data={"status": status.HTTP_200_OK,
                              "message": "Note data get successfully",
                              "data": serializer.data},
                        status=status.HTTP_200_OK)

    # Update Note
    def put(self, request, id):
        # check note id is available or not in database table
        if not Notes.objects.filter(user=request.user, id=id):
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'Note is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)

        # get object from database
        Notes_obj = Notes.objects.get(user=request.user, id=id)

        serializer = self.get_serializer(Notes_obj, data=request.data)

        # serializer validation
        if not serializer.is_valid():
            return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                  "message": serializer.errors,
                                  "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                # save updated note in database
                serializer.save()
                return Response(data={"status": status.HTTP_200_OK,
                                      "message": "Note Updated Successfully",
                                      "data": serializer.data},
                                status=status.HTTP_200_OK)
            except:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST,
                                      "message": serializer.errors,
                                      "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)

    # Delete Note
    def delete(self,request,id):
        # check note id is available or not in database table
        if not Notes.objects.filter(id=id,user=request.user):
            return Response(data={"status": status.HTTP_404_NOT_FOUND,
                                  "message": 'Note is not found, Please check ID',
                                  "data": {}},
                            status=status.HTTP_404_NOT_FOUND)

        # get note object from database
        note = Notes.objects.get(id=id, user=request.user)
        # delete note object
        note.delete()
        return Response(data={"status": status.HTTP_204_NO_CONTENT,
                              "message": 'Note is deleted successfully',
                              "data": {}},
                        status=status.HTTP_200_OK)
