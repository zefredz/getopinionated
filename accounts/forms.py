import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.template.defaultfilters import slugify

from common.stringify import int_to_roman
from models import CustomUser

error_messages = {
    'duplicate_username': _("A user with that username already exists."),
    'duplicate_email': _("A user with that email address already exists."),
    'password_mismatch': _("The two password fields didn't match."),
}

class ProfileCreationForm(UserCreationForm):
    
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    
    #username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
    #    error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    username = forms.RegexField(label=_("Username or emailaddress"), max_length=100,
        regex=r'^[\w .@+-]+$',
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    
    def clean_username(self):
        # check if slug is unique (via CustomUser.isValidUserName)
        username = self.cleaned_data["username"]
        if not CustomUser.isValidUserName(username):
            raise forms.ValidationError(error_messages['duplicate_username'])
        try:
            User.objects.get(email=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(error_messages['duplicate_email'])

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        
        user.set_password(self.cleaned_data["password1"])
        # if the username is a mailaddress
        if re.match(r'^[a-zA-Z0-9!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', user.username):
            user.email = user.username
            #extract the username from the mailaddress
            username = user.username.split("@", 1)[0] #take the part before the @ in the mail address as username
            username = username.replace('.','_')
            #if this username would already exist, add roman numbers until this is not the case
            if not CustomUser.isValidUserName(username):
                # the username/userslug does already exist
                index = 2
                while True:
                    username="{} {}".format(username, int_to_roman(index))
                    if CustomUser.isValidUserName(username):
                        break
                    index += 1
            user.username = username
        else:
            user.email = ""
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        # self.fields['username'].widget.attrs['readonly'] = True # text input

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_username(self):
        # check if slug is unique (via CustomUser.isValidUserName)
        username = self.cleaned_data["username"]
        if not self.instance.profile.isValidUserNameChange(username):
            raise forms.ValidationError(error_messages['duplicate_username'])
        return username

    def clean_status(self):
        return self.instance.status

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Email address or username"), max_length=30)