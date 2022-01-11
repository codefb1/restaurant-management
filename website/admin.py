from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Table)
admin.site.register(Categorie)
admin.site.register(Ingredient)
admin.site.register(LigneIgredient)
admin.site.register(Statut)
admin.site.register(Plat)
admin.site.register(Vente)
admin.site.register(LigneVente)
admin.site.register(Fournisseur)
admin.site.register(Achat)
admin.site.register(LigneAchat)
