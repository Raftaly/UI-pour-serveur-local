from Client import Client


class Minecraft :
    def __init__(self,ip,pseudo,mdp):

        self.nom = "Minecraft"
        self.client = Client(ip,pseudo,mdp)