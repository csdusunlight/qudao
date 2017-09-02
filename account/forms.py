from .models import MyUser
from django.contrib.auth.forms import UserCreationForm
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('email', 'mobile','username')

from django.contrib.auth.forms import UserChangeForm
class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = '__all__'
