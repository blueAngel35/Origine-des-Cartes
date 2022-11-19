#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 22:18:52 2022

@author: Genetix
"""
from PIL import Image
import requests

import pandas

# Params
lang = "fr"
maxH = 150
maxW = 150

# Noms de Fichiers en Entrée
fileNameImages = "asset/images/imagesDesMedias.tsv"

fileNameMaster = "data/origineDesCartes.tsv"
fileNameInfosCartes = "data/infosCartes.tsv"
fileNameCartesParExtensions="data/repartitionCarteExtensions.tsv"
fileNameNotes = "data/notes.txt"

fileNameStyleCartesParMedia = "asset/styleCartesParMedia.txt"
fileNameStyleMediasParExtensions = "asset/styleMediasParExtensions.txt"
fileNameAutriceLicence = "asset/autriceLicence.txt"

#Noms des Fichiers de Sortie
fileNameCarteParMediaHtml = "cartesParMedia.html"
fileNameMediaParExtensionHtml = "mediasParExtensions.html"

# Elements à ajouter aux HTML
print("Lecture CSS")
styleFileCarteParMedia = open(fileNameStyleCartesParMedia, 'r')
styleCarteParMedia = ""
for line in styleFileCarteParMedia:
    styleCarteParMedia+=line
styleFileCarteParMedia.close()

styleFileMediaParExtension = open(fileNameStyleMediasParExtensions, 'r')
styleMediaParExtension = ""
for line in styleFileMediaParExtension:
    styleMediaParExtension+=line
styleFileMediaParExtension.close()

print("Lecture Autrice")
autriceLicenceFile = open(fileNameAutriceLicence, 'r')
blocAutriceLicence = ""
for line in autriceLicenceFile:
    blocAutriceLicence+=line
autriceLicenceFile.close()

# Tableau Master
print("Lecture Tableau Master")
tableauMaster = pandas.read_csv(fileNameMaster, sep ="\t", index_col=0,
                                na_filter=True,keep_default_na=False,na_values="")

#tableauMaster = tableauMaster.replace(r'^Oui.+', "Oui", regex=True)
#tableauMaster = tableauMaster.replace("Oui", True)
tableauMaster = tableauMaster.fillna(False)

# Tableau Cartes par Extension
print("Lecture Tableau Cartes par Extension")
tableauCartesParExtension = pandas.read_csv(fileNameCartesParExtensions, sep ="\t", index_col=0,
                                na_filter=True,keep_default_na=False,na_values="")
tableauCartesParExtension = tableauCartesParExtension.fillna(False)

# Tableau Infos Cartes
print("Lecture Tableau Infos Cartes")
tableauInfosCartes = pandas.read_csv(fileNameInfosCartes, sep ="\t", index_col=0,na_filter=True,keep_default_na=False,na_values="")
tableauInfosCartes = tableauInfosCartes.fillna(False)

# Informations sur les cartes et personnages
print("Informations sur les cartes et personnages")
dictType = {}; dictPerso = {}; dictVaisseau = {};
for index, row in tableauInfosCartes.iterrows():
    Personnage = row['Personnage']
    Type = row['Type']
    Vaisseau = row['Vaisseau']
    Carte = index
    dictType[Carte]=Type
    dictPerso[Carte]=Personnage
    dictVaisseau[Carte]=Vaisseau
    
# Images des Medias
print("Lecture Tableau Images des Medias")
tableauImages = pandas.read_csv(fileNameImages, sep ="\t")
dictImages = {}
for index, row in tableauImages.iterrows():
    name = row['Media']
    url = row['Url de l’Image']
    dictImages[name]=url

# Lecture des Notes
print("Lecture des Notes")
dictNotes = {}
fileNotes = open(fileNameNotes, "r")
for ligne in fileNotes : 
    n = ligne.split(";")[0]
    note = ligne.split(";")[1].strip()
    dictNotes[n]=note
fileNotes.close()

# Avoir la balise image pour un media
def getImagesParMedia(media):
    html =  '<div><a>'+media+'</a>'
    if media in dictImages:
        urlImage = dictImages[media]
        html +=  '</br><img class="fit-picture" '
        with Image.open(requests.get(urlImage, stream=True).raw) as im:
            w = im.width ; h = im.height 
            if h>w:
                newH = maxH; newW = (newH*w) / h
            else:
                newW = maxW; newH = (newW*h) / w
            html += 'height='+str(newH)+' width='+str(newW)+' '
        html += 'src="'+urlImage+'" alt="'+media+'"></div>'
    return html    

# Avoir les pilotes d'un Media
def getPilotesParMedia(pilote):
    col = tableauMaster[pilote]
    return list(col[col != False].index)

def getMediaParPilote(pilote):
    row = tableauMaster.loc[pilote]
    return list(row[row != False].index)

def convNomCarte(nom, media):
    texte = ''
    if dictPerso[nom] != "n/a":
        texte += 'Personnage : '+simplifierNomPersonnage(nom)+'</br>'
    if dictType[nom]=="Pilote":
        texte += 'Type : Pilote ('+dictVaisseau[nom]+')</br>'
    elif dictType[nom]=="Titre":
        texte += 'Type : Titre ('+dictVaisseau[nom]+')</br>'
    else:
        texte += 'Type : '+dictType[nom]+'</br>'
    if getNote(nom, media)!="null":
        texte += 'Note : '+getNote(nom, media)+'</br>'
    
    html =  '<div class="tooltip">'+nom
    html += '<span class="tooltiptext">'+texte+'</span>'
    html += '</div>'
    return html

def simplifierNomPersonnage(nom):
    if dictPerso[nom] != "n/a":
        return dictPerso[nom]
    else:
        return nom

def getNote(nomCarte, media):
    val = tableauMaster.at[nomCarte, media]
    if 'Oui (' in val:
        return dictNotes[val.replace('Oui (','').replace(')','')]
    else:
        return "null"

# Tableau par media
print("Organisation des URL Medias")
dicoCarteParMedia= {}
for col in tableauMaster :
    dicoCarteParMedia[col] = getPilotesParMedia(col)
          
# Ecriture du Tableau par Media en HTML
print("Ecriture du Tableau par Media en HTML")
fileCarteParMediaHtml = open(fileNameCarteParMediaHtml, "w")
fileCarteParMediaHtml.write('<!DOCTYPE html><html lang="'+lang+'">'+styleCarteParMedia+'<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n')
fileCarteParMediaHtml.write('<table><tr><th>Media</th><th>Nombre de Cartes</th><th>Listes des Cartes</th></tr>\n')
 
i = 0
l = len(dicoCarteParMedia)
for media in dicoCarteParMedia:
    i=i+1
    print(str(i)+"/"+str(l))
    liste = dicoCarteParMedia[media]
    listeHtml = ''
    for nomCarte in liste:
        listeHtml += (convNomCarte(nomCarte, media))+", \n"
    listeHtml = listeHtml[:-4]
    listeHtml = listeHtml+"\n"
    image = getImagesParMedia(media)
    fileCarteParMediaHtml.write('<tr><th>'+image+'</th><th>'+str(len(liste))+'</th><td>'+listeHtml+'</td></tr>\n')
     
fileCarteParMediaHtml.write('</table></br>'+'\n')
fileCarteParMediaHtml.write(blocAutriceLicence)
fileCarteParMediaHtml.close()
print("Ecriture du Tableau par Media en HTML Fin")
 

# Tableau Medias par Extensions

# Avoir les pilotes d'une extension
def getPilotesParExtension(extension):
    col = tableauCartesParExtension[extension]
    return list(col[col != False].index)

def getExtensionsParPilote(extension):
    row = tableauCartesParExtension.loc[extension]
    return list(row[row != False].index)

dicoExtensions = {}
for extension in tableauCartesParExtension :
    listePilotes = getPilotesParExtension(extension)
    listeMediaTmp = []
    dicoMediaCartes = {}
    for pilote in listePilotes:
        listeMediaTmp = getMediaParPilote(pilote)
        for media in listeMediaTmp:
            if media not in dicoMediaCartes.keys() :
                dicoMediaCartes[media] = []  
            dicoMediaCartes[media].append(pilote)
                
    dicoExtensions[extension]=dicoMediaCartes
          
# Ecriture du Tableau Medias par Extensions en HTML
print("Ecriture du Tableau Medias par Extensions en HTML")
maxH = 150
maxW = 150
fileMediaParExtensionHtml = open(fileNameMediaParExtensionHtml, "w")
fileMediaParExtensionHtml.write('<!DOCTYPE html><html lang="'+lang+'">'+styleMediaParExtension)
fileMediaParExtensionHtml.write('<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>\n')
fileMediaParExtensionHtml.write('<table><tr><th>Extension</th><th>Listes des Medias</th></tr>\n')

def convertListePilotesForHtml(listePersonnages):
    html = 'Cartes : '
    for perso in listePersonnages:
        html+=perso+", "
    return html
    
def getImageMediaWithPilotList(media, listePersonnages):
    htmlImage='<div><a>'+media+'</a>'
    if media in dictImages:
        urlImage = dictImages[media]
        htmlImage +=  '</br><img class="fit-picture" '
        with Image.open(requests.get(urlImage, stream=True).raw) as im:
            w = im.width ; h = im.height 
            if h>w:
                newH = maxH; newW = (newH*w) / h
            else:
                newW = maxW; newH = (newW*h) / w
            htmlImage += 'height='+str(newH)+' width='+str(newW)+' '
        htmlImage += 'src="'+urlImage+'" alt="'+media+'"></div></div>'

    html =  '<div class="tooltip">'+htmlImage
    html += '<span class="tooltiptext">'+convertListePilotesForHtml(listePersonnages)+'</span>'
    html += '</div>'
    return htmlImage
    
i = 0
l = len(dicoExtensions)    
for extension in dicoExtensions:
    i=i+1
    print(str(i)+"/"+str(l))
    liste = dicoExtensions[extension]
    listeHtml = ''
    for media in liste:
        listePilotesTmp = dicoExtensions[extension][media]
        image = getImageMediaWithPilotList(media, listePilotesTmp)
        listeHtml += image#+", "
    #listeHtml = listeHtml.replace(",</br>",",")
    if len(listeHtml)>1:
        fileMediaParExtensionHtml.write('<tr><th>'+extension+'</th><td>'+listeHtml+'</td></tr>\n')
    
fileMediaParExtensionHtml.write('</table></br>'+'\n')
fileMediaParExtensionHtml.write(blocAutriceLicence)
fileMediaParExtensionHtml.close() 
print("Ecriture du Tableau Medias par Extensions en HTML fini")
