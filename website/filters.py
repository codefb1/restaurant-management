import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Vente
        fields = '__all__'

class AchatFilter(django_filters.FilterSet):
    class Meta:
        model = Achat
        fields = '__all__'
class IngredientFilter(django_filters.FilterSet):
    class Meta:
        model = Ingredient
        fields = '__all__'
class PlatFilter(django_filters.FilterSet):
    class Meta:
        model = Plat
        fields = ['nom_plat','prix_plat','categorie','statut']

class FournisseurFilter(django_filters.FilterSet):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class CategorieFilter(django_filters.FilterSet):
    class Meta:
        model = Categorie
        fields = ['nom_categorie']
