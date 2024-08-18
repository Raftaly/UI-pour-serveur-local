from Client import Client


class SCP :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "SCP:SL"
        self.client = Client(ip,pseudo,mdp)