from Client import Client
from Module_options import GestionnaireOptions

class Minecraft :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "Minecraft"
        self.client = Client(ip,pseudo,mdp)

        self.options = GestionnaireOptions()
    
    def CreerConsole(self,console):
        pass