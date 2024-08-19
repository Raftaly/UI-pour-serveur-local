import paramiko
import paramiko.client
import time


TENTATIVE_CONNEXION_MAX = 50


class Client :
    def __init__(self,ip,utilisateur,mdp):
        self.ip = ip
        self.utilisateur = utilisateur
        self.mot_de_passe = mdp 

        self.terminal = paramiko.client.SSHClient()

        self.repertoire_actuelle = ""

        self.console = None
        self.ligne_console = 0

        self.connecter()

    def connecter(self):
        if not self.est_connecte() :
            print("Connexion au serveur sous l'identifiant %s..." %self.utilisateur)

            self.terminal.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.terminal.connect(hostname=self.ip,username=self.utilisateur,password=self.mot_de_passe)

            nb_tentatives = 0
            while nb_tentatives < TENTATIVE_CONNEXION_MAX and not self.est_connecte() :
                nb_tentatives += 1
                self.terminal.connect(hostname=self.ip,username=self.utilisateur,password=self.mot_de_passe)
                
            
            if self.est_connecte():
                print("Connecté au serveur ! :)")
                return True
            else :
                print("Connexion échoué. Le serveur est-il allumé et connecté au wifi ?")
                return False

    def est_connecte(self):
        if self.terminal.get_transport() is not None :
            return self.terminal.get_transport().is_active()
        else :
            False
        
    def deconnecter(self):
        self.terminal.close()
        self.terminal = None 

    def execute_commande(self,commande,attendre_reponse = True):
        if attendre_reponse :
            if self.repertoire_actuelle != "" :
                _,reponse,erreur = self.terminal.exec_command("cd %s &&" %self.repertoire_actuelle + commande)
            else :
                _,reponse,erreur = self.terminal.exec_command(commande)

            print(erreur.read().decode())
            return reponse.read().decode()
        else :
            if self.repertoire_actuelle != "" :
                self.terminal.exec_command("cd %s &&" %self.repertoire_actuelle + commande)
            else :
                self.terminal.exec_command(commande)
        
    def changer_de_repertoire(self,chemin) :
        self.repertoire_actuelle = chemin

    def log(self,texte):
        self.console.configure(state="normal")
        self.console.insert("end","\n"+texte,"center")
        self.console.configure(state="disabled")
        self.console.see("end")

