from django import forms
from api.models import PollModel

class PollForm(forms.ModelForm):
    class Meta:
        model = PollModel
        fields = ['question', 'option_one', 'option_two', 'option_three']

