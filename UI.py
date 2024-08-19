import tkinter.dialog
import tkinter.messagebox
from FiveM import FiveM
from Minecraft import Minecraft
from SCP import SCP

import tkinter
from tkinter import ttk

import threading
import csv
from os.path import exists

client_jeux = {"Minecraft":None,"SCP:SL":None,"FiveM":None}

BOUTON_PAR_LIGNE = 3

################## Main UI ##################################
class Onglets :
    def __init__(self,root):
        self.gestionnaire = ttk.Notebook(root)
        self.onglets_jeux = {}
        for jeu in client_jeux :
            self.onglets_jeux[jeu] = ttk.Frame(self.gestionnaire)
            self.gestionnaire.add(self.onglets_jeux[jeu],text=jeu)
        self.gestionnaire.pack()

class TemplateOnglet:
    def __init__(self,root,jeu):
        self.console = ttk.Frame(root,borderwidth=5,relief="sunken")
        self.remplir_console_frame(jeu)

        self.options = ttk.Frame(root)
        self.remplir_options_frame(jeu)



        self.options.pack(side=tkinter.LEFT)
        self.console.pack(side=tkinter.RIGHT)
    
    def remplir_console_frame(self,jeu):
        console = tkinter.Text(self.console,state=tkinter.DISABLED,background="black",foreground="white")
        console.tag_configure("center",justify="center")

        console.grid(row=0,column=0)

        client_jeux[jeu].CreerConsole(console)

        entree = ttk.Entry(self.console)
        entree.grid(row=1)

        bouton = ttk.Button(self.console,text="-- Valider --")
        bouton.grid(row=2)

    def remplir_options_frame(self,jeu):
        i = 0
        for option in client_jeux[jeu].options:
            bouton = ttk.Button(self.options,text=option,command=lambda option=option: threading.Thread(target=client_jeux[jeu].options[option]).start())
            bouton.grid(row=i // BOUTON_PAR_LIGNE,column=i % BOUTON_PAR_LIGNE)
            i += 1

class Main :
    def __init__(self):
        self.fenetre = tkinter.Tk()
        self.fenetre.title("Serveur de jeux")
        self.onglets = Onglets(self.fenetre)

        for jeu in client_jeux :
            TemplateOnglet(self.onglets.onglets_jeux[jeu],jeu)


        self.fenetre.mainloop()

################### Prompt info client #####################################

def tous_valide():
    complet = True
    for jeu in client_jeux :
        if not client_jeux[jeu]:
            complet = False
    return complet

class FormulaireAcces:
    def __init__(self,nom_jeu,root,n_colonne,entree_ip,tableau_colonne):
        self.jeu = nom_jeu
        self.colonne_frame = ttk.Frame(root)
        self.entree_ip = entree_ip

        self.tableau_colonne_jeu = tableau_colonne
        
        titre_colonne = ttk.Label(self.colonne_frame,text=nom_jeu)
        titre_colonne.grid(row=0)

        self.entrees = {}

        ligne = 1
        for info in ["Pseudo","Mot de passe"] :
            entree =  ttk.Entry(self.colonne_frame)
            entree.insert(tkinter.END,info)
            entree.grid(row=ligne)
            self.entrees[info] = entree

            ligne += 1

        self.bouton_valider = tkinter.Button(self.colonne_frame,text="Vérifier les informations",command=self.verifie_infos,bg="red")
        self.bouton_valider.grid(row=ligne)

        self.colonne_frame.grid(column=n_colonne,row=1)

    def verifie_infos(self):
        if self.jeu == "FiveM" :
            client = FiveM(self.entree_ip.get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get())
        elif self.jeu == "Minecraft" :
            client = Minecraft(self.entree_ip.get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get()) 
        elif self.jeu == "SCP:SL" :
            client = SCP(self.entree_ip.get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get())

        if client :
            self.bouton_valider.configure(bg="green",state=tkinter.DISABLED,text="OK")

            client_jeux[self.jeu] = client

            if tous_valide():
                reponse = tkinter.messagebox.askyesno("Enregistrer informations ?","Veux-tu enregistrer les infomations pour la prochaine fois ?")
                if reponse :
                    sauvegarde_infos(self.tableau_colonne_jeu,self.entree_ip.get())

                self.colonne_frame.master.destroy()

                tkinter.messagebox.showwarning("NE PAS FERMER LA FENETRE !","ATTENTION, pour que les serveurs fonctionnent il ne faut pas fermer la fenetre suivante. Fermes là quand tu n'as plus besoin des serveurs !")
                Main()

class FenetreInitialisation:
    def __init__(self):
        self.fenetre = tkinter.Tk()
        self.fenetre.title("Informations de connexion")
        
        entree_ip = ttk.Entry(self.fenetre)
        entree_ip.insert(tkinter.END,"IP")
        entree_ip.grid(row=0,column=1)

        self.colonnes = {}
        i = 0
        for jeu in client_jeux:
            self.colonnes[jeu] = FormulaireAcces(jeu,self.fenetre,i,entree_ip,self.colonnes)
            i += 1
        
        if exists("Infos_connexion.csv") and tkinter.messagebox.askyesno("Pré-remplir les informations ?","Veux-tu compléter directement avec les infos enregistrées ?") :
            ecrit_infos(self.colonnes)
        self.fenetre.mainloop()

def sauvegarde_infos(colonne_jeu,ip):
    fichier = open("Infos_connexion.csv",mode="w")

    cles = ["Jeu","Pseudo","Mot de passe","IP"]

    transcripteur = csv.DictWriter(fichier,cles)
    transcripteur.writeheader()

    infos_jeux = []
    for jeu in colonne_jeu :
        dico = {}
        dico["Jeu"] = jeu
        dico["IP"] = ip
        for info in cles :
            if info != "Jeu" and info != "IP" :
                dico[info] = colonne_jeu[jeu].entrees[info].get()
        infos_jeux.append(dico)
    transcripteur.writerows(infos_jeux)
    fichier.close()

def ecrit_infos(colonnes_jeux):
    fichier = open("Infos_connexion.csv",mode="r")
    liste_dico = list(csv.DictReader(fichier))
    for jeu in liste_dico :
        nom = jeu["Jeu"]
        colonnes_jeux[nom].entree_ip.delete(0,tkinter.END)
        colonnes_jeux[nom].entree_ip.insert(tkinter.END,jeu["IP"])
        for info in jeu :
            if info != "Jeu" and info != "IP" :
                colonnes_jeux[nom].entrees[info].delete(0,tkinter.END)
                colonnes_jeux[nom].entrees[info].insert(tkinter.END,jeu[info])
###################################################################
FenetreInitialisation()
