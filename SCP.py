from Client import Client
from Module_options import GestionnaireOptions


class SCP :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "SCP:SL"
        self.client = Client(ip,pseudo,mdp)

        self.options = GestionnaireOptions()

    def CreerConsole(self,console):
        pass