from Client import Client
from Module_options import GestionnaireOptions

import webbrowser 
import bs4
import requests
import csv
from os.path import exists



console = None

LIEN_ARTIFACT = "https://runtime.fivem.net/artifacts/fivem/build_proot_linux/master/"
TYPE_LIEN_VALIDE = [".git",".zip"]

class FiveM :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "FiveM"
        self.client = Client(ip,pseudo,mdp)

        self.console = None

        self.options = GestionnaireOptions()
        self.initialise_options()

        self.client.execute_commande("pkill -U FiveM")

    def initialise_options(self):
        self.options.ajoute_option_simple("Allumer le serveur",self.allumer,True)
        self.options.ajoute_option_simple("Eteindre le serveur",self.eteindre,True)
        self.options.ajoute_option_texte("Ajouter un mode",self.ajoute_mode,False,"Copie-Colle le lien github du mode :")
        self.options.ajoute_option_choix("Retirer un mode",self.retire_mode,False,"Choisis un mode à retirer",self.recupere_mod_installes())

    def allumer(self):
        if not self.client.est_connecte() :
            self.client.connecter()
            self.client.log("--------------- Nouvelle Instance du serveur ---------------")

            self.client.log("Recherche de mise à jour...")
            self.mise_a_jour()

            self.client.log("Démarrage du serveur")
            self.client.changer_de_repertoire("base_serveur")
            self.client.execute_commande("sh run.sh",False)

            self.client.log("Ouverture du tableau de bord du serveur \n(S'il n'y a pas de page disponible c'est que le serveur n'a pas marché)")
            webbrowser.open_new("http://" + self.client.ip+":40120")
        else :
            self.client.log("Le serveur est déjà allumé !")

    def eteindre(self):
        if self.client.est_connecte() :
            self.client.log("Fermeture du serveur...")
            self.client.deconnecter()
            self.client.log("Serveur fermé !")

            self.client.log("--------------- Fermeture de l'instance du serveur ---------------")

    def mise_a_jour(self):
        if self.client.est_connecte() :
            version_disponible,lien = derniere_version_disponible()
            version_actuelle = self.recupere_version_actuelle()
            
            if version_actuelle == -1 or version_disponible == -1 or version_disponible > version_actuelle :
                self.client.log("Une nouvelle version est disponible => Mise à jour lancée (%s --> %s)" % (str(version_actuelle), str(version_disponible)))

                self.client.changer_de_repertoire("base_serveur")

                self.client.log("Nettoyage des fichiers...")
                self.client.execute_commande("rm -r alpine && rm run.sh")
                
                self.client.log("Téléchargement de la mise à jour...")
                self.client.execute_commande("wget " + lien)
                
                self.client.log("Extraction des fichiers...")
                self.client.execute_commande("tar xf fx.tar.xz")

                self.client.log("Finalisation de l'installation...")
                self.client.execute_commande("rm fx.tar.xz")

                self.client.log("Mise à jour terminée !")

                self.mettre_a_jour_version(version_disponible)

        else :
            self.client.log("Mise à jour impossible le serveur ne repond pas :( )")
            self.eteindre()

    def recupere_mod_installes(self):
        self.client.changer_de_repertoire("data_serveur/resources")
        liste_modes = [mode for mode in self.client.execute_commande("ls").split() if mode[0] != "["]

        return liste_modes

    def lien_valide(self,lien):
        if lien is None :
            return False,""

        n = len(lien)
        if lien[n - 4:] == ".git" :
            return True,"git"
        elif lien[n - 4:] == ".zip" :
            return True,"zip"
        else :
            return False,""
    
    def ajoute_mode(self,lien):
        self.client.connecter()

        est_valide,type_f = self.lien_valide(lien)
        if est_valide :
            nom = recupere_nom_mode(lien)

            liste_modes_installes = self.recupere_mod_installes()
            if nom in liste_modes_installes :
                self.client.log("Le mode est déjà installé")
            else :

                self.client.changer_de_repertoire("data_serveur/resources")

                self.client.log("Téléchargement du mode " + nom + "...")
                if type_f == "git" :
                    self.client.execute_commande("git clone " + lien)
                elif type_f == "zip" :
                    self.client.execute_commande("mkdir " + nom)
                    self.client.changer_de_repertoire("data_serveur/resources/" + nom)
                    self.client.execute_commande("wget " + lien)
                    self.client.execute_commande("unzip %s.zip" %nom )
                    self.client.execute_commande ("rm " + nom)


                if self.est_dossier_root(nom) :
                    liste_modes_installes.append(nom)

                    self.mettre_a_jour_modes_cfg(liste_modes_installes)

                    self.options.recupere_option("Retirer un mode").ajoute_choix(nom)
                    
                    self.client.log("Mode installé")
                else:
                    self.client.log("! Mode non installé (Le dossier est complexe) !")

                self.client.deconnecter()
                
        else :
            self.client.log("Le mode n'existe pas ou le lien n'est pas de github !")

    def mettre_a_jour_modes_cfg(self,liste_modes):
        texte = ""
        for mode in liste_modes :
            texte += "ensure " + mode + "\n"
        
        self.client.changer_de_repertoire("data_serveur")

        self.client.execute_commande("rm modes.cfg")
        self.client.execute_commande("echo '%s' >> modes.cfg" %texte)

    def retire_mode(self,nom):
        self.client.connecter()

        liste_modes_installes = self.recupere_mod_installes()

        if nom in liste_modes_installes :
            self.client.log("Désinstallation du mode " + nom)
            self.client.changer_de_repertoire("data_serveur/resources")
            self.client.execute_commande("rm -r " + nom)
            liste_modes_installes.remove(nom)

            self.client.changer_de_repertoire("data_serveur")

            self.mettre_a_jour_modes_cfg(liste_modes_installes)
            self.client.log("Désinstallation complété")
            
            self.client.deconnecter()

        else :
            self.client.log("Le mode '%s' n'est pas installé !" %nom)

    def est_dossier_root(self,nom_mode):
        self.client.changer_de_repertoire("data_serveur/resources")
        fichiers = self.client.execute_commande("ls " + nom_mode).split()

        return "fxmanifest.lua" in fichiers
    
    def CreerConsole(self,console):
        self.console = console
        self.client.console = console

    def recupere_version_actuelle(self):
        self.client.connecter()
        self.client.changer_de_repertoire("")
        version = self.client.execute_commande("cat Version.txt",True).strip()

        if version.isdigit() :
            return int(version)
        else :
            return -1
        
    def mettre_a_jour_version(self,version):
        self.client.connecter()
        self.client.changer_de_repertoire("")
        self.client.execute_commande('echo "%s" > Version.txt' % str(version))



    
def recupere_nom_mode(lien):
    i = len(lien) - 5 #Les 4 dernier sont le .git ou .zip etc... (inutile)
    lien = lien[:i+1]
    
    while lien[i] != "/" :
        i -=1

    return lien[i + 1:]

# Version internet
def derniere_version_disponible():
    reponse = requests.get("https://runtime.fivem.net/artifacts/fivem/build_proot_linux/master/") #Envoie une requête au serveur
    
    if reponse.ok : #Vérifie si la page est accessible
        page = bs4.BeautifulSoup(reponse.content,"html.parser") #Récupère le contenu de la page avec la réponse
        
        #Les fichiers valides sont à partir de l'indice 3 dans la fonction find_all("a") => On veut la dernière version donc on prend le plus près de 0
        bloc_a = page.find_all("a")[3]
        lien = bloc_a.get('href')[2:]

        return (extraire_version_lien(lien), LIEN_ARTIFACT + lien)

    else :
        print("Connexion à la page des fichiers impossible !")
        return -1

def extraire_version_lien(lien) : #On retire à l'avance les bout inutiles du début
    i = 0
    while lien[i] != "-" :
        i += 1
    return int(lien[:i])

#Texte
def derniere_occ(mot):
    occurences = {}
    for i in range(len(mot)):
        occurences[mot[i]] = i 
    return occurences

def decalage(mot,car_texte,pos_lettre_mot,dico_occ_mot):
    if not car_texte in mot :
        decalage_final = pos_lettre_mot + 1
    else :
        indice_derniere_occurence = dico_occ_mot[car_texte]
        decalage_final = pos_lettre_mot - indice_derniere_occurence
        if decalage_final < 0 :
            decalage_final = 1

    return decalage_final

def boyer_moore(texte,mot):
    pos_mot = 0
    trouve = False
    dico_mot = derniere_occ(mot)
    while not trouve and pos_mot + len(mot) < len(texte) :
        i_lettre = len(mot) - 1
        while i_lettre >= 0 and mot[i_lettre] == texte[pos_mot + i_lettre] :
            i_lettre -= 1
        
        if i_lettre == -1 :
            trouve = True
        else :
            pos_mot += decalage(mot,texte[pos_mot + i_lettre],i_lettre,dico_mot)
    return (trouve,pos_mot)
           
