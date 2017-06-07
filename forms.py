from wtforms_alchemy import ModelForm
from app import Change


class ChangeForm(ModelForm):
    class Meta:
        include = ['cr', 'verified_hosts', 'verification_commands']
        exclude = ['before', 'after']
        model = Change
