from threading import Thread
import tkinter
import tkinter.simpledialog
import tkinter.ttk

class GestionnaireOptions:
    def __init__(self):
        self.liste = []

    def ajoute_option_simple(self,action,fonction,parallele):
        self.liste.append(Option_Simple(action,fonction,parallele))

    def ajoute_option_texte(self,action,fonction,parallele,consignes):
        self.liste.append(Option_Texte(action,fonction,parallele,consignes))

    def ajoute_option_choix(self,action,fonction,parallele,consignes,choix):
        self.liste.append(Option_choix(action,fonction,parallele,consignes,choix))

    def recupere_option(self,action):
        i = 0
        while i < len(self.liste) and self.liste[i].nom != action :
            i += 1

        if i == len(self.liste):
            return None 
        else :
            return self.liste[i]

class Option_Simple() :
    def __init__(self,action,fonction,parallele):
        self.nom = action
        self.fonction = fonction
        self.en_parallele = parallele

        self.fenetre_necessaire = False

    def execute_fonction(self):
        if self.en_parallele :
            Thread(target=self.fonction).start()
        else :
            self.fonction()

class Option_Texte() :
    def __init__(self,action,fonction,parallele,consignes):
        self.nom = action
        self.fonction = fonction
        self.en_parallele = parallele

        self.fenetre_necessaire = False

        self.consignes = consignes

    def execute_fonction(self):
        reponse = tkinter.simpledialog.askstring(self.nom,self.consignes)

        if self.en_parallele :
            Thread(target=self.fonction,args=[reponse]).start()
        else :
            self.fonction(reponse)

class Option_choix :
    def __init__(self,action,fonction,parallele,consignes,choix : list):
        self.nom = action
        self.fonction = fonction
        self.en_parallele = parallele

        self.consignes = consignes
        self.choix = choix

        self.fenetre_necessaire = True

    def ajoute_choix(self,choix):
        self.choix.append(choix)

    def retire_choix(self,choix):
        self.choix.remove(choix)

    def creer_dialog(self,fenetre):
        root = tkinter.Toplevel(fenetre)
        root.title = self.nom
        
        label = tkinter.ttk.Label(root,text=self.consignes)
        label.grid(column=0,row=0)

        valeur_selectionnee = tkinter.StringVar()

        choix = tkinter.ttk.Combobox(root,values=self.choix,textvariable=valeur_selectionnee)
        choix.grid(column=1,row=0)

        def cliquer(choix):
            self.execute_choix(choix)
            self.retire_choix(choix)
            root.destroy()

        bouton = tkinter.ttk.Button(root,text="Valider",command=lambda : cliquer(choix.get()))
        bouton.grid(column=2,row=0)

        root.mainloop()

    def execute_choix(self,choix):
        if self.en_parallele :
            Thread(target=self.fonction,args=[choix]).start()
        else :
            self.fonction(choix)

    def execute_fonction(self,fenetre):
        self.creer_dialog(fenetre)