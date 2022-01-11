from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from .forms import *
from django.forms import inlineformset_factory
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.forms import modelformset_factory
from django.db import transaction, IntegrityError

import pandas as pd
import numpy as np
from .filters import *
from django.http import JsonResponse
import json
from .decorators import *


# index views .


@login_required(login_url='defaultlogin')
def index(request):
    #topclient = Vente.objects.raw('SELECT 1 id, website_client.nomcl, website_vente.datev, COUNT(website_vente.client_id) as somme FROM website_client, website_vente WHERE website_client.id=website_vente.client_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW() group by client_id ORDER BY somme  DESC LIMIT 1')
    topplat = LigneVente.objects.raw('SELECT 1 id, website_plat.id, website_plat.nom_plat, website_vente.datev ,sum(website_lignevente.quantitev) as total FROM website_plat, website_vente, website_lignevente WHERE website_plat.id=website_lignevente.plat_id and website_vente.id=website_lignevente.vente_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW() group by website_plat.id ORDER BY total  DESC LIMIT 1')
    nbcomande = Vente.objects.raw('SELECT 1 id, COUNT(id) as nbcmd FROM website_vente WHERE website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW()')
    revenu = LigneVente.objects.raw('SELECT 1 id, SUM(website_lignevente.quantitev * website_plat.prix_plat) as totalc, website_vente.datev from website_plat, website_vente, website_lignevente WHERE website_plat.id=website_lignevente.plat_id and website_vente.id=website_lignevente.vente_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW()')
    recentcmd = Vente.objects.raw('SELECT 1 id, website_table.numtab, sum(website_lignevente.quantitev * website_plat.prix_plat) as total , website_vente.datev, website_vente.heur from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_vente.id=website_lignevente.vente_id and website_plat.id=website_lignevente.plat_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 90 DAY) AND NOW() GROUP by website_vente.id ORDER BY `website_vente`.`datev` DESC LIMIT 10')
    top4pl = Plat.objects.raw('SELECT 1 id, website_plat.nom_plat, website_plat.prix_plat, website_plat.imagplat, sum(website_lignevente.quantitev * website_plat.prix_plat) as total, sum(website_lignevente.quantitev) as nombre  from website_plat, website_lignevente WHERE  website_plat.id=website_lignevente.plat_id GROUP by website_plat.id ORDER BY `total`  DESC LIMIT 4')

    prevision = Plat.objects.raw('SELECT 1 id, dat, total, (AVG(total) OVER (ORDER BY dat ROWS BETWEEN 1 PRECEDING AND 0 FOLLOWING)) as mb from (select website_vente.datev as dat ,sum(website_lignevente.quantitev * website_plat.prix_plat) as total from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_vente.id=website_lignevente.vente_id and website_plat.id=website_lignevente.plat_id GROUP by website_vente.datev) a')

    queryset = Vente.objects.raw('SELECT 1 id, dat, total, (AVG(total) OVER (ORDER BY dat ROWS BETWEEN 1 PRECEDING AND 0 FOLLOWING)) as mb from (select website_vente.datev as dat ,sum(website_lignevente.quantitev * website_plat.prix_plat) as total from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_vente.id=website_lignevente.vente_id and website_plat.id=website_lignevente.plat_id GROUP by website_vente.datev) a')
    dat = list()
    total = list()
    mb = list()

    for entry in queryset:
        dat.append('%s day' % entry.dat)
        total.append(entry.total)
        mb.append(entry.mb)



    context = { 'dat': json.dumps(dat), 'total': json.dumps(total), 'mb': json.dumps(mb),  'recentcmd':recentcmd, 'top4pl':top4pl, 'topplat':topplat, 'nbcomande':nbcomande, 'revenu':revenu}
    return render(request, 'index.html',context)


def prevision_chart(request):
    labels = []
    data = []

    queryset = Vente.objects.raw('SELECT 1 id, dat, total, (AVG(total) OVER (ORDER BY dat ROWS BETWEEN 1 PRECEDING AND 0 FOLLOWING)) as mb from (select website_vente.datev as dat ,sum(website_lignevente.quantitev * website_plat.prix_plat) as total from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_vente.id=website_lignevente.vente_id and website_plat.id=website_lignevente.plat_id GROUP by website_vente.datev) a')
    for entry in queryset:
        labels.append(entry.dat)
        data.append(entry.mb)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

# cataloge de produit views .





#**************************plats*****************************


# ajouter un plats  views .
@login_required(login_url='defaultlogin')
def create(request):

    ingredientFormset = modelformset_factory(LigneIgredient, form=IngpltForm)
    form = PlatForm(request.POST or None, request.FILES)
    formset = ingredientFormset(request.POST or None, queryset= LigneIgredient.objects.none(), prefix='ingredients')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    plat = form.save(commit=False)
                    plat.save()

                    for ingre in formset:
                        data = ingre.save(commit=False)
                        data.plat = plat
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('productlist')
    context = {}
    plats = Plat.objects.all()
    filter = PlatFilter(request.GET, queryset=plats)
    plats = filter.qs
    return render(request, 'addproduct.html', {'form':form, 'formset':formset, 'plats':plats, 'filter':filter})

def updatep(request, pk):
    pl = Plat.objects.get(id=pk)
    ing = LigneIgredient.objects.filter(plat=pk)
    ingredientFormset = modelformset_factory(LigneIgredient, form=IngpltForm,)
    form = PlatForm(instance=pl)
    formset = ingredientFormset(request.POST or None, queryset= LigneIgredient.objects.filter(plat=pk), prefix='ingredients')
    if request.method == "POST":
        form = PlatForm(request.POST or None, request.FILES, instance=pl)
        formset = ingredientFormset(request.POST or None, queryset= LigneIgredient.objects.filter(plat=pk), prefix='ingredients')
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    plat = form.save(commit=False)
                    plat.save()

                    for ingre in formset:
                        data = ingre.save(commit=False)
                        data.plat = plat
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('productlist')
    context = {}
    plats = Plat.objects.all()

    filter = PlatFilter(request.GET, queryset=plats)
    plats = filter.qs
    return render(request, 'addproduct.html', {'form':form, 'formset':formset, 'plats':plats, 'filter':filter})


def deleteplat(request, pk):

    plat = Plat.objects.get(id=pk)
    ingre = LigneIgredient.objects.filter(plat=pk)
    if request.method == "POST":
        ingre.delete()
        plat.delete()

        return redirect('addproduct')


    context={}
    return render(request, 'deleteplat.html',{'plat':plat, 'ingre':ingre})
def updateplat(request, pk):

    plat= Plat.objects.get(id=pk)
    form = PlatForm(instance=plat)
    if request.method == 'POST':
        form = PlatForm(request.POST, instance=plat)
        if form.is_valid():
            form.save()
            return redirect('addproduct')
    context = {'form':form}
    return render(request, 'updateplat.html', context)


    context={}
    return render(request, 'updateplat.html',{'plat':plat})
def cout(request):
    ingredient = Ingredient.objects.all()
    ligne = LigneIgredient.objects.all()
    plat = Plat.objects.all()

    context={}
    return render(request, 'productlist.html',{'plat':plat})


# liste de produits views .
@login_required(login_url='defaultlogin')
def productlist(request):
    plats = Plat.objects.all()
    context={}
    return render(request, 'productlist.html',{'plats':plats})


# grid de produits  views .
@login_required(login_url='defaultlogin')
def productgrid(request, pk):
    pk = pk
    categori = Categorie.objects.filter(id=pk)
    plat = Plat.objects.filter(categorie=pk)
    context = {'categori':categori, 'plat':plat}



    return render(request, 'productgrid.html', context)





#************************commandes************************
 # commande views .
@login_required(login_url='defaultlogin')
def orders(request):
    venteFormset = modelformset_factory(LigneVente, form=LigneVenteForm)
    form = OrderForm(request.POST or None, request.FILES)
    formset = venteFormset(request.POST or None, queryset= LigneVente.objects.none(), prefix='ventes')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    vente = form.save(commit=False)
                    vente.save()
                    for vnt in formset:
                        data = vnt.save(commit=False)
                        data.vente = vente
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('orders')
    #vt = LigneVente.objects.raw('select website_vente.id, numtab, datev, heur, nom_plat, quantitev from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_plat.id=website_lignevente.plat_id and website_vente.id=website_lignevente.vente_id ')
    vt = Vente.objects.all()
    filter = OrderFilter(request.GET, queryset=vt)
    vt = filter.qs
    #filter = OrderFilter()
    #tablevente = vt.objects.raw('select 1 id nomcl, datev, heur, nom_plat, quantitev from vt group by nomcl')

    context = {'vt':vt, 'form':form, 'formset':formset, 'filter':filter}
    return render(request, 'orders.html',context)


def addorder(request):

    ven = Vente.objects.all()
    myfilter = OrderFilter(request.GET, queryset=Vente.objects.all())
    ven = myfilter.qs
    context = {'ven':ven, 'myfilter':myfilter}
    return render(request, 'addorder.html', context)


def updateorder(request, pk):
    commande = Vente.objects.get(id=pk)
    lignecommande = LigneVente.objects.filter(vente=pk)
    venteFormset = modelformset_factory(LigneVente, form=LigneVenteForm)
    form = OrderForm(instance=commande)
    formset = venteFormset(request.POST or None, queryset= LigneVente.objects.filter(vente=pk), prefix='ventes')
    if request.method == "POST":


        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    vente = form.save(commit=False)
                    vente.save()
                    for vnt in formset:
                        data = vnt.save(commit=False)
                        data.vente = vente
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('orders')
    #vt = LigneVente.objects.raw('select website_vente.id, numtab, datev, heur, nom_plat, quantitev from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_plat.id=website_lignevente.plat_id and website_vente.id=website_lignevente.vente_id ')
    vt = Vente.objects.all()
    filter = OrderFilter(request.GET, queryset=vt)
    vt = filter.qs
    #filter = OrderFilter()
    #tablevente = vt.objects.raw('select 1 id nomcl, datev, heur, nom_plat, quantitev from vt group by nomcl')

    context = {'vt':vt, 'form':form, 'formset':formset, 'filter':filter}
    return render(request, 'orders.html',context)


def deleteorder(request, pk):
	orde = Vente.objects.get(id=pk)
	if request.method == "POST":
		orde.delete()
		return redirect('orders')

	context = {'item':orde}
	return render(request, 'deleteorder.html', context)

def detailcommande(request, pk):
    pk = pk
    vente = Vente.objects.filter(id=pk)
    plat = LigneVente.objects.filter(vente=pk)
    context = {'vente':vente, 'plat':plat}



    return render(request, 'detailcommande.html', context)


#*********************************table*******************************

# liste des clients  views .
@login_required(login_url='defaultlogin')
def tablelist(request):
    form = TableForm()
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tablelist')
    table = Table.objects.all()
    context = {'table':table, 'form':form}
    return render(request, 'tablelist.html', context)


def addtable(request):

    form = TableForm()
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tablelist')

    contex = {'form':form}
    return render(request, 'addtable.html', contex)

def updatetable(request, pk):

	custom = Table.objects.get(id=pk)
	form = TableForm(instance=custom)

	if request.method == 'POST':
		form = TableForm(request.POST, instance=custom)
		if form.is_valid():
			form.save()
			return redirect('tablelist')

	context = {'form':form}
	return render(request, 'addtable.html', context)

#delete a cutomer
def deletetable(request, pk):
	tab = Table.objects.get(id=pk)
	if request.method == "POST":
		tab.delete()
		return redirect('tablelist')

	context = {'item':tab}
	return render(request, 'deletable.html', context)








#*************************tables**************************

# liste de table basic views .
@login_required(login_url='defaultlogin')
def basictables(request):
    return render(request, 'basic-tables.html',{})



# liste de table de données  views .
@login_required(login_url='defaultlogin')
def datatables(request):
    plats = Plat.objects.all()
    return render(request, 'data-tables.html', {'plats':plats})


#***************------------------users----------------************
# le profil de user views .

def userprofile(request):
    user = User.objects.all()

    context = {'user':user}


    return render(request, 'user-profile.html',context)




# le profil de user views .
@login_required(login_url='defaultlogin')
def adduser(request):
    userr = User.objects.all()
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(request, 'compte ajouter pour ' + user)


    context = {'form':form, 'userr':userr}
    return render(request, 'form-layout.html', context)
@login_required(login_url='defaultlogin')
def updatuser(request,pk):
    userr = User.objects.all()
    use = User.objects.get(id=pk)
    form = CreateUserForm(instance=use)

    if request.method == 'POST':
        form = CreateUserForm(request.POST, instance=use)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(request, 'compte modifier pour  ' + user)


    context = {'form':form, 'userr':userr}
    return render(request, 'form-layout.html', context)
def deleteuser(request, pk):
	use = User.objects.get(id=pk)

	if request.method == "POST":
		use.delete()
		return redirect('adduser')

	context = {'use':use}
	return render(request, 'deleteuser.html', context)


# login page views .


def defaultlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
    context = {}
    return render(request, 'default-login.html', context)



def LogOutUser(request):
    return redirect('defaultlogin')



@login_required(login_url='defaultlogin')
def lock(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')

    context = {}
    return render(request, 'lock-screen.html', context)





#------------categories-------------------------


@login_required(login_url='defaultlogin')
def productcata(request):

    categori = Categorie.objects.all()





    return render(request, 'productcata.html',{'categori':categori})

def Delete(request, pk):
	cat = Categorie.objects.get(id=pk)
	if request.method == "POST":
		cat.delete()
		return redirect('productcata')

	context = {'item':cat}
	return render(request, 'supcat.html', context)


def AddCat(request):
    form = CategoriForm()
    if request.method == 'POST':
        form = CategoriForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productcata')

    contex = {'form':form}
    return render(request, "addcat.html", contex)

def updatecat(request, pk):

	catego = Categorie.objects.get(id=pk)
	form = CategoriForm(instance=catego)

	if request.method == 'POST':
		form = CategoriForm(request.POST, instance=catego)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'addcat.html', context)

#***********************inventaire*****************************
def inventaire(request):

    invetry = Achat.objects.raw('select 1 id, nom ,uni, achat_totale,vent_totale, achat_totale-vent_totale as reste from (SELECT DISTINCT website_ingredient.id ,website_ingredient.noming as nom ,website_ingredient.unite as uni, sum(website_ligneachat.qtachat) as achat_totale from website_ingredient ,website_ligneachat WHERE website_ingredient.id=website_ligneachat.ingredient_id group by website_ingredient.id) a LEFT JOIN (select website_ligneigredient.ingredient_id ,sum(website_lignevente.quantitev*website_ligneigredient.qtip) as vent_totale FROM website_lignevente, website_ligneigredient WHERE website_lignevente.plat_id=website_ligneigredient.plat_id group by website_ligneigredient.ingredient_id) v on a.id= v.ingredient_id')



    context= {'invetry':invetry}
    return render(request, 'inventaire.html',context)

def inventaire1m(request):

    invetry = Achat.objects.raw('select 1 id, nom ,uni, achat_totale,vent_totale, achat_totale-vent_totale as reste from (SELECT DISTINCT website_ingredient.id ,website_ingredient.noming as nom ,website_ingredient.unite as uni, sum(website_ligneachat.qtachat) as achat_totale from website_ingredient , website_ligneachat , website_achat WHERE website_ingredient.id=website_ligneachat.ingredient_id and website_achat.id=website_ligneachat.achat_id and website_achat.datachat BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW() group by website_ingredient.id) a LEFT JOIN (select website_ligneigredient.ingredient_id ,sum(website_lignevente.quantitev*website_ligneigredient.qtip) as vent_totale FROM website_lignevente, website_ligneigredient, website_vente WHERE website_lignevente.plat_id=website_ligneigredient.plat_id and website_vente.id=website_lignevente.vente_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW() group by website_ligneigredient.ingredient_id) v on a.id= v.ingredient_id')



    context= {'invetry':invetry}
    return render(request, 'inventaire1m.html',context)
def inventaire3m(request):

    invetry = Achat.objects.raw('select 1 id, nom ,uni, achat_totale,vent_totale, achat_totale-vent_totale as reste from (SELECT DISTINCT website_ingredient.id ,website_ingredient.noming as nom ,website_ingredient.unite as uni, sum(website_ligneachat.qtachat) as achat_totale from website_ingredient , website_ligneachat , website_achat WHERE website_ingredient.id=website_ligneachat.ingredient_id and website_achat.id=website_ligneachat.achat_id and website_achat.datachat BETWEEN DATE_SUB(NOW(), INTERVAL 90 DAY) AND NOW() group by website_ingredient.id) a LEFT JOIN (select website_ligneigredient.ingredient_id ,sum(website_lignevente.quantitev*website_ligneigredient.qtip) as vent_totale FROM website_lignevente, website_ligneigredient, website_vente WHERE website_lignevente.plat_id=website_ligneigredient.plat_id and website_vente.id=website_lignevente.vente_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 90 DAY) AND NOW() group by website_ligneigredient.ingredient_id) v on a.id= v.ingredient_id')



    context= {'invetry':invetry}
    return render(request, 'inventaire3m.html',context)
def inventaire6m(request):

    invetry = Achat.objects.raw('select 1 id, nom ,uni, achat_totale,vent_totale, achat_totale-vent_totale as reste from (SELECT DISTINCT website_ingredient.id ,website_ingredient.noming as nom ,website_ingredient.unite as uni, sum(website_ligneachat.qtachat) as achat_totale from website_ingredient , website_ligneachat , website_achat WHERE website_ingredient.id=website_ligneachat.ingredient_id and website_achat.id=website_ligneachat.achat_id and website_achat.datachat BETWEEN DATE_SUB(NOW(), INTERVAL 180 DAY) AND NOW() group by website_ingredient.id) a LEFT JOIN (select website_ligneigredient.ingredient_id ,sum(website_lignevente.quantitev*website_ligneigredient.qtip) as vent_totale FROM website_lignevente, website_ligneigredient, website_vente WHERE website_lignevente.plat_id=website_ligneigredient.plat_id and website_vente.id=website_lignevente.vente_id and website_vente.datev BETWEEN DATE_SUB(NOW(), INTERVAL 180 DAY) AND NOW() group by website_ligneigredient.ingredient_id) v on a.id= v.ingredient_id')



    context= {'invetry':invetry}
    return render(request, 'inventaire6m.html',context)
#***********achat***************

def achat(request):
    achatformset = modelformset_factory(LigneAchat, form=LigneAchatForm)
    form = AchatForm(request.POST or None, request.FILES)
    formset = achatformset(request.POST or None, queryset= LigneAchat.objects.none(), prefix='achats')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    achat = form.save(commit=False)
                    achat.save()

                    for acht in formset:
                        data = acht.save(commit=False)
                        data.achat = achat
                        data.save()
            except IntegrityError:
                print("error encountered")

                return redirect('achat')
    acha = Achat.objects.all()
    filter = AchatFilter(request.GET, queryset=acha)
    acha = filter.qs
    #achat = LigneVente.objects.raw('SELECT website_achat.id, noming, datachat, nomf, prixachat, qtachat from website_ingredient, website_achat, website_fournisseur WHERE website_ingredient.id=website_achat.ingredient_id AND website_fournisseur.id=website_achat.fournisseur_id')
    context = {'filter':filter, 'acha':acha, 'form':form, 'formset':formset}


    return render(request, 'achat.html', context)


def addachat(request):
    achatformset = modelformset_factory(LigneAchat, form=LigneAchatForm)
    form = AchatForm(request.POST or None, request.FILES)
    formset = achatformset(request.POST or None, queryset= LigneAchat.objects.none(), prefix='achats')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    achat = form.save(commit=False)
                    achat.save()

                    for acht in formset:
                        data = acht.save(commit=False)
                        data.achat = achat
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('achat')
    context = {}
    return render(request, 'addachat.html', {'form':form, 'formset':formset})



def deletachat(request, pk):
	achat = Achat.objects.get(id=pk)
	if request.method == "POST":
		achat.delete()
		return redirect('achat')

	context = {'achat':achat}
	return render(request, 'deletachat.html', context)
def updatachat(request, pk):

    achat = Achat.objects.get(id=pk)
    ligneachat = LigneAchat.objects.filter(achat=pk)
    achatformset = modelformset_factory(LigneAchat, form=LigneAchatForm)
    form = AchatForm(instance=achat)
    formset = achatformset(request.POST or None, queryset= LigneAchat.objects.filter(achat=pk), prefix='achats')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    achat = form.save(commit=False)
                    achat.save()

                    for acht in formset:
                        data = acht.save(commit=False)
                        data.achat = achat
                        data.save()
            except IntegrityError:
                print("error encountered")

                return redirect('achat')
    acha = Achat.objects.all()
    filter = AchatFilter(request.GET, queryset=acha)
    acha = filter.qs
    #achat = LigneVente.objects.raw('SELECT website_achat.id, noming, datachat, nomf, prixachat, qtachat from website_ingredient, website_achat, website_fournisseur WHERE website_ingredient.id=website_achat.ingredient_id AND website_fournisseur.id=website_achat.fournisseur_id')
    context = {'filter':filter, 'acha':acha, 'form':form, 'formset':formset}


    return render(request, 'achat.html', context)
def detailachat(request, pk):
    pk = pk
    commande = Achat.objects.filter(id=pk)
    ingredient = LigneAchat.objects.filter(achat=pk)
    context = {'commande':commande, 'ingredient':ingredient}



    return render(request, 'detailachat.html', context)
def cc(request, pk):
    ac = Achat.objects.get(id=pk)
    #b = LigneAchat.objects.get(achat_id=pk)
    achatformset = modelformset_factory(LigneAchat, form=LigneAchatForm)
    form = AchatForm(request.POST or None, request.FILES, instance=ac)
    #query = LigneAchat.objects.filter(achat=pk)
    formset = achatformset(request.POST or None, queryset= LigneAchat.objects.filter(achat_id=pk), prefix='achats')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    achat = form.save(commit=False)
                    achat.save()

                    for acht in formset:
                        data = acht.save(commit=False)
                        data.achat = achat
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('achat')
    context = {'form':form, 'formset':formset}
    return render(request, 'addachat.html')

#***************fournisseur*************

def addfournisseur(request):
    form = FournisseurForm()
    if request.method == 'POST':
        form = FournisseurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('achat')

    context = {'form':form}


    return render(request, 'addfournisseur.html',context)

def fournisseur(request):
    fournisseur = Fournisseur.objects.all()
    context = {'fournisseur':fournisseur}


    return render(request, 'fournisseur.html',context)


def deletfournisseur(request, pk):
	fourni = Fournisseur.objects.get(id=pk)
	if request.method == "POST":
		fourni.delete()
		return redirect('fournisseur')

	context = {'fourni':fourni}
	return render(request, 'deletfournisseur.html', context)


def updatefournisseur(request, pk):

	fourni = Fournisseur.objects.get(id=pk)
	form = FournisseurForm(instance=fourni)

	if request.method == 'POST':
		form = FournisseurForm(request.POST, instance=fourni)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'addfournisseur.html', context)

#*********************************ingredient***************************
def adding(request):
    ingredient = Ingredient.objects.all()

    context = {'ingredient':ingredient}
    return render(request, 'inglist.html', context)
def inglist(request):
    form = IngredientForm()
    if request.method == 'POST':
        form = IngredientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inglist')
    ingredient = Ingredient.objects.all()
    context = {'form':form, 'ingredient':ingredient}


    return render(request, 'inglist.html',context)
def updating(request, pk):
    ingre = Ingredient.objects.get(id=pk)
    form = IngredientForm(instance=ingre)
    if request.method == 'POST':
        form = IngredientForm(request.POST, request.FILES, instance=ingre)
        if form.is_valid():
            form.save()
            return redirect('inglist')

    context = {'form':form}


    return render(request, 'adding.html',context)
def delting(request, pk):
	ingre = Ingredient.objects.get(id=pk)
	if request.method == "POST":
		fourni.delete()
		return redirect('inglist')

	context = {'ingre':ingre}
	return render(request, 'delting.html', context)


def menu(request):
    catego = Categorie.objects.all()
    plat = Plat.objects.all()
    context = {'catego':catego, 'plat':plat}
    return render(request, 'menupers.html', context)

def listeplat(request, pk):
    pk = pk
    categori = Categorie.objects.filter(id=pk)
    plat = Plat.objects.filter(categorie=pk)
    ingre = LigneIgredient.objects.filter(plat_id=plat)
    context = {'categori':categori, 'plat':plat, 'ingre':ingre}

    return render(request, 'listeplat.html', context)

def menuing(request, pk):
    pk = pk
    plat = Plat.objects.filter(id=pk)
    ingre = LigneIgredient.objects.filter(plat=pk)
    context = {'plat':plat, 'ingre':ingre}

    return render(request, 'menuing.html', context)

def commander(request):
    venteFormset = modelformset_factory(LigneVente, form=LigneVenteForm)
    form = OrderForm(request.POST or None, request.FILES)
    formset = venteFormset(request.POST or None, queryset= LigneVente.objects.none(), prefix='ventes')
    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    vente = form.save(commit=False)
                    vente.save()

                    for vnt in formset:
                        data = vnt.save(commit=False)
                        data.vente = vente
                        data.save()
            except IntegrityError:
                print("error encountered")
            return redirect('menu')

    #vt = LigneVente.objects.raw('select website_vente.id, numtab, datev, heur, nom_plat, quantitev from website_table, website_vente, website_plat, website_lignevente WHERE website_table.id=website_vente.table_id and website_plat.id=website_lignevente.plat_id and website_vente.id=website_lignevente.vente_id ')

    #tablevente = vt.objects.raw('select 1 id nomcl, datev, heur, nom_plat, quantitev from vt group by nomcl')



    context = { 'form':form, 'formset':formset}

    return render(request, 'commander.html', context)
def cuisine(request):

    commande = Vente.objects.raw('SELECT * FROM website_vente ORDER BY website_vente.datev DESC')
    context = {'commande':commande}

    return render(request, 'cuisine.html', context)

def cmdetail(request, pk):
    pk = pk
    commande = Vente.objects.filter(id=pk)
    plat = LigneVente.objects.filter(vente=pk)
    context = {'commande':commande, 'plat':plat}



    return render(request, 'cmdetail.html', context)

def detailplat(request, pk):
    pk = pk
    pla = Plat.objects.filter(id=pk)
    ingredient = LigneIgredient.objects.filter(plat=pk)
    context = {'pla':pla, 'ingredient':ingredient}
    return render(request, 'detailplat.html', context)
