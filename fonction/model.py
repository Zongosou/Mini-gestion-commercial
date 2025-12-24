import os
from PySide6.QtCore import Qt
from jinja2 import Environment, FileSystemLoader
try:
    from num2words import num2words
except:
    pass

class Model:    
    def __init__(self) -> None:
        super().__init__()

        self.env = Environment(loader=FileSystemLoader('template'))

        # La fonction principale
    def genere_model2(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, tab, msg,ifu,autre):
        try:
            if not tab.model():
                raise ValueError("Le tableau ne contient pas de modèle valide.")

            nbchamps = tab.model().columnCount()
            nblignes = tab.model().rowCount()

            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "ifu":ifu,
                    "autre":autre
                },
                "message": msg,
                "entetes_tableau": [tab.model().headerData(j, Qt.Orientation.Horizontal, 0) for j in range(nbchamps)],
                "donnees_tableau": [
                    [tab.model().index(i, j).data() or '' for j in range(nbchamps)]
                    for i in range(nblignes)
                ]
            }

            # Chargez le modèle Jinja2
            template = self.env.get_template('html_model.html')

            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
    
    def genere_statistique(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, clients_dict,msg:str,ifu,autre):
        try:
           
            # Calcule 
            total_general = 0
            clients_list = []
            for fourn, produits in clients_dict.items():
                
                sous_total =sum(l["montant"] for l in produits)
                total_general += sous_total
                clients_list.append({"client":fourn,"produits":produits,"sous_total":sous_total})

            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "ifu":ifu,
                    "autre":autre
                },
                "clients":clients_list,
                "total_general":total_general,  
                "message":msg             
            }
            # Chargez le modèle Jinja2
            template = self.env.get_template('statistique.html')
            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        # Utile
        
     
    def genere_general(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, clients_dict,msg,ifu,autre):
        try:
           
            # Calcule 
            total_general = 0
            clients_list = []
            for fourn, produits in clients_dict.items():
                
                sous_total =sum(l["montant"] for l in produits)
                total_general += sous_total
                clients_list.append({"client":fourn,"produits":produits})

            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "ifu":ifu,
                    "autre":autre
                },
                "clients":clients_list,
                "total_general":total_general,  
                "message":msg             
            }
            # Chargez le modèle Jinja2
            template = self.env.get_template('general_model.html')
            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"

    def facture_(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None,responsabable, list_article,vente,msg,remarque,ifu,autre,date,chemin=None):
        try:
           
            # Calcule 
            lettre = ""
            ht = 0.0
            for j in list_article:
                ht  +=float(j[3])
                mnt_ttc = ht * (1 + (float(vente['tva']) / 100))
                net = float(mnt_ttc)
                try:
                    lettre=num2words(net,lang='fr')
                except Exception as e:
                    print(str(e))
           
            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "resp":responsabable,
                    "ifu":ifu,
                    "autre":autre
                },
                "liste_article":list_article,
                "vente":vente,
                "message":msg,
                "ht":ht  ,
                "ttc":mnt_ttc,
                "net": net,
                "lettre":lettre ,
                "chemin":chemin   ,
                "remarque":remarque,
                "date": date
            }
            
            # Chargez le modèle Jinja2
            template = self.env.get_template('facture.html')

            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        # Utile

    def inventaire_(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, ifu=None, autre=None, groupes=dict(), msg=None, Entete_=None):
        try:
            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            for periode, lignes in groupes.items():
                total = sum(montant for _, _, _, montant in lignes)
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "ifu": ifu,
                    "autre": autre
                },
                "groupe":groupes,
                "titre":msg ,
                "totaux":total,
                "periodes":periode,
                "entete":Entete_
            }
            
            # Chargez le modèle Jinja2
            template = self.env.get_template('model_statist.html')

            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        # Utile
    
    def genere_article(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, tab, msg):
        try:
            if not tab.model():
                raise ValueError("Le tableau ne contient pas de modèle valide.")

            nbchamps = tab.model().columnCount()
            nblignes = tab.model().rowCount()

            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse
                },
                "message": msg,
                "entetes_tableau": [tab.model().headerData(j, Qt.Orientation.Horizontal, 0) for j in range(nbchamps)],
                "donnees_tableau": [
                    [tab.model().index(i, j).data() or '' for j in range(nbchamps)]
                    for i in range(nblignes)
                ]
            }

            # Chargez le modèle Jinja2
            template = self.env.get_template('html_model.html')

            # Rendre le modèle avec les données
            html_rendu = template.render(donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        # Utile
        
    def facture_achat(self,list_article,achat):
        try:
           
            # Calcule 
            lettre = ""
            ht = 0.0
            net = 0.0
            mnt_ttc = 0.0
            for j in list_article:
                ht  +=float(j[3])
                mnt_ttc = ht * (1 + (float(achat['tva']) / 100))
                net = float(mnt_ttc)
                try:
                    lettre=num2words(net,lang='fr')
                except Exception as e:
                    print(str(e))
           
            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                
                "liste_article":list_article,
                "achat":achat,
                "ht":ht  ,
                "ttc":mnt_ttc,
                "net": net,
                "lettre":lettre           
                      
            }
            
            # Chargez le modèle Jinja2
            template = self.env.get_template('fact_achat.html')

            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        

    
    def genere_statistique_date(self, Entr:None, T1:None, T2:None, info:None, ville:None, adresse:None, clients_dict,msg:str,ifu,autre):
        try:
           
            # Calcule 
            total_general = 0
            clients_list = []
            for fourn, produits in clients_dict.items():
                
                sous_total =sum(l["montant"] for l in produits)
                total_general += sous_total
                clients_list.append({"date":fourn,"produits":produits,"sous_total":sous_total})

            # Préparez le contexte (les données) pour Jinja2
            # Créez des dictionnaires pour une meilleure organisation
            donnees = {
                "entreprise": {
                    "nom": Entr,
                    "tel1": T1,
                    "tel2": T2,
                    "info": info,
                    "ville": ville,
                    "adresse": adresse,
                    "ifu":ifu,
                    "autre":autre
                },
                "clients":clients_list,
                "total_general":total_general,  
                "message":msg             
            }
            # Chargez le modèle Jinja2
            template = self.env.get_template('stat_date.html')
            # Rendre le modèle avec les données
            html_rendu = template.render(donnees=donnees)

            return html_rendu

        except Exception as e:
            return f"<p>Erreur : {e}</p>"
        # Utile
        
     