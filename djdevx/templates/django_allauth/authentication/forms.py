from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ReauthenticateForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
    UserTokenForm,
)

form_classes_list = [
    "block",
    "w-full",
    "rounded-md",
    "border-0",
    "py-1.5",
    "shadow-sm",
    "ring-1",
    "ring-inset",
    "ring-gray-300",
    "sm:text-sm",
    "sm:leading-6",
    "focus:ring-2",
    "focus:ring-inset",
    "focus:ring-blue-500",
    "outline-none",
    "focus:outline-none",
    "placeholder:text-gray-500",
    "dark:placeholder:text-gray-500",
    "my-2",
    "px-2",
    "text-gray-700",
    "dark:text-gray-700",
]

form_classes = " ".join(form_classes_list)


class AuthAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super(AuthAddEmailForm, self).__init__(*args, **kwargs)
        email_field = self.fields["email"]
        email_field.widget.attrs.update({"class": form_classes, "style": ""})


class AuthChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({"class": form_classes, "style": ""})
            field.help_text = ""


class AuthLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(AuthLoginForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({"class": form_classes, "style": ""})
            field.help_text = ""


class AuthReauthenticateForm(ReauthenticateForm):
    def __init__(self, *args, **kwargs):
        super(AuthReauthenticateForm, self).__init__(*args, **kwargs)
        password_field = self.fields["password"]
        password_field.widget.attrs.update({"class": form_classes, "style": ""})


class AuthResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(AuthResetPasswordForm, self).__init__(*args, **kwargs)
        email = self.fields["email"]
        email.widget.attrs.update({"class": form_classes, "style": ""})


class AuthResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(AuthResetPasswordKeyForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({"class": form_classes, "style": ""})


class AuthSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(AuthSignupForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({"class": form_classes, "style": ""})
            field.help_text = ""


class AuthUserTokenForm(UserTokenForm):
    def __init__(self, *args, **kwargs):
        super(AuthUserTokenForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": form_classes,
                    "style": "",
                }
            )
