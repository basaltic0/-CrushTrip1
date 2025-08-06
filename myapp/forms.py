from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="姓氏", widget=forms.TextInput())
    last_name = forms.CharField(label="名字", widget=forms.TextInput())
    username = forms.CharField(label="帳號名稱", widget=forms.TextInput())
    password1 = forms.CharField(label="密碼", widget=forms.PasswordInput())
    password2 = forms.CharField(label="確認密碼", widget=forms.PasswordInput())
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "請輸入電子信箱", "required": "required"}
        ),
    )

    avatar = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg, image/png, image/jpg"}
        ),
    )

    gender = forms.ChoiceField(
        choices=[("M", "男性"), ("F", "女性"), ("O", "其他")],
        widget=forms.Select(),
        label="性別",
    )

    travel_partner = forms.ChoiceField(
        choices=CustomUser._meta.get_field("travel_partner").choices,
        widget=forms.Select(),
        required=False,
        label="期望旅伴性別",
    )

    preferred_age_range = forms.ChoiceField(
        choices=CustomUser._meta.get_field("preferred_age_range").choices,
        widget=forms.Select(),
        required=False,
        label="期望年齡層",
    )

    preferred_travel = forms.MultipleChoiceField(
        choices=CustomUser._meta.get_field("preferred_travel").choices,
        widget=forms.CheckboxSelectMultiple(),
        label="旅遊偏好",
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "gender",
            "preferred_travel",
            "travel_partner",
            "preferred_age_range",
            "password1",
            "password2",
            "avatar",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "兩次輸入的密碼不一致。")

#忘記帳號
class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(label="Email")

#send message
class ContactForm(forms.Form):
    name = forms.CharField(label="姓名", max_length=100)
    email = forms.EmailField(label="Email")
    subject = forms.CharField(label="主旨", max_length=150)
    message = forms.CharField(label="訊息內容", widget=forms.Textarea)

#修改會員資料
class CustomUserUpdateForm(forms.Form):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={'class': 'form-control',"placeholder": "請輸入電子信箱"})
    )
    first_name = forms.CharField(label="姓氏", widget=forms.TextInput())
    last_name = forms.CharField(label="名字", widget=forms.TextInput())
    username = forms.CharField(label="帳號名稱", widget=forms.TextInput())
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg, image/png, image/jpg"}
        ),
    )
    gender = forms.ChoiceField(
        choices=CustomUser._meta.get_field("gender").choices,
        widget=forms.Select(),
        label="性別",
    )
    travel_partner = forms.ChoiceField(
        choices=CustomUser._meta.get_field("travel_partner").choices,
        widget=forms.Select(),
        required=False,
        label="期望旅伴性別",
    )
    preferred_age_range = forms.ChoiceField(
        choices=CustomUser._meta.get_field("preferred_age_range").choices,
        widget=forms.Select(),
        required=False,
        label="期望年齡層",
    )
    preferred_travel = forms.MultipleChoiceField(
        choices=CustomUser._meta.get_field("preferred_travel").choices,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="旅遊偏好",
    )  
    
   



    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields["username"].disabled = False  # 讓使用者改帳號名稱
