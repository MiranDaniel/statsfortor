from django import forms

class Search(forms.Form):
    relay = forms.CharField(label='Relay search', max_length=100)