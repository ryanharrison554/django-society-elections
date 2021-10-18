from django import forms

from ..validators import email_user_validator

class VoterForm(forms.Form):
    """Form to validate voter information"""

    email = forms.EmailField(
        help_text="Your email will not be stored in a plaintext format. Instead"
        " it will be stored in a non-reversible way that will allow us to "
        "validate whether or not you have already voted.",
        error_messages="You did not enter a valid email address",
        validators=[email_user_validator]
    )