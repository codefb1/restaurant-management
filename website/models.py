from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
# Create your models here.




class Table(models.Model):
    

    numtab = models.IntegerField(null=True)

    def __str__(self):
        return str(self.numtab)





class Categorie(models.Model):
    nom_categorie = models.CharField(max_length=255)
    image_categorie = models.ImageField(null=True, blank=True)


    def __str__(self):
        return str(self.nom_categorie)



class Ingredient(models.Model):
    UNITE= (
           ('kg', 'kg'),
           ('L', 'L'),
           ('u', 'u'),
           )
    noming = models.CharField(max_length=255)

    unite = models.CharField(max_length=255, null=True, choices=UNITE)



    def __str__(self):
        return str(self.noming)

class Statut(models.Model):

    nomst = models.CharField(max_length=255,  null=True)


    def __str__(self):
        return str(self.nomst)

class Plat(models.Model):

    nom_plat = models.CharField(max_length=255)
    prix_plat = models.DecimalField(max_digits=7, decimal_places=2)
    categorie = models.ForeignKey(Categorie, null=True, on_delete=models.SET_NULL)
    statut = models.CharField(max_length=255, null=True)
    datecreation = models.DateTimeField(auto_now_add=True)
    imagplat = models.ImageField(null=True, blank=True)


    def __str__(self):
        return str(self.nom_plat)





class LigneIgredient(models.Model):
    plat = models.ForeignKey(Plat, null=True, on_delete=models.SET_NULL)
    ingredient = models.ForeignKey(Ingredient, null=True, on_delete=models.SET_NULL)
    qtip = models.FloatField(max_length=255)
    class meta:
        unique_together = [['plat', 'ingredient']]

    def __str__(self):
        return str(self.plat)




class Vente(models.Model):
    table = models.ForeignKey(Table, null=True, on_delete=models.SET_NULL)
    datev = models.DateField(auto_now_add=True)
    heur = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class LigneVente(models.Model):
    plat = models.ForeignKey(Plat, null=True, on_delete=models.SET_NULL)
    vente = models.ForeignKey(Vente, null=True, on_delete=models.SET_NULL)
    quantitev = models.FloatField(max_length=255)



    def __str__(self):
        return str(self.plat)

class Fournisseur(models.Model):
    nomf = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)



    def __str__(self):
        return str(self.nomf)



class Achat(models.Model):

    fournisseur = models.ForeignKey(Fournisseur, null=True, on_delete=models.SET_NULL)
    datachat = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return str(self.fournisseur)

class LigneAchat(models.Model):
    achat = models.ForeignKey(Achat, null=True, on_delete=models.SET_NULL)
    ingredient = models.ForeignKey(Ingredient, null=True, on_delete=models.SET_NULL)
    qtachat = models.FloatField(max_length=255)
    prixachat = models.FloatField(max_length=255)

    def __str__(self):
        return str(self.ingredient)


class Inventaire(models.Model):
    ingredient = models.ForeignKey(Ingredient, null=True, on_delete=models.SET_NULL)
    unite = models.CharField(max_length=255)
    achat = models.FloatField(max_length=255)
    vente = models.FloatField(max_length=255)
    resultat = models.FloatField(max_length=255)

    def __str__(self):
        return str(self.ingredient)
