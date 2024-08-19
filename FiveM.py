from Client import Client
import webbrowser 
import bs4
import requests
import csv


console = None

LIEN_ARTIFACT = "https://runtime.fivem.net/artifacts/fivem/build_proot_linux/master/"
TYPE_LIEN_VALIDE = [".git",".zip"]

class FiveM :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "FiveM"
        self.client = Client(ip,pseudo,mdp)

        self.console = None

        self.options = {"Allumer le serveur" : self.allumer,"Eteindre le serveur":self.eteindre}

    def allumer(self):
        self.client.connecter()
        self.log("--------------- Nouvelle Instance du serveur ---------------")

        self.log("Recherche de mise à jour...")
        self.mise_a_jour()

        self.log("Démarrage du serveur")
        self.client.changer_de_repertoire("base_serveur")
        self.client.execute_commande("sh run.sh",False)

        self.log("Ouverture du tableau de bord du serveur (S'il n'y a pas de page disponible c'est que le serveur n'a pas marché)")
        webbrowser.open_new("http://" + self.client.ip+":40120")

    def eteindre(self):
        if self.client.est_connecte() :
            self.log("Fermeture du serveur...")
            self.client.execute_commande("pkill -U FiveM") # Stoppe tous les procesuss lancé par fiveM (un peu radicale mais ça marche)
            self.log("Serveur fermé !")

            self.log("--------------- Fermeture de l'instance du serveur ---------------")
            self.client.connecter()

    def mise_a_jour(self):
        if self.client.est_connecte() :
            version_disponible,lien = derniere_version_disponible()
            version_actuelle = recupere_version_actuelle()
            
            if version_actuelle != -1 and version_disponible != -1 and version_disponible > version_actuelle :
                self.log("Une nouvelle version est disponible => Mise à jour lancée")

                self.client.changer_de_repertoire("base_serveur")

                self.log("Nettoyage des fichiers...")
                self.client.execute_commande("rm -r alpine && rm run.sh")
                
                self.log("Téléchargement de la mise à jour...")
                self.client.execute_commande("wget " + lien)
                
                self.log("Extraction des fichiers...")
                self.client.execute_commande("tar xf fx.tar.xz")

                self.log("Finalisation de l'installation...")
                self.client.execute_commande("rm fx.tar.xz")

                self.log("Mise à jour terminée !")

                mettre_a_jour_version("FiveM",version_disponible)

        else :
            self.log("Mise à jour impossible le serveur ne repond pas :( )")
            self.eteindre()

    def recupere_mod_installes(self):
        self.client.changer_de_repertoire("data_serveur/resources")
        liste_modes = [mode for mode in self.client.execute_commande("ls").split() if mode[0] != "["]
        
        return liste_modes

    def lien_valide(self,lien):
        n = len(lien)
        if lien[n - 4:] == ".git" :
            return True,"git"
        elif lien[n - 4:] == ".zip" :
            return True,"zip"
        return 
    
    def ajoute_mode(self,lien):
        est_valide,type_f = self.lien_valide(lien)
        if est_valide :
            nom = recupere_nom_mode(lien)

            liste_modes_installes = self.recupere_mod_installes()
            if nom in liste_modes_installes :
                self.log("Le mode est déjà installé")
            else :
                self.client.changer_de_repertoire("data_serveur/resources")

                self.log("Téléchargement du mode " + nom + "...")
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
                    self.log("Mode installé")
                    return nom
                else:
                    self.log("! Mode non installé (Le dossier est complexe) !")
                
        else :
            self.log("Le lien n'est pas valide !")

    def mettre_a_jour_modes_cfg(self,liste_modes):
        texte = ""
        for mode in liste_modes :
            texte += "ensure " + mode + "\n"
        
        self.client.changer_de_repertoire("data_serveur")

        self.client.execute_commande("rm modes.cfg")
        self.client.execute_commande("echo '%s' >> modes.cfg" %texte)

    def retire_mode(self,nom):

        liste_modes_installes = self.recupere_mod_installes()

        if nom in liste_modes_installes :
            self.log("Désinstallation du mode " + nom)
            self.client.changer_de_repertoire("data_serveur/resources")
            self.client.execute_commande("rm -r " + nom)
            liste_modes_installes.remove(nom)

            self.client.changer_de_repertoire("data_serveur")

            self.mettre_a_jour_modes_cfg(liste_modes_installes)
            self.log("Désinstallation complété")
            

        else :
            self.log("Le mode  n'est pas installé !")

    def est_dossier_root(self,nom_mode):
        self.client.changer_de_repertoire("data_serveur/resources")
        fichiers = self.client.execute_commande("ls " + nom_mode).split()

        return "fxmanifest.lua" in fichiers
    
    def CreerConsole(self,console):
        self.console = console
        self.client.console = console

    def log(self,texte):
        self.console.set(self.console.get()+"\n"+texte)


    
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
    return lien[:i]

#CSV
def recupere_version_actuelle():
    fichier = open("Versions.csv","r")
    liste_jeux = list(csv.DictReader(fichier))

    trouve,indice = indice_dictionnaire_jeu("FiveM",liste_jeux)
    fichier.close()

    if trouve :
        return liste_jeux[indice]["Version"]
    else :
        return -1

def mettre_a_jour_version(jeu,nouvelle_version): #Ajoute le jeu s'il n'existe pas
    fichier = open("Versions.csv","w+")
    liste_jeux = list(csv.DictReader(fichier))
    trouve,indice_jeu = indice_dictionnaire_jeu(jeu,liste_jeux)
    if trouve :
        liste_jeux[indice_jeu]["Version"] = nouvelle_version
    else :
        liste_jeux.append({"Nom" : jeu, "Version" : nouvelle_version})

    cles = ["Nom","Version"]

    descripteur = csv.DictWriter(fichier,cles)
    descripteur.writeheader()
    descripteur.writerows(liste_jeux)
    fichier.close()

def indice_dictionnaire_jeu(nom_jeu,liste) :
    i = 0
    while i < len(liste) and liste[i]["Nom"] != nom_jeu :
        i +=1
    return (i < len(liste),i)

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
           
