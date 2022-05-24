from django.urls import path
from . import views


urlpatterns = [

    # Users APIS
    path('users/register', views.UserRegisterView.as_view()),
    path('users/login', views.UserLoginView.as_view()),
    path('users', views.ListUserView.as_view()),
    path('users/<int:id>', views.DetailUpdateDeleteUserView.as_view()),
    path('users/logout', views.LogoutView.as_view()),

    # CRUD Notes APIS
    path('notes', views.CreateAndListNoteView.as_view()),
    path('notes/<int:id>', views.UpdateDeleteDetailNoteView.as_view()),

]