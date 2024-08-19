from FiveM import FiveM
from Minecraft import Minecraft
from SCP import SCP

import tkinter
from tkinter import ttk

import threading

client_jeux = {"FiveM":FiveM("192.168.1.39","FiveM","1090")}

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
        self.console = ttk.Frame(root)
        self.remplir_console_frame(jeu)

        self.options = ttk.Frame(root)
        self.remplir_options_frame(jeu)



        self.options.pack(side=tkinter.LEFT)
        self.console.pack(side=tkinter.RIGHT)
    
    def remplir_console_frame(self,jeu):
        console = tkinter.StringVar(self.console)
        texte = ttk.Label(self.console,textvariable=console)
        texte.grid(row=0)

        target=client_jeux[jeu].CreerConsole(console)

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
    def __init__(self,nom_jeu,root,n_colonne,entree_ip):
        self.jeu = nom_jeu
        self.colonne_frame = ttk.Frame(root)
        self.entree_ip = entree_ip
        
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
                self.colonne_frame.master.destroy()
                Main()

class FenetreInitialisation:
    def __init__(self):
        self.fenetre = tkinter.Tk()
        
        entree_ip = ttk.Entry(self.fenetre)
        entree_ip.insert(tkinter.END,"IP")
        entree_ip.grid(row=0,column=1)

        self.colonnes = {}
        i = 0
        for jeu in client_jeux:
            self.colonnes[jeu] = FormulaireAcces(jeu,self.fenetre,i,entree_ip)
            i += 1
        self.fenetre.mainloop()

###################################################################
#FenetreInitialisation()
Main()