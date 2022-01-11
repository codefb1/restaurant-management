from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Plat
from django.forms.models import inlineformset_factory
from django.forms import ModelForm





class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']


class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = '__all__'



class IngpltForm(ModelForm):
    class Meta:
        model = LigneIgredient
        fields = ['ingredient', 'qtip']

        widgets = {
			'ingredient': forms.Select(attrs={'class': 'formset-field'}),
			'qtip': forms.TextInput(attrs={'class': 'formset-field'})

		}

class CategoriForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = '__all__'


class TableForm(ModelForm):
    class Meta:
        model = Table
        fields = '__all__'
class OrderForm(ModelForm):
    class Meta:
        model = Vente
        fields = '__all__'
class LigneVenteForm(ModelForm):
    class Meta:
        model = LigneVente
        fields = ['plat', 'quantitev']

        widgets = {
			'plat': forms.Select(attrs={'class': 'formset-field'}),
			'quantitev': forms.TextInput(attrs={'class': 'formset-field'})

		}


class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = '__all__'
class LigneAchatForm(ModelForm):
    class Meta:
        model = LigneAchat
        fields = ['ingredient', 'qtachat', 'prixachat']

        widgets = {
			'ingredient': forms.Select(attrs={'class': 'formset-field'}),
			'qtachat': forms.TextInput(attrs={'class': 'formset-field'}),
            'prixachat': forms.TextInput(attrs={'class': 'formset-field'})

		}



class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = '__all__'
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'
