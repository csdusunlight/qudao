from .models import MyUser
from django.contrib.auth.forms import UserCreationForm
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('mobile','username','qq_number')

from django.contrib.auth.forms import UserChangeForm
class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = '__all__'
