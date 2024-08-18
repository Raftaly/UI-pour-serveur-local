import tkinter.dialog
from FiveM import FiveM
from Minecraft import Minecraft
from SCP import SCP

import tkinter
from tkinter import ttk

class FormulaireAcces:
    def __init__(self,nom_jeu,root,n_colonne):
        self.jeu = nom_jeu
        self.colonne_frame = ttk.Frame(root)
        
        titre_colonne = ttk.Label(self.colonne_frame,text=nom_jeu)
        titre_colonne.grid(row=0)

        self.entrees = {}

        ligne = 1
        for info in ["Pseudo","IP","Mot de passe"] :
            entree =  ttk.Entry(self.colonne_frame)
            entree.insert(tkinter.END,info)
            entree.grid(row=ligne)
            self.entrees[info] = entree

            ligne += 1

        self.bouton_valider = tkinter.Button(self.colonne_frame,text="Vérifier les informations",command=self.verifie_infos,bg="red")
        self.bouton_valider.grid(row=ligne)

        self.colonne_frame.grid(column=n_colonne,row=0)

    def verifie_infos(self):
        try :
            if self.jeu == "FiveM" :
                client = FiveM(self.entrees["IP"].get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get())
            elif self.jeu == "Minecraft" :
                client = Minecraft(self.entrees["IP"].get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get()) 
            elif self.jeu == "SCP:SL" :
                client = SCP(self.entrees["IP"].get(),self.entrees["Pseudo"].get(),self.entrees["Mot de passe"].get())
            self.bouton_valider.state(tkinter.DISABLED)
            self.bouton_valider.configure(bg="green")
        except :
            pass 

class FenetreInitialisation:
    def __init__(self):
        self.fenetre = tkinter.Tk()

        self.colonnes = {}
        i = 0
        for jeu in ["FiveM","Minecraft","SCP:SL"]:
            self.colonnes[jeu] = FormulaireAcces(jeu,self.fenetre,i)
            i += 1
        self.fenetre.mainloop()
FenetreInitialisation()