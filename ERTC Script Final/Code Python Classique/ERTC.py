import os
import sqlite3
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox, simpledialog
from tkinter import ttk
import customtkinter as CTk
from customtkinter import CTkButton
from tkcalendar import DateEntry
from tkinter import filedialog
from PIL import Image,ImageTk
import pandas as pd
from tkcalendar import Calendar
import datetime
#------------------------------------- [ CREER DES CHEMIN RELATIF ] -----------------------------------------------------------------

# Obtenir le répertoire où se trouve le script
script_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# Définir des chemins relatifs en fonction de l'emplacement du script
chemin_db = os.path.join(script_dir, 'ERTC_Database.db')
chemin_db_typeProduit = os.path.join(script_dir,
'../../../ERTC Script Finale (initial)/ERTC Script Final/Code Python Classique/typeProduit.db')
chemin_export_excel = os.path.join(script_dir,
'../../../ERTC Script Finale (initial)/ERTC Script Final/Code Python Classique/Export_Excel')

#------------------------------------- [ CREATION BDD ] -----------------------------------------------------------------
def creer_table_produits():
    # Créer le répertoire 'Export_Excel' s'il n'existe pas
    os.makedirs(chemin_export_excel, exist_ok=True)
    try:
#Vérifier si le fichier de base de données existe dans le chemin spécifié
        if not os.path.exists(chemin_db):
         conn = sqlite3.connect(chemin_db)
         curseur = conn.cursor()
         curseur.execute('''
          CREATE TABLE IF NOT EXISTS Produits (
            id_produit INTEGER PRIMARY KEY AUTOINCREMENT,
            "Date de la rédaction du rapport" TEXT
            )
        ''')
         conn.commit()
         conn.close()
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création de la base de données : {e}")

def creer_table_clients():
    # Créer le répertoire 'Export_Excel' s'il n'existe pas
    os.makedirs(chemin_export_excel, exist_ok=True)
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS Clients (
            id_client INTEGER PRIMARY KEY AUTOINCREMENT,
            "Nom de l'entreprise" TEXT
            )
        ''')
    conn.commit()
    conn.close()
creer_table_produits()
creer_table_clients()

#------------------------------------- [ INSERTION DANS BDD ] -----------------------------------------------------------------
def inserer_colonnes_produit(colonnes_produits):
    with sqlite3.connect(chemin_db) as conn:
        curseur = conn.cursor()
        for nom_colonne in colonnes_produits:
            # Vérifier si la colonne existe déjà avant d'essayer de l'ajouter
            curseur.execute(f"PRAGMA table_info(Produits)")
            existing_columns = [col[1] for col in curseur.fetchall()]
            if nom_colonne not in existing_columns:
                curseur.execute(f'ALTER TABLE Produits ADD COLUMN "{nom_colonne}" TEXT')
def inserer_colonnes_client(colonnes_clients):
    with sqlite3.connect(chemin_db) as conn:
        curseur = conn.cursor()
        for nom_colonne in colonnes_clients:
            # Vérifier si la colonne existe déjà avant d'essayer de l'ajouter
            curseur.execute(f"PRAGMA table_info(Clients)")
            existing_columns = [col[1] for col in curseur.fetchall()]
            if nom_colonne not in existing_columns:
                curseur.execute(f'ALTER TABLE Clients ADD COLUMN "{nom_colonne}" TEXT')

# Liste pour stocker les noms de colonnes pour chaque table
colonnes_produits = []
colonnes_clients = []
text_file = 'output.txt'
# Lecture du fichier texte
with open(text_file, "r", encoding="utf-8") as file:
    for ligne in file:
        # Extraire le nom de la colonne avant les deux points
        nom_colonne = ligne.split(":")[0].strip()
        # Si la ligne contient "BD CLIENT", ajouter à la liste des colonnes clients
        if "BD CLIENT" in ligne:
            colonnes_clients.append(nom_colonne)
        else:
            colonnes_produits.append(nom_colonne)

# Insérer les colonnes dans les tables produits et clients
if colonnes_produits:
    inserer_colonnes_produit(colonnes_produits)
if colonnes_clients:
    inserer_colonnes_client(colonnes_clients)


# ------------------------------------- [ INSERTION DANS BDD ] -----------------------------------------------------------------
# Fonction pour insérer des données dans la table "produit" de la base de données.

def inserer_produit(**kwargs):
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()

    # Generate dynamic insertion query based on column names
    colonnes = ", ".join(f'"{key}"' for key in kwargs.keys())
    valeurs = ", ".join("?" for _ in kwargs.values())

    # Construct the SQL query
    requete = f'INSERT INTO Produits ({colonnes}) VALUES ({valeurs})'

    # Encode the values to avoid character encoding issues
    valeurs_encodees = [str(val).encode('utf-8') if isinstance(val, str) else val for val in kwargs.values()]

    # Execute the SQL query
    curseur.execute(requete, valeurs_encodees)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

def inserer_client(**kwargs):
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()

    # Generate dynamic insertion query based on column names
    colonnes = ", ".join(f'"{key}"' for key in kwargs.keys())
    valeurs = ", ".join("?" for _ in kwargs.values())

    # Construct the SQL query
    requete = f'INSERT INTO Clients ({colonnes}) VALUES ({valeurs})'

    # Encode the values to avoid character encoding issues
    valeurs_encodees = [str(val).encode('utf-8') if isinstance(val, str) else val for val in kwargs.values()]

    # Execute the SQL query
    curseur.execute(requete, valeurs_encodees)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()



#combobox_clients = None
def obtenir_clients():
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()
    curseur.execute("SELECT id_client, [Nom de l'entreprise] FROM Clients")
    clients = curseur.fetchall()
    conn.close()
    return clients
def ajouter_combobox_clients():
    global combobox_clients # Définir la variable comme globale
    clients = obtenir_clients()
    clients_list = [f"{client[0]}: {client[1]}" for client in clients]
    combobox_clients = CTk.CTkComboBox(client_frame, values=clients_list, text_color="White", fg_color="DarkOrchid4")
    combobox_clients.pack(pady=5, padx=10, fill="x")
    combobox_clients.bind("<<ComboboxSelected>>", remplir_champs_client)

def remplir_champs_client(event):
    global combobox_clients  # Accéder à la variable globale
    client_id = combobox_clients.selection_get().split(":")[0]
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()
    curseur.execute("SELECT * FROM Clients WHERE id_client=?", (client_id,))
    client = curseur.fetchone()
    conn.close()

    if client:
        entry_nom_de_entreprise.delete(0, tk.END)
        entry_nom_de_entreprise.insert(0, client[1])
        entry_nom_du_fabricant.delete(0, tk.END)
        entry_nom_du_fabricant.insert(0, client[2])
        entry_adresse_du_fabricant.delete(0, tk.END)
        entry_adresse_du_fabricant.insert(0, client[3])
        entry_siret_du_fabricant.delete(0, tk.END)
        entry_siret_du_fabricant.insert(0, client[4])
        entry_nom_du_conditionneur.delete(0, tk.END)
        entry_nom_du_conditionneur.insert(0, client[5])
        entry_adresse_du_conditionneur.delete(0, tk.END)
        entry_adresse_du_conditionneur.insert(0, client[6])
        entry_siret_du_conditionneur.delete(0, tk.END)
        entry_siret_du_conditionneur.insert(0, client[7])
        entry_nom_du_distributeur.delete(0, tk.END)
        entry_nom_du_distributeur.insert(0, client[8])
        entry_adresse_du_distributeur.delete(0, tk.END)
        entry_adresse_du_distributeur.insert(0, client[9])
        entry_siret_du_distributeur.delete(0, tk.END)
        entry_siret_du_distributeur.insert(0, client[10])
        entry_nom_de_la_personne_responsable.delete(0, tk.END)
        entry_nom_de_la_personne_responsable.insert(0, client[11])
        entry_adresse_de_la_personne_responsable.delete(0, tk.END)
        entry_adresse_de_la_personne_responsable.insert(0, client[12])
        entry_siret_de_la_personne_responsable.delete(0, tk.END)
        entry_siret_de_la_personne_responsable.insert(0, client[13])

# Fonction pour valider le formulaire avec les champs du produit
def valider_formulaire():
    # Assurez-vous que les champs obligatoires ne sont pas vides
    if not (
            entry_date_de_redaction_rapport.get_date() and entry_etude.get() and entry_denomination_commerciale_du_produit
            and entry_nom_de_entreprise and entry_nom_du_fabricant and entry_adresse_du_fabricant
            and entry_siret_du_fabricant and entry_nom_du_conditionneur and entry_adresse_du_conditionneur and entry_siret_du_conditionneur
            and entry_nom_du_distributeur and entry_adresse_du_distributeur and entry_siret_du_distributeur and entry_nom_de_la_personne_responsable
            and entry_adresse_de_la_personne_responsable and entry_siret_de_la_personne_responsable
            and entry_reference_du_produit_evalue and combobox_type_de_produit and entry_contenant_et_type_de_conditionnement and entry_allegation_sante
            and combobox_population_cible and combobox_circuit_de_distribution and combobox_description_produit
            and entry_aspect and entry_couleur and combobox_odeur and combobox_type_de_produit  # site_application_1
            and entry_ph_20c and entry_densite_20c and entry_indice_refraction_20c and entry_point_eclair and entry_point_fusion
            and entry_viscosite and entry_activite_eau and entry_conditionnement_et_presentation and entry_capacite and label_stockage and
            date_mise_sur_marche_du_premier_lot and text_restrictions_cosmetiques and combobox_ddm and combobox_Formulation_1
            and combobox_Cotation_1 and combobox_interface_produit and combobox_Cotation_2 and combobox_duree_utilisation_3 and combobox_Cotation_3 and combobox_Cotation_4
            and combobox_zone_application_4 and combobox_public and combobox_Cotation_5 and combobox_rt
            and combobox_pao and combobox_pao_retenue and text_analyses and combobox_conclusion_1 and combobox_risque_microbiologique
            and entry_fonction and entry_mode_emploi and text_precautions_emploi_et_restrictions_usage and entry_x_informations_sur_le_produit_cosmetique
            and (entry_pays_origine or checkbox_pays_origine) and (checkbox_contenu_1 or checkbox_contenu_2)
            and (checkbox_symbole_date_durabilite_minimale_1 or checkbox_symbole_date_durabilite_minimale_2) and
            (checkbox_precautions_particulieres_emploi_1 or checkbox_precautions_particulieres_emploi_2)
            and (checkbox_numero_de_lot_de_fabrication_1 or checkbox_numero_de_lot_de_fabrication_2) and
            (checkbox_fonction_du_produit_1 or checkbox_fonction_du_produit_2) and (
            checkbox_liste_des_ingredients_1 or checkbox_liste_des_ingredients_2)
            and entry_langue and entry_liste_1 and entry_liste_2 and (combobox_allergenes or entry_allergenes) and text_recommandations and text_ccl_microbio and text_fabricant
            and text_description and text_restrictions_cosmetiques_opinions_SCCS
            and combobox_impuretes and combobox_Allergenes and (combobox_produit_rincer or entry_produit_rincer)
            and combobox_conclusion_fin and date_de_redaction_rapport_final):
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
        return
    try:
        conn_type_produit = sqlite3.connect(chemin_db_typeProduit)
        curseur_type_produit = conn_type_produit.cursor()
        curseur_type_produit.execute("SELECT * FROM typeProduit WHERE product_type=?",
                                     (combobox_type_de_produit.get(),))
        type_produit_data = curseur_type_produit.fetchone()
        conn_type_produit.close()
        if type_produit_data:
            print("Type produit data:", type_produit_data)  # Debugging line
        else:
            print("No data found for the selected product type.")  # Debugging line
            messagebox.showerror("Erreur", "No data found for the selected product type.")
            return
    except Exception as e:
        print("Database error:", e)  # Debugging line
        messagebox.showerror("Erreur", f"Erreur de base de données: {e}")
    # Fusionner les données de la partie de produit du formulaire avec les données supplémentaires de "typeProduit"
    data_produit = {
            "Date de la rédaction du rapport": entry_date_de_redaction_rapport.get_date(),
            "Étude": entry_etude.get(),
            "Dénomination commerciale du produit": entry_denomination_commerciale_du_produit.get(),
            "Dénomination commerciale (déclinaison)": entry_denomination_commerciale_declinaison.get(),
            "Référence du produit évalué": entry_reference_du_produit_evalue.get(),
            "Type de produit": combobox_type_de_produit.get(),
            "Contenant et type de conditionnement": entry_contenant_et_type_de_conditionnement.get(),
            "Allégations santé": entry_allegation_sante.get(),
            "Population cible": combobox_population_cible.get(),
            "Circuit de distribution": combobox_circuit_de_distribution.get(),
            "Description du produit": combobox_description_produit.get(),
            "Aspect": entry_aspect.get(),
            "Couleur": entry_couleur.get(),
            "Odeur": combobox_odeur.get(),
            "pH à 20°C": entry_ph_20c.get(),
        "Site d’application-1": type_produit_data[2],
        "Mode d’application-1": type_produit_data[3],
        "Quantité appliquée-1": type_produit_data[4],
        "Facteur de rétention-1": type_produit_data[5],
        "Durée d’application-1": type_produit_data[6],
        "Durée d’utilisation-1": type_produit_data[7],
        "Temps d’exposition-1": type_produit_data[8],
        "Fréquence d’utilisation-1": type_produit_data[9],
        "Surface d’application-1": type_produit_data[10],
        "VENH-1": type_produit_data[11],
        "Voie principale d’exposition-1": type_produit_data[12],
        "Voies secondaires d’exposition-1": type_produit_data[13],
        "Présence de nanomatériaux-1": type_produit_data[14],
        "Densité à 20°C": entry_densite_20c.get(),
        "Indice de réfraction à 20°C": entry_indice_refraction_20c.get(),
        "Point éclair": entry_point_eclair.get(),
        "Point de fusion (melting point)": entry_point_fusion.get(),
        "T° d’auto-inflammation (auto ignition)": entry_auto_inflammation.get(),
        #"T° d’ébullition (boiling point)": entry_ebullition.get(),
        "Acidité (% d’acide oléique)": entry_acidite.get(),
        "Indice de peroxyde": entry_indice_peroxyde.get(),
        "Solubilité dans/miscibilité à 20°C": entry_solubilite.get(),
        "Viscosité": entry_viscosite.get(),
        "Activité de l'eau": entry_activite_eau.get(),
        "Conditionnement et présentation": entry_conditionnement_et_presentation.get(),
        "Capacité": entry_capacite.get(),
        "Stockage": combobox_stockage.get(),
        "Date de mise sur le marché du premier lot": date_mise_sur_marche_du_premier_lot.get_date(),
        "Restrictions cosmétiques / opinions SCCS": text_restrictions_cosmetiques.get("1.0", tk.END).strip(),
        "DDM": combobox_ddm.get(),
        "Formulation 1": combobox_Formulation_1.get(),
        "Cotation 1": combobox_Cotation_1.get(),
        "Interface produit/environnement 2": combobox_interface_produit.get(),
        "Cotation 2": combobox_Cotation_2.get(),
        "Durée d’utilisation 3": combobox_duree_utilisation_3.get(),
        "Cotation 3": combobox_Cotation_3.get(),
        "Zone d’application 4": combobox_zone_application_4.get(),
        "Cotation 4": combobox_Cotation_4.get(),
        "Public": combobox_public.get(),
        "Cotation 5": combobox_Cotation_5.get(),
        # "Risque théorique": entry_risque_theorique.get(),
        "RT": combobox_rt.get(),
        "PAO": combobox_pao.get(),
        "PAO retenue": combobox_pao_retenue.get(),
        "Analyses": text_analyses.get("1.0", tk.END).strip(),
        "Conclusion": combobox_conclusion_1.get(),
        "Risque microbiologique": combobox_risque_microbiologique.get(),
        "Argumentation": checkbox_argumentation_1.get() or checkbox_argumentation_2.get() or checkbox_argumentation_3.get() or entry_argumentation.get(),
        "Fonction": entry_fonction.get(),
        "Mode d’emploi": entry_mode_emploi.get(),
        "Précautions d’emploi et restrictions d’usage": text_precautions_emploi_et_restrictions_usage.get("1.0",tk.END).strip(),
        #"Hydroxyde de sodium": combobox_hydroxyde_de_sodium.get(),

        }
    inserer_produit(**data_produit)
    messagebox.showinfo("Succès", "Entrée ajoutée à la base de données avec succès!")

    # Recupérer les données du formulaire de la partie client
    merged_data_client = {
            "Nom de l'entreprise": entry_nom_de_entreprise.get(),
            "Nom du fabricant": entry_nom_du_fabricant.get(),
            "Adresse du fabricant": entry_adresse_du_fabricant.get(),
            "SIRET du fabricant": entry_siret_du_fabricant.get(),
            "Nom du conditionneur": entry_nom_du_conditionneur.get(),
            "Adresse du conditionneur": entry_adresse_du_conditionneur.get(),
            "SIRET du conditionneur": entry_siret_du_conditionneur.get(),
            "Nom du distributeur": entry_nom_du_distributeur.get(),
            "Adresse du distributeur": entry_adresse_du_distributeur.get(),
            "SIRET du distributeur": entry_siret_du_distributeur.get(),
            "Nom de la personne responsable": entry_nom_de_la_personne_responsable.get(),
            "Adresse de la personne responsable": entry_adresse_de_la_personne_responsable.get(),
            "SIRET de la personne responsable": entry_siret_de_la_personne_responsable.get()
        }
    # Insérer les données fusionnées dans la table "client"
    inserer_client(**merged_data_client)
    '''else:
        # Gérer le cas où aucune donnée n'est récupérée depuis "typeProduit"
        print("No data found for the selected product type.")'''

    # Afficher le message de réussite
    messagebox.showinfo("Succès", "Entrée ajoutée à la base de données avec succès!")
    # Effacer les champs du formulaire après la soumission
    #effacer_champs_formulaire()
'''
def effacer_champs_formulaire():
    entry_date_de_redaction_rapport.set_date(datetime.date.today())  # Effacer la date en la définissant sur la date actuelle  # Effacer la date
    entry_etude.delete(0, tk.END)
    entry_denomination_commerciale_du_produit.delete(0, tk.END)
    entry_denomination_commerciale_declinaison.delete(0, tk.END)
    entry_reference_du_produit_evalue.delete(0, tk.END)
    combobox_type_de_produit.set("---")
    entry_contenant_et_type_de_conditionnement.delete(0, tk.END)
    entry_allegation_sante.delete(0, tk.END)
    combobox_population_cible.set("---")
    combobox_circuit_de_distribution.set("---")
    combobox_description_produit.set("---")
    entry_aspect.delete(0, tk.END)
    entry_couleur.delete(0, tk.END)
    combobox_odeur.set("---")
    entry_ph_20c.delete(0, tk.END)
    entry_densite_20c.delete(0, tk.END)
    entry_indice_refraction_20c.delete(0, tk.END)
    entry_point_eclair.delete(0, tk.END)
    entry_point_fusion.delete(0, tk.END)
    entry_auto_inflammation.delete(0, tk.END)
    entry_ebullition.delete(0, tk.END)
    entry_acidite.delete(0, tk.END)
    entry_indice_peroxyde.delete(0, tk.END)
    entry_solubilite.delete(0, tk.END)
    entry_viscosite.delete(0, tk.END)
    entry_activite_eau.delete(0, tk.END)
    entry_conditionnement_et_presentation.delete(0, tk.END)
    entry_capacite.delete(0, tk.END)
    combobox_stockage.set("---")
    text_restrictions_cosmetiques.delete("1.0", tk.END)
    combobox_ddm.set("---")
    combobox_Formulation_1.set("---")
    combobox_Cotation_1.set("---")
    combobox_interface_produit.set("---")
    combobox_Cotation_2.set("---")
    combobox_duree_utilisation_3.set("---")
    combobox_Cotation_3.set("---")
    combobox_zone_application_4.set("---")
    combobox_Cotation_4.set("---")
    combobox_public.set("---")
    combobox_Cotation_5.set("---")
    combobox_rt.set("---")
    combobox_pao.set("---")
    combobox_pao_retenue.set("---")
    text_analyses.delete("1.0", tk.END)
    combobox_conclusion_1.set("---")
    combobox_risque_microbiologique.set("---")
    checkbox_argumentation_1.deselect()
    checkbox_argumentation_2.deselect()
    checkbox_argumentation_3.deselect()
    entry_argumentation.delete(0, tk.END)
    entry_fonction.delete(0, tk.END)
    entry_mode_emploi.delete(0, tk.END)
    text_precautions_emploi_et_restrictions_usage.delete("1.0", tk.END)
    combobox_hydroxyde_de_sodium.set("---")
    entry_x_informations_sur_le_produit_cosmetique.delete(0, tk.END)
    checkbox_nom_raison_sociale_1.deselect()
    checkbox_nom_raison_sociale_2.deselect()
    entry_pays_origine.delete(0, tk.END)
    checkbox_pays_origine.deselect()
    checkbox_contenu_1.deselect()
    checkbox_contenu_2.deselect()
    checkbox_symbole_date_durabilite_minimale_1.deselect()
    checkbox_symbole_date_durabilite_minimale_2.deselect()
    checkbox_precautions_particulieres_emploi_1.deselect()
    checkbox_precautions_particulieres_emploi_2.deselect()
    checkbox_numero_de_lot_de_fabrication_1.deselect()
    checkbox_numero_de_lot_de_fabrication_2.deselect()
    checkbox_fonction_du_produit_1.deselect()
    checkbox_fonction_du_produit_2.deselect()
    checkbox_liste_des_ingredients_1.deselect()
    checkbox_liste_des_ingredients_2.deselect()
    entry_langue.delete(0, tk.END)
    entry_liste_1.delete(0, tk.END)
    entry_liste_2.delete(0, tk.END)
    checkbox_bio_1.deselect()
    checkbox_bio_2.deselect()
    combobox_allergenes.set("---")
    entry_allergenes.delete(0, tk.END)
    text_recommandations.delete("1.0", tk.END)
    text_ccl_microbio.delete("1.0", tk.END)
    text_fabricant.delete("1.0", tk.END)
    text_description.delete("1.0", tk.END)
    text_restrictions_cosmetiques_opinions_SCCS.delete("1.0", tk.END)
    combobox_impuretes.set("---")
    combobox_Allergenes.set("---")
    combobox_produit_rincer.set("---")
    entry_produit_rincer.delete(0, tk.END)
    informations_mos.set("---")
    combobox_conclusion_fin.set("---")
    entry_date_de_redaction_rapport_final.delete(0, tk.END)
    date_de_redaction_rapport_final.set_date(datetime.date.today())
    # Effacer les champs relatifs aux informations du client
    entry_nom_de_entreprise.delete(0, tk.END)
    entry_nom_du_fabricant.delete(0, tk.END)
    entry_adresse_du_fabricant.delete(0, tk.END)
    entry_siret_du_fabricant.delete(0, tk.END)
    entry_nom_du_conditionneur.delete(0, tk.END)
    entry_adresse_du_conditionneur.delete(0, tk.END)
    entry_siret_du_conditionneur.delete(0, tk.END)
    entry_nom_du_distributeur.delete(0, tk.END)
    entry_adresse_du_distributeur.delete(0, tk.END)
    entry_siret_du_distributeur.delete(0, tk.END)
    entry_nom_de_la_personne_responsable.delete(0, tk.END)
    entry_adresse_de_la_personne_responsable.delete(0, tk.END)
    entry_siret_de_la_personne_responsable.delete(0, tk.END)'''
'''
# ------------------------------------- [ FONCTION AUTOCOMPLETION ] -----------------------------------------------------------------


# Boîte de dialogue avec fonction d'autocomplétion pour sélectionner une dénomination commerciale lors de l'export Excel.
class BoiteDialogueAutocomplete(simpledialog.Dialog):
    def __init__(self, parent, titre, invite, noms):
        self.invite = invite
        self.noms = noms
        simpledialog.Dialog.__init__(self, parent, title=titre)

    def body(self, parent):
        # Affiche une étiquette avec l'invite spécifiée.
        ttk.Label(parent, text=self.invite).pack(padx=5, pady=5)

        # Crée une combobox avec les noms fournis pour l'autocomplétion.
        self.entry = ttk.Combobox(parent, values=self.noms)
        self.entry.pack(padx=5, pady=5)

        return self.entry  # Met le focus initial sur la combobox

    def apply(self):
        # Enregistre le résultat comme la valeur sélectionnée dans la combobox
        self.result = self.entry.get()


def get_all_denominations():
    conn = sqlite3.connect(chemin_db)
    curseur = conn.cursor()
    curseur.execute("SELECT denomination_commerciale FROM Produits")
    denominations = [row[0] for row in curseur.fetchall()]
    conn.close()
    return denominations


def ouvrir_boite_autocomplete():
    denominations = get_all_denominations()
    boite = BoiteDialogueAutocomplete(app, "Sélectionner une dénomination", "Choisissez une dénomination :",
                                      denominations)
    if boite.result:
        messagebox.showinfo("Sélection", f"Vous avez sélectionné : {boite.result}")
'''
def exporter_en_excel():
    # Charger le fichier Excel existant
    chemin_fichier_excel = 'TABLEAU GENERAL MODELE V2.xlsx'
    df = pd.read_excel(chemin_fichier_excel,engine='openpyxl')

    # Récupérer les données saisies dans le formulaire pour la table Produits
    data_produit = {
        "Date de la rédaction du rapport": entry_date_de_redaction_rapport.get_date(),
        "Étude": entry_etude.get(),
        "Dénomination commerciale du produit": entry_denomination_commerciale_du_produit.get(),
        "Dénomination commerciale (déclinaison)": entry_denomination_commerciale_declinaison.get(),
        "Référence du produit évalué": entry_reference_du_produit_evalue.get(),
        "Type de produit": combobox_type_de_produit.get(),
        "Contenant et type de conditionnement": entry_contenant_et_type_de_conditionnement.get(),
        "Allégations santé": entry_allegation_sante.get(),
        "Population cible": combobox_population_cible.get(),
        "Circuit de distribution": combobox_circuit_de_distribution.get(),
        "Description du produit": combobox_description_produit.get(),
        "Aspect": entry_aspect.get(),
        "Couleur": entry_couleur.get(),
        "Odeur": combobox_odeur.get(),
        "pH à 20°C": entry_ph_20c.get(),
        "Densité à 20°C": entry_densite_20c.get(),
        "Indice de réfraction à 20°C": entry_indice_refraction_20c.get(),
        "Point éclair": entry_point_eclair.get(),
        "Point de fusion (melting point)": entry_point_fusion.get(),
        "T° d’auto-inflammation (auto ignition)": entry_auto_inflammation.get(),
        "T° d’ébullition (boiling point)": entry_ebullition.get(),
        "Acidité (% d’acide oléique)": entry_acidite.get(),
        "Indice de peroxyde": entry_indice_peroxyde.get(),
        "Solubilité dans/miscibilité à 20°C": entry_solubilite.get(),
        "Viscosité": entry_viscosite.get(),
        "Activité de l'eau": entry_activite_eau.get(),
        "Conditionnement et présentation": entry_conditionnement_et_presentation.get(),
        "Capacité": entry_capacite.get(),
        "Stockage": combobox_stockage.get(),
        "Date de mise sur le marché du premier lot": date_mise_sur_marche_du_premier_lot.get_date(),
        "Restrictions cosmétiques / opinions SCCS": text_restrictions_cosmetiques.get("1.0", tk.END).strip(),
        "DDM": combobox_ddm.get(),
        "Formulation 1": combobox_Formulation_1.get(),
        "Cotation 1": combobox_Cotation_1.get(),
        "Interface produit/environnement 2": combobox_interface_produit.get(),
        "Cotation 2": combobox_Cotation_2.get(),
        "Durée d’utilisation 3": combobox_duree_utilisation_3.get(),
        "Cotation 3": combobox_Cotation_3.get(),
        "Zone d’application 4": combobox_zone_application_4.get(),
        "Cotation 4": combobox_Cotation_4.get(),
        "Public": combobox_public.get(),
        "Cotation 5": combobox_Cotation_5.get(),
        "RT": combobox_rt.get(),
        "PAO": combobox_pao.get(),
        "PAO retenue": combobox_pao_retenue.get(),
        "Analyses": text_analyses.get("1.0", tk.END).strip(),
        "Conclusion": combobox_conclusion_1.get(),
        "Risque microbiologique": combobox_risque_microbiologique.get(),
        "Argumentation": checkbox_argumentation_1.get() or checkbox_argumentation_2.get() or checkbox_argumentation_3.get() or entry_argumentation.get(),
        "Fonction": entry_fonction.get(),
        "Mode d’emploi": entry_mode_emploi.get(),
        "Précautions d’emploi et restrictions d’usage": text_precautions_emploi_et_restrictions_usage.get("1.0", tk.END).strip(),
        "Hydroxyde de sodium": combobox_hydroxyde_de_sodium.get(),
        "X. Informations sur le produit cosmétique": entry_x_informations_sur_le_produit_cosmetique.get(),
        "Nom / raison sociale": checkbox_nom_raison_sociale_1.get() or checkbox_nom_raison_sociale_2.get(),
        "Pays d’origine": checkbox_pays_origine.get() or entry_pays_origine.get(),
        "Contenu": checkbox_contenu_1.get() or checkbox_contenu_2.get(),
        "Symbole / Date de durabilité minimale": checkbox_symbole_date_durabilite_minimale_1.get() or checkbox_symbole_date_durabilite_minimale_2.get(),
        "Précautions particulières d’emploi": checkbox_precautions_particulieres_emploi_1.get() or checkbox_precautions_particulieres_emploi_2.get(),
        "Numéro de lot de fabrication": checkbox_numero_de_lot_de_fabrication_1.get() or checkbox_numero_de_lot_de_fabrication_2.get(),
        "Fonction du produit": checkbox_fonction_du_produit_1.get() or checkbox_fonction_du_produit_2.get(),
        "Liste des ingrédients": checkbox_liste_des_ingredients_1.get() or checkbox_liste_des_ingredients_2.get(),
        "Langue": entry_langue.get(),
        "Liste 1": entry_liste_1.get(),
        "Liste 2": entry_liste_2.get(),
        "BIO *": checkbox_bio_1.get() or checkbox_bio_2.get(),
        "ALLERGENES **": combobox_allergenes.get() or entry_allergenes.get(),
        "Recommandations": text_recommandations.get("1.0", tk.END).strip(),
        "CCL Microbio": text_ccl_microbio.get("1.0", tk.END).strip(),
        "Fabricant / Distributeur": text_fabricant.get("1.0", tk.END).strip(),
        "Description (conditionnement)": text_description.get("1.0", tk.END).strip(),
        "Impuretés": combobox_impuretes.get(),
        "Allergènes": combobox_allergenes.get() or entry_allergenes.get(),
        "Produit à rincer": combobox_produit_rincer.get() or entry_produit_rincer.get(),
        "Informations MoS": informations_mos.get(),
        "Conclusion finale": combobox_conclusion_fin.get(),
        "Date de rédaction du rapport final": date_de_redaction_rapport_final.get_date()
    }
    # Récupérer les données saisies dans le formulaire pour la table Clients
    data_client = {
        "Nom de l'entreprise": entry_nom_de_entreprise.get(),
        "Nom du fabricant": entry_nom_du_fabricant.get(),
        "Adresse du fabricant": entry_adresse_du_fabricant.get(),
        "SIRET du fabricant": entry_siret_du_fabricant.get(),
        "Nom du conditionneur": entry_nom_du_conditionneur.get(),
        "Adresse du conditionneur": entry_adresse_du_conditionneur.get(),
        "SIRET du conditionneur": entry_siret_du_conditionneur.get(),
        "Nom du distributeur": entry_nom_du_distributeur.get(),
        "Adresse du distributeur": entry_adresse_du_distributeur.get(),
        "SIRET du distributeur": entry_siret_du_distributeur.get(),
        "Nom de la personne responsable": entry_nom_de_la_personne_responsable.get(),
        "Adresse de la personne responsable": entry_adresse_de_la_personne_responsable.get(),
        "SIRET de la personne responsable": entry_siret_de_la_personne_responsable.get()
    }

    # Combiner les données des deux tables
    data_combined = {**data_produit, **data_client}

    # Ajouter les données combinées sous forme de nouvelle ligne au DataFrame
    df = df.append(data_combined, ignore_index=True)

    # Enregistrer le DataFrame mis à jour dans le fichier Excel
    df.to_excel(chemin_fichier_excel, index=False,engine='openpyxl')
    messagebox.showinfo("Export", "Les données ont été exportées avec succès vers le fichier Excel.")

#------------------------------------- [ CODE POUR LES CHAMPS DE SAISIE ] -----------------------------------------------------------------
# Initialisation du formulaire
creer_table_produits()
creer_table_clients()
app = CTk.CTk()
app.geometry("1500*900")
app.title("Formulaire Produit Cosmétique")

#Définir le mode d'apparence
CTk.set_appearance_mode("dark")

# Créer un cadre principal
main_frame = CTk.CTkScrollableFrame(app)
main_frame.pack(pady = 20, padx = 60, fill = "both", expand = True)
# Créer un cadre pour les champs du client
client_frame = CTk.CTkFrame(main_frame,fg_color="white")
client_frame.pack(pady=20, padx=10, fill="x")

ajouter_combobox_clients()

entry_nom_de_entreprise = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Nom de l'entreprise",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_nom_de_entreprise.pack(pady = 5, padx = 10,anchor ='w')

entry_nom_du_fabricant = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Nom du fabricant",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_nom_du_fabricant.pack(pady = 5, padx = 10,anchor ='w')

entry_adresse_du_fabricant = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Adresse du fabricant",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_adresse_du_fabricant.pack(pady = 5, padx = 10,anchor ='w')

entry_siret_du_fabricant = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="SIRET du fabricant",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_siret_du_fabricant.pack(pady = 5, padx = 10,anchor ='w')

entry_nom_du_conditionneur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Nom du conditionneur",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_nom_du_conditionneur.pack(pady = 5, padx = 10,anchor ='w')

entry_adresse_du_conditionneur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Adresse du conditionneur",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_adresse_du_conditionneur.pack(pady = 5, padx = 10,anchor ='w')

entry_siret_du_conditionneur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="SIRET du conditionneur",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_siret_du_conditionneur .pack(pady = 5, padx = 10,anchor ='w')

entry_nom_du_distributeur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Nom du distributeur ",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_nom_du_distributeur .pack(pady = 5, padx = 10,anchor ='w')

entry_adresse_du_distributeur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Adresse du distributeur ",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_adresse_du_distributeur .pack(pady = 5, padx = 10,anchor ='w')

entry_siret_du_distributeur = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="SIRET du distributeur ",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_siret_du_distributeur .pack(pady = 5, padx = 10,anchor ='w')

entry_nom_de_la_personne_responsable = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Nom de la personne responsable",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_nom_de_la_personne_responsable .pack(pady = 5, padx = 10,anchor ='w')

entry_adresse_de_la_personne_responsable = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="Adresse de la personne responsable ",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_adresse_de_la_personne_responsable .pack(pady = 5, padx = 10,anchor ='w')

entry_siret_de_la_personne_responsable = CTk.CTkEntry(master = client_frame, width = 2200, placeholder_text="SIRET de la personne responsable ",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_siret_de_la_personne_responsable .pack(pady = 5, padx = 10,anchor ='w')

#Créer un cadre pour les champs du produit
produit_frame = CTk.CTkFrame(main_frame,fg_color="white")
produit_frame.pack(pady=20, padx=10, fill= "x")

#Champs du produit

date_de_redaction_rapport_label = CTk.CTkLabel(produit_frame, text="Date de la rédaction du rapport", font = ('Century Gothic',15),text_color="gray30")
date_de_redaction_rapport_label.pack(pady=5, padx=10,anchor = 'w')
entry_date_de_redaction_rapport = DateEntry(produit_frame, date_pattern = 'dd/mm/yyyy')
entry_date_de_redaction_rapport.pack(pady = 10, padx=20, anchor = 'w')

entry_etude = CTk.CTkEntry(master = produit_frame, width = 2200, placeholder_text="Etude",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_etude.pack(pady = 5, padx = 10,anchor ='w')

entry_denomination_commerciale_du_produit = CTk.CTkEntry(master = produit_frame,width= 2200, placeholder_text="dénomination commerciale du produit",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_denomination_commerciale_du_produit.pack(pady = 5, padx = 10,anchor ='w')

entry_denomination_commerciale_declinaison = CTk.CTkEntry(master = produit_frame,width = 220,placeholder_text="dénomination commerciale déclinaison",fg_color="DarkOrchid4",placeholder_text_color="white" )
entry_denomination_commerciale_declinaison.pack(pady=5, padx=10, fill="x")

'''
autocomplete_button = CTkButton(main_frame, text="Sélectionner Dénomination", command=ouvrir_boite_autocomplete, fg_color="purple3", text_color='White')
autocomplete_button.pack(pady=10, padx=15, anchor='w')'''

entry_reference_du_produit_evalue = CTk.CTkEntry(master=produit_frame,width = 220,placeholder_text="Référence de produit évalué",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_reference_du_produit_evalue.pack(pady=5, padx=10, fill="x")

label_type_produit = CTk.CTkLabel(produit_frame, text=" Type de produit",font = ('Century Gothic',15),text_color="gray30")
label_type_produit.pack(pady=5, padx=10, anchor="w")
combobox_type_de_produit = CTk.CTkComboBox(produit_frame, values=["Deo non spray", "Dentifrice", "Eau dentifrice","Aprés-shampooing","Shampooing","Teintures capillaires oxydatives / permanentes","Teintures capillaires semi-permanentes et lotions","Produits coiffants","Produits coiffants non rincé","Mascara","Deodorant aerosol spray sans ethanol","Parfum en spray avec ethanol","Eau de toilette spray avec ethanol","Eyeliner","Crème pour les mains rincé","Lavage à la main au savon","Crème pour les mains","Lubrifiant","Lotion pour le corps rincé","Huiles pour le bain, sels, etc","Gel douche","Lotion pour le corps","Crème pour le visage rincé","Fond de teint liquide","Démaquillant","Crème pour le visage","Maquillage des yeux"],text_color='White',fg_color='DarkOrchid4')
combobox_type_de_produit.pack(pady=5, padx=10, fill="x")

entry_contenant_et_type_de_conditionnement = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Contenant et type de conditionnement",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_contenant_et_type_de_conditionnement.pack(pady=5, padx=10, fill="x")

entry_allegation_sante = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Allegation santé ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_allegation_sante.pack(pady=5, padx=10, fill="x")

label_population_cible = CTk.CTkLabel(produit_frame, text=" Population cible",font = ('Century Gothic',15),text_color="gray30")
label_population_cible.pack(pady=5, padx=10, anchor="w")
combobox_population_cible = CTk.CTkComboBox(produit_frame, values=["Adultes", "Adultes sauf femmes enceintes ou allaitantes", "Enfants entre 3 et 12 ans ","Nourissons"],fg_color = "DarkOrchid4",text_color="White")
combobox_population_cible.pack(pady=5, padx=10, fill="x")

label_circuit_de_distribution = CTk.CTkLabel(produit_frame, text="Circuit de distribution",font = ('Century Gothic',15),text_color="gray30")
label_circuit_de_distribution.pack(pady=5, padx=10, anchor="w")
combobox_circuit_de_distribution = CTk.CTkComboBox(produit_frame, values=["Détaillants et Internet","Détaillants","Internet"],fg_color = "DarkOrchid4",text_color="White")
combobox_circuit_de_distribution.pack(pady=5, padx=10, fill="x")

label_description_produit = CTk.CTkLabel(produit_frame, text="Description du produit",font = ('Century Gothic',15),text_color="gray30")
label_description_produit.pack(pady=5, padx=10, anchor="w")
combobox_description_produit = CTk.CTkComboBox(produit_frame, values=["Produit rincé","Produit non rincé","Produit considéré comme rincé","Produit concidéré comme non rincé"],fg_color = "DarkOrchid4",text_color="White")
combobox_description_produit.pack(pady=5, padx=10, fill="x")

entry_aspect = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Aspect ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_aspect.pack(pady=5, padx=10, fill="x")

entry_couleur = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Couleur ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_aspect.pack(pady=5, padx=10, fill="x")

label_odeur = CTk.CTkLabel(produit_frame, text="odeur",font = ('Century Gothic',15),text_color="gray30")
label_odeur.pack(pady=5, padx=10, anchor="w")
combobox_odeur = CTk.CTkComboBox(produit_frame, values=["Caractéristique de la /des compositions(s) aromatique(s)/parfumante(s) utilisé(es)","Caractéristiques de la/des matiére(s) prmiére(s) utilisée(s)","sans odeur"],fg_color = "DarkOrchid4",text_color="White")
combobox_odeur.pack(pady=5, padx=10, fill="x")

entry_ph_20c = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="pH à 20°C ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_ph_20c.pack(pady=5, padx=10, fill="x")

entry_densite_20c = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Densité à 20°C ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_densite_20c.pack(pady=5, padx=10, fill="x")

entry_indice_refraction_20c = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Indice de réfraction à 20°C ",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_indice_refraction_20c.pack(pady=5, padx=10, fill="x")

entry_point_eclair = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Point éclair",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_point_eclair.pack(pady=5, padx=10, fill="x")

entry_point_fusion = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Point de fusion(melting point)",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_point_fusion.pack(pady=5, padx=10, fill="x")

entry_auto_inflammation = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="T° d’auto-inflammation (auto ignition)",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_auto_inflammation.pack(pady=5, padx=10, fill="x")

entry_ebullition = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="T° d’ébulltion (boiling point)",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_ebullition.pack(pady=5, padx=10, fill="x")

entry_acidite = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Acidité (% d’acide oléique)",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_acidite.pack(pady=5, padx=10, fill="x")

entry_indice_peroxyde = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Indice de peroxyde",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_indice_peroxyde.pack(pady=5, padx=10, fill="x")

entry_solubilite = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Solubilité dans/miscibilité à 20°C",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_solubilite.pack(pady=5, padx=10, fill="x")

entry_viscosite = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Viscosité",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_viscosite.pack(pady=5, padx=10, fill="x")

entry_activite_eau = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Activité de l'eau",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_activite_eau.pack(pady=5, padx=10, fill="x")

entry_conditionnement_et_presentation = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Conditionnement et présentation",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_conditionnement_et_presentation.pack(pady=5, padx=10, fill="x")

entry_capacite = CTk.CTkEntry(produit_frame,width = 220,placeholder_text="Capacité",fg_color="DarkOrchid4",placeholder_text_color="white")
entry_capacite.pack(pady=5, padx=10, fill="x")

label_stockage = CTk.CTkLabel(produit_frame, text="Stockage",font = ('Century Gothic',15),text_color="gray30")
label_stockage.pack(pady=5, padx=10, anchor="w")
combobox_stockage = CTk.CTkComboBox(produit_frame, values=["Conserver dans un endroit frais et sec, à l'abri de la lumière et de la chaleur","Conserver sur un porte savon après utilisation"],fg_color = "DarkOrchid4",text_color="White")
combobox_stockage.pack(pady=5, padx=10, fill="x")

date_mise_sur_marche_du_premier_lot = CTk.CTkLabel(produit_frame, text="Date de mise sur le marché du premier lot", font = ('Century Gothic',15),text_color="gray30")
date_mise_sur_marche_du_premier_lot.pack(pady=5, padx=10,anchor = 'w')
date_mise_sur_marche_du_premier_lot = DateEntry(produit_frame, date_pattern = 'dd/mm/yyyy')
date_mise_sur_marche_du_premier_lot.pack(pady = 10, padx=20, anchor = 'w')

# Variable pour stocker le label de l'image
image_label = None

def select_image():
    global image_label
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
    if file_path:
        load_image(file_path)

def load_image(file_path):
    global image_label
    # Ouvrir l'image avec PIL
    image = Image.open(file_path)

    # Redimensionner l'image si nécessaire
    image = image.resize((300, 300), Image.ANTIALIAS)

    # Convertir l'image en objet PhotoImage pour Tkinter
    photo = ImageTk.PhotoImage(image)

    if image_label is None:
        image_label = tk.Label(produit_frame, image=photo)
        image_label.image = photo  # Conserver une référence pour éviter la suppression de l'image
        image_label.pack()
    else:
        image_label.configure(image=photo)
        image_label.image = photo  # Mettre à jour la référence

# Bouton pour sélectionner l'image
select_image_button = CTkButton(produit_frame, text="Image Présentation", command=select_image,fg_color="purple3",text_color='White')
select_image_button.pack(pady=10,padx=15,anchor='w')

label_restrictions_cosmetiques = CTk.CTkLabel(produit_frame, text="Restrictions cosmétiques / opinions SCCS",font = ('Century Gothic',15),text_color="gray30")
label_restrictions_cosmetiques.pack(pady=5, padx=10, anchor="w")
text_restrictions_cosmetiques = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_restrictions_cosmetiques.pack(pady=5,padx=10,anchor="w")

label_ddm = CTk.CTkLabel(produit_frame, text="DDM",font = ('Century Gothic',15),text_color="gray30")
label_ddm.pack(pady=5, padx=10, anchor="w")
combobox_ddm = CTk.CTkComboBox(produit_frame, values=["La durabilité du produit cosmétique excède 30 mois, l'indication de la date de durabilité n'est pas obligatoire.","Compte tenu notamment de l'absence d'eau et de l'activité de l'eau Aw (théorique) du produit fini, la formulation présente une stabilité élevée face à la contamination microbienne."],fg_color = "DarkOrchid4",text_color="White")
combobox_ddm.pack(pady=5, padx=10, fill="x")

label_Formulation_1 = CTk.CTkLabel(produit_frame, text="Formulation 1",font = ('Century Gothic',15),text_color="gray30")
label_Formulation_1.pack(pady=5, padx=10, anchor="w")
combobox_Formulation_1 = CTk.CTkComboBox(produit_frame, values=["Compte tenu notamment de l'efficacité du système conservateur, la formule présente une stabilité élevée face à la contamination microbienne.","Compte tenu notamment de l'efficacité du système conservateur et du conditionnement, la formule présente une stabilité élevée face à la contamination microbienne.","Compte tenu notamment de la concentration en alcool dans le produit fini, la formulation présente une stabilité élevée face à la contamination microbienne","Compte tenu notamment de l'efficacité du système conservateur et du conditionnement, la formule présente une stabilité élevée face à la contamination microbienne.","Compte tenu notamment de la concentration en alcool dans le produit fini, la formulation présente une stabilité élevée face à la contamination microbienne.","Compte tenu notamment de la concentration en alcool dans le produit fini, la formulation présente une stabilité élevée face à la contamination microbienne.""Compte tenu notamment de la faible quantité d'eau et de l'activité de l'eau Aw (théorique) du produit fini, la formulation présente une stabilité élevée face à la contamination microbienne","Compte tenu notamment de la présence d'alcool, de l'absence d'eau et de l'activité de l'eau Aw (théorique) du produit fini, la formulation présente une stabilité élevée face à la contamination microbienne","Compte tenu notamment de l'absence d'eau et de l'activité de l'eau Aw (théorique) du produit fini, la formulation présente une stabilité élevée face à la contamination microbienne"],fg_color = "DarkOrchid4",text_color="White")
combobox_Formulation_1.pack(pady=5, padx=10, fill="x")

label_Cotation_1 = CTk.CTkLabel(produit_frame, text="Cotation 1",font = ('Century Gothic',15),text_color="gray30")
label_Cotation_1.pack(pady=5, padx=10, anchor="w")
combobox_Cotation_1 = CTk.CTkComboBox(produit_frame, values=["1","2","3","4"],fg_color = "DarkOrchid4",text_color="White")
combobox_Cotation_1.pack(pady=5, padx=10, fill="x")

label_interface_produit = CTk.CTkLabel(produit_frame, text="Interface produit/environnement 2",font = ('Century Gothic',15),text_color="gray30")
label_interface_produit.pack(pady=5, padx=10, anchor="w")
combobox_interface_produit = CTk.CTkComboBox(produit_frame, values=["Compte tenu du conditionnement, mais aussi de l’utilisation fréquente possible du produit, ce paramètre présente un risque élevé.","Compte tenu du conditionnement, mais aussi de l’utilisation fréquente possible du produit, ce paramètre présente un risque élevé.","Compte tenu du conditionnement et de l’utilisation possible du produit, ce paramètre présente un risque très faible"],fg_color = "DarkOrchid4",text_color="White")
combobox_interface_produit.pack(pady=5, padx=10, fill="x")

label_Cotation_2 = CTk.CTkLabel(produit_frame, text="Cotation 2",font = ('Century Gothic',15),text_color="gray30")
label_Cotation_2.pack(pady=5, padx=10, anchor="w")
combobox_Cotation_2 = CTk.CTkComboBox(produit_frame, values=["1","2","3","4"],fg_color = "DarkOrchid4",text_color="White")
combobox_Cotation_2.pack(pady=5, padx=10, fill="x")

label_duree_utilisation_3 = CTk.CTkLabel(produit_frame, text="Durée d’utilisation 3",font = ('Century Gothic',15),text_color="gray30")
label_duree_utilisation_3.pack(pady=5, padx=10, anchor="w")
combobox_duree_utilisation_3 = CTk.CTkComboBox(produit_frame, values=["D'après la fréquence d'utilisation et le conditionnement, la durée d’utilisation du produit est relativement courte, aussi le risque lié à ce paramètre est-il faible.","D'après la fréquence d'utilisation et le conditionnement, la durée d’utilisation du produit est relativement longue, aussi le risque lié à ce paramètre est-il élevé."],fg_color = "DarkOrchid4",text_color="White")
combobox_duree_utilisation_3.pack(pady=5, padx=10, fill="x")

label_Cotation_3 = CTk.CTkLabel(produit_frame, text="Cotation 3",font = ('Century Gothic',15),text_color="gray30")
label_Cotation_3.pack(pady=5, padx=10, anchor="w")
combobox_Cotation_3 = CTk.CTkComboBox(produit_frame, values=["1","2","3","4"],fg_color = "DarkOrchid4",text_color="White")
combobox_Cotation_3.pack(pady=5, padx=10, fill="x")

label_zone_application_4 = CTk.CTkLabel(produit_frame, text="Zone d’application 4",font = ('Century Gothic',15),text_color="gray30")
label_zone_application_4.pack(pady=5, padx=10, anchor="w")
combobox_zone_application_4 = CTk.CTkComboBox(produit_frame, values=["(Compte tenu de la zone d'application du produit, celui-ci peut entrer en contact avec les yeux. Le risque lié à ce paramètre est très élevé.","Compte tenu de la zone d'application du produit, celui-ci peut entrer en contact avec les muqueuses. Le risque lié à ce paramètre est élevé","Compte tenu de la zone d'application du produit, celui-ci peut entrer en contact avec les plis. Le risque lié à ce paramètre est faible"," Compte tenu de la zone d'application du produit, celui-ci peut entrer en contact avec les cheveux. Le risque lié à ce paramètre est très faible."],fg_color = "DarkOrchid4",text_color="White")
combobox_zone_application_4.pack(pady=5, padx=10, fill="x")

label_Cotation_4 = CTk.CTkLabel(produit_frame, text="Cotation 4",font = ('Century Gothic',15),text_color="gray30")
label_Cotation_4.pack(pady=5, padx=10, anchor="w")
combobox_Cotation_4 = CTk.CTkComboBox(produit_frame, values=["1","2","3","4"],fg_color = "DarkOrchid4",text_color="White")
combobox_Cotation_4.pack(pady=5, padx=10, fill="x")

label_public = CTk.CTkLabel(produit_frame, text="Public",font = ('Century Gothic',15),text_color="gray30")
label_public.pack(pady=5, padx=10, anchor="w")
combobox_public = CTk.CTkComboBox(produit_frame, values=["Le produit est principalement destiné à l’usage des nourissons. Le risque lié à ce paramètre est très élevé. ","Le produit est principalement destiné à l’usage des enfants entre 3 et 12 anss. Le risque lié à ce paramètre est élevé.","Le produit est principalement destiné à l’usage des adultes et des personnes âgées. Le risque lié à ce paramètre est faible.","Le produit est principalement destiné à l’usage des adultes. Le risque lié à ce paramètre est très faible"],fg_color = "DarkOrchid4",text_color="White")
combobox_public.pack(pady=5, padx=10, fill="x")

label_Cotation_5 = CTk.CTkLabel(produit_frame, text="Cotation 5",font = ('Century Gothic',15),text_color="gray30")
label_Cotation_5.pack(pady=5, padx=10, anchor="w")
combobox_Cotation_5 = CTk.CTkComboBox(produit_frame, values=["1","2","3","4"],fg_color = "DarkOrchid4",text_color="White")
combobox_Cotation_5.pack(pady=5, padx=10, fill="x")

label_rt = CTk.CTkLabel(produit_frame, text="RT",font = ('Century Gothic',15),text_color="gray30")
label_rt.pack(pady=5, padx=10, anchor="w")
combobox_rt = CTk.CTkComboBox(produit_frame, values=["si 1 ≤ RT ≤ 8, PAO ≤ 18 mois","si 8 < RT ≤ 28, PAO ≤ 12 mois ","si 28 < RT ≤ 48, PAO ≤ 6 mois","si 48 < RT, PAO non applicable"],fg_color = "DarkOrchid4",text_color="White")
combobox_rt.pack(pady=5, padx=10, fill="x")

label_pao = CTk.CTkLabel(produit_frame, text="PAO",font = ('Century Gothic',15),text_color="gray30")
label_pao.pack(pady=5, padx=10, anchor="w")
combobox_pao = CTk.CTkComboBox(produit_frame, values=["18 M","12 M "," 6 M"," PAO non applicable"],fg_color = "DarkOrchid4",text_color="White")
combobox_pao.pack(pady=5, padx=10, fill="x")

label_pao_retenue = CTk.CTkLabel(produit_frame, text="PAO retenue",font = ('Century Gothic',15),text_color="gray30")
label_pao_retenue.pack(pady=5, padx=10, anchor="w")
combobox_pao_retenue = CTk.CTkComboBox(produit_frame, values=["18 M","12 M "," 6 M"," PAO non applicable"],fg_color = "DarkOrchid4",text_color="White")
combobox_pao_retenue.pack(pady=5, padx=10, fill="x")

label_analyses = CTk.CTkLabel(produit_frame, text="Analyses",font = ('Century Gothic',15),text_color="gray30")
label_analyses.pack(pady=5, padx=10, anchor="w")
text_analyses = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_analyses.pack(pady=5,padx=10,anchor="w")

label_conclusion_1 = CTk.CTkLabel(produit_frame, text="Conclusion",font = ('Century Gothic',15),text_color="gray30")
label_conclusion_1.pack(pady=5, padx=10, anchor="w")
combobox_conclusion_1 = CTk.CTkComboBox(produit_frame, values=["Les résultats des essais de vieillissement accéléré - stabilité de la formule seule ne sont pas disponibles en totalité au moment de la rédaction du DIP et devront être confirmés ","Les résultats des essais de vieillissement accéléré - stabilité de la formule seule sont disponibles à 1, 2 et 3 mois au moment de la rédaction du DIP et ne sont pas conformes dans les différentes conditions. Les résultats ne sont pas acceptables. Ces résultats sont disponibles en annexe du DIP.","Les résultats des essais de vieillissement accéléré - stabilité de la formule seule sont disponibles à 1, 2 et 3 mois au moment de la rédaction du DIP et sont conformes dans les différentes conditions. Les résultats sont acceptables. Ces résultats sont disponibles en annexe du DIP."],fg_color = "DarkOrchid4",text_color="White")
combobox_conclusion_1.pack(pady=5, padx=10, fill="x")

label_risque_microbiologique = CTk.CTkLabel(produit_frame, text="Risque microbiologique",font = ('Century Gothic',15),text_color="gray30")
label_risque_microbiologique.pack(pady=5, padx=10, anchor="w")
combobox_risque_microbiologique = CTk.CTkComboBox(produit_frame, values=["Risque microbiologique maîtrisé"," Risque microbiologique non maîtrisé"],fg_color = "DarkOrchid4",text_color="White")
combobox_risque_microbiologique.pack(pady=5, padx=10, fill="x")

label_argumentation = CTk.CTkLabel(produit_frame, text="Argumentation",font = ('Century Gothic',15),text_color="gray30")
label_argumentation.pack(pady=5, padx=10, anchor="w")
checkbox_argumentation_1 = CTk.CTkCheckBox(produit_frame, text="Formule hostile au développement de micro-organismes", fg_color="DarkOrchid4", text_color="black")
checkbox_argumentation_1.pack(pady=5, padx=10, fill="x")
checkbox_argumentation_2 = CTk.CTkCheckBox(produit_frame, text="Analyse du risque microbiologique - Profil A (ISO 11930 :2012 – Evaluation de la protection antimicrobienne d'un produit cosmétique", fg_color="DarkOrchid4", text_color="black")
checkbox_argumentation_2.pack(pady=5, padx=10, fill="x")
checkbox_argumentation_3 = CTk.CTkCheckBox(produit_frame, text="Analyse du risque microbiologique - Profil B (ISO 11930 :2012 – Evaluation de la protection antimicrobienne d'un produit cosmétique", fg_color="DarkOrchid4", text_color="black")
checkbox_argumentation_3.pack(pady=5, padx=10, fill="x")
entry_argumentation = CTk.CTkEntry(master = produit_frame, width = 2200, placeholder_text="Autres",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_argumentation.pack(pady = 5, padx = 10,anchor ='w')

entry_fonction = CTk.CTkEntry(master = produit_frame, width = 2200, placeholder_text="Fonction",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_fonction.pack(pady = 5, padx = 10,anchor ='w')

entry_mode_emploi = CTk.CTkEntry(master = produit_frame, width = 2200, placeholder_text="Mode d’emploi",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_mode_emploi.pack(pady = 5, padx = 10,anchor ='w')

label_precautions_emploi_et_restrictions_usage = CTk.CTkLabel(produit_frame, text="Précautions d’emploi et restrictions d’usage",font = ('Century Gothic',15),text_color="gray30")
label_precautions_emploi_et_restrictions_usage.pack(pady=5, padx=10, anchor="w")
text_precautions_emploi_et_restrictions_usage = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_precautions_emploi_et_restrictions_usage.pack(pady=5,padx=10,anchor="w")

hydroxyde_de_sodium = CTk.CTkLabel(produit_frame, text="HYDROXYDE DE SODIUM+BK:BBO:BP",font = ('Century Gothic',15),text_color="gray30")
hydroxyde_de_sodium.pack(pady=5, padx=10, anchor="w")
combobox_hydroxyde_de_sodium = CTk.CTkComboBox(produit_frame, values=["","La valeur MoS pour HYDROXYDE DE SODIUM n’est pas pertinente car cet ingrédient est consommé pendant le processus de fabrication du produit fini et ne figure pas dans le produit fini."],fg_color = "DarkOrchid4",text_color="White")
combobox_hydroxyde_de_sodium.pack(pady=5, padx=10, fill="x")

entry_x_informations_sur_le_produit_cosmetique = CTk.CTkEntry(master = produit_frame, width = 2200, placeholder_text="X. INFORMATIONS SUR LE PRODUIT COSMETIQUE",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_x_informations_sur_le_produit_cosmetique.pack(pady = 5, padx = 10,anchor ='w')

nom_raison_sociale = CTk.CTkLabel(produit_frame, text="Nom / raison sociale / adresse de la personne responsable",font = ('Century Gothic',15),text_color="gray30")
nom_raison_sociale.pack(pady=5, padx=10, anchor="w")
checkbox_nom_raison_sociale_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_nom_raison_sociale_1.pack(pady=5, padx=10, fill="x")
checkbox_nom_raison_sociale_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_nom_raison_sociale_2.pack(pady=5, padx=10, fill="x")

nom_pays_origine = CTk.CTkLabel(produit_frame, text=" Pays d’origine (pour les produits cosmétiques importés) ",font = ('Century Gothic',15),text_color="gray30")
nom_pays_origine.pack(pady=5, padx=10, anchor="w")
entry_pays_origine = CTk.CTkEntry(master = produit_frame, width = 2200,fg_color="DarkOrchid4",placeholder_text_color="White")
entry_pays_origine.pack(pady = 5, padx = 10,anchor ='w')
checkbox_pays_origine = CTk.CTkCheckBox(produit_frame, text="non pertinent", fg_color="DarkOrchid4", text_color="black")
checkbox_pays_origine.pack(pady=5, padx=10, fill="x")

contenu = CTk.CTkLabel(produit_frame, text="CONTENU",font = ('Century Gothic',15),text_color="gray30")
contenu.pack(pady=5, padx=10, anchor="w")
checkbox_contenu_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_contenu_1.pack(pady=5, padx=10, fill="x")
checkbox_contenu_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_contenu_2.pack(pady=5, padx=10, fill="x")

symbole_date_durabilite_minimale = CTk.CTkLabel(produit_frame, text="Symbole / Date de durabilité minimale",font = ('Century Gothic',15),text_color="gray30")
symbole_date_durabilite_minimale.pack(pady=5, padx=10, anchor="w")
checkbox_symbole_date_durabilite_minimale_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_symbole_date_durabilite_minimale_1.pack(pady=5, padx=10, fill="x")
checkbox_symbole_date_durabilite_minimale_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_symbole_date_durabilite_minimale_2.pack(pady=5, padx=10, fill="x")

precautions_particulieres_emploi = CTk.CTkLabel(produit_frame, text="Précautions particulières d’emploi ",font = ('Century Gothic',15),text_color="gray30")
precautions_particulieres_emploi.pack(pady=5, padx=10, anchor="w")
checkbox_precautions_particulieres_emploi_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_precautions_particulieres_emploi_1.pack(pady=5, padx=10, fill="x")
checkbox_precautions_particulieres_emploi_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_precautions_particulieres_emploi_2.pack(pady=5, padx=10, fill="x")

numero_de_lot_de_fabrication = CTk.CTkLabel(produit_frame, text="Numéro de lot de fabrication / référence du produit  ",font = ('Century Gothic',15),text_color="gray30")
numero_de_lot_de_fabrication.pack(pady=5, padx=10, anchor="w")
checkbox_numero_de_lot_de_fabrication_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_numero_de_lot_de_fabrication_1.pack(pady=5, padx=10, fill="x")
checkbox_numero_de_lot_de_fabrication_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_numero_de_lot_de_fabrication_2.pack(pady=5, padx=10, fill="x")

fonction_du_produit = CTk.CTkLabel(produit_frame, text="Fonction du produit (sauf si cela ressort clairement de sa présentation)   ",font = ('Century Gothic',15),text_color="gray30")
fonction_du_produit.pack(pady=5, padx=10, anchor="w")
checkbox_fonction_du_produit_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_fonction_du_produit_1.pack(pady=5, padx=10, fill="x")
checkbox_fonction_du_produit_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_fonction_du_produit_2.pack(pady=5, padx=10, fill="x")

liste_des_ingredients = CTk.CTkLabel(produit_frame, text="Liste des ingrédients",font = ('Century Gothic',15),text_color="gray30")
liste_des_ingredients.pack(pady=5, padx=10, anchor="w")
checkbox_liste_des_ingredients_1 = CTk.CTkCheckBox(produit_frame, text="OK", fg_color="DarkOrchid4", text_color="black")
checkbox_liste_des_ingredients_1.pack(pady=5, padx=10, fill="x")
checkbox_liste_des_ingredients_2 = CTk.CTkCheckBox(produit_frame, text="cf « Annotations conseillées sur l'étiquette »", fg_color="DarkOrchid4", text_color="black")
checkbox_liste_des_ingredients_2.pack(pady=5, padx=10, fill="x")

entry_langue = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="Langue",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_langue.pack(pady = 5, padx = 10,anchor ='w')

entry_liste_1 = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="Liste 1 (INCI version non saponifiée) ou version INCI non savon",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_liste_1.pack(pady = 5, padx = 10,anchor ='w')

entry_liste_2 = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="Liste 2 (INCI version saponifiée)",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_liste_2.pack(pady = 5, padx = 10,anchor ='w')

bio = CTk.CTkLabel(produit_frame, text="BIO",font = ('Century Gothic',15),text_color="gray30")
bio.pack(pady=5, padx=10, anchor="w")
checkbox_bio_1 = CTk.CTkCheckBox(produit_frame, text="", fg_color="DarkOrchid4", text_color="black")
checkbox_bio_1.pack(pady=5, padx=10, fill="x")
checkbox_bio_2 = CTk.CTkCheckBox(produit_frame, text="*Issu de l'agriculture biologique", fg_color="DarkOrchid4", text_color="black")
checkbox_bio_2.pack(pady=5, padx=10, fill="x")

allergenes = CTk.CTkLabel(produit_frame, text="HYDROXYDE DE SODIUM+BK:BBO:BP",font = ('Century Gothic',15),text_color="gray30")
allergenes.pack(pady=5, padx=10, anchor="w")
combobox_allergenes = CTk.CTkComboBox(produit_frame, values=["Présent dans le(s) parfum(s)","Présent dans le(s) parfum et l'huile(s) essentielle(s)","Présents dans le(s) huiles essentielle(s)"],fg_color = "DarkOrchid4",text_color="White")
combobox_allergenes.pack(pady=5, padx=10, fill="x")
entry_allergenes = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="ALLERGENES",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_allergenes.pack(pady = 5, padx = 10,anchor ='w')

label_recommandations = CTk.CTkLabel(produit_frame, text="Recommandations",font = ('Century Gothic',15),text_color="gray30")
label_recommandations.pack(pady=5, padx=10, anchor="w")
text_recommandations = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_recommandations.pack(pady=5,padx=10,anchor="w")

label_ccl_microbio = CTk.CTkLabel(produit_frame, text="CCL MICROBIO",font = ('Century Gothic',15),text_color="gray30")
label_ccl_microbio.pack(pady=5, padx=10, anchor="w")
text_ccl_microbio = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_ccl_microbio.pack(pady=5,padx=10,anchor="w")

label_fabricant = CTk.CTkLabel(produit_frame, text="Fabricant / distributeur (conditionnement)",font = ('Century Gothic',15),text_color="gray30")
label_fabricant.pack(pady=5, padx=10, anchor="w")
text_fabricant = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_fabricant.pack(pady=5,padx=10,anchor="w")

label_description = CTk.CTkLabel(produit_frame, text="Description (conditionnement)",font = ('Century Gothic',15),text_color="gray30")
label_description.pack(pady=5, padx=10, anchor="w")
text_description = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_description.pack(pady=5,padx=10,anchor="w")

label_restrictions_cosmetiques_opinions_SCCS = CTk.CTkLabel(produit_frame, text="Restrictions cosmétiques / opinions SCCS (détails)",font = ('Century Gothic',15),text_color="gray30")
label_restrictions_cosmetiques_opinions_SCCS.pack(pady=5, padx=10, anchor="w")
text_restrictions_cosmetiques_opinions_SCCS = CTk.CTkTextbox(produit_frame, width=200, corner_radius=3,text_color="Black",fg_color='gray64')
text_restrictions_cosmetiques_opinions_SCCS.pack(pady=5,padx=10,anchor="w")

label_impuretes = CTk.CTkLabel(produit_frame, text="Impuretés",font = ('Century Gothic',15),text_color="gray30")
label_impuretes.pack(pady=5, padx=10, anchor="w")
combobox_impuretes = CTk.CTkComboBox(produit_frame, values=["Absence","Présence"],fg_color = "DarkOrchid4",text_color="White")
combobox_impuretes.pack(pady=5, padx=10, fill="x")

label_Allergenes = CTk.CTkLabel(produit_frame, text="Allergenes",font = ('Century Gothic',15),text_color="gray30")
label_Allergenes.pack(pady=5, padx=10, anchor="w")
combobox_Allergenes = CTk.CTkComboBox(produit_frame, values=["Absence","Présence"],fg_color = "DarkOrchid4",text_color="White")
combobox_Allergenes.pack(pady=5, padx=10, fill="x")

label_produit_rincer = CTk.CTkLabel(produit_frame, text="0,01% (produit à rincer) ou > 0,001% (produit sans rinçage)",font = ('Century Gothic',15),text_color="gray30")
label_produit_rincer.pack(pady=5, padx=10, anchor="w")
combobox_produit_rincer = CTk.CTkComboBox(produit_frame, values=["> 0,001% (produit sans rinçage)","> 0,01% (produit à rincer)"," > 0,01% (produit à rincer)"],fg_color = "DarkOrchid4",text_color="White")
combobox_produit_rincer.pack(pady=5, padx=10, fill="x")
entry_produit_rincer = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="Autres",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_produit_rincer.pack(pady = 5, padx = 10,anchor ='w')

informations_mos = CTk.CTkLabel(produit_frame, text="Information MoS",font = ('Century Gothic',15),text_color="gray30")
informations_mos.pack(pady=5, padx=10, anchor="w")
informations_mos = CTk.CTkComboBox(produit_frame, values=["","L'OMS propose une valeur minimale MoS = 100. Il est généralement admis que la MoS doit au moins être > 100 afin de conclure qu'une substance est sans danger pour la santé humaine dans le cadre de son utilisation."],fg_color = "DarkOrchid4",text_color="White")
informations_mos.pack(pady=5, padx=10, fill="x")

label_conclusion_fin = CTk.CTkLabel(produit_frame, text="pHConclusion",font = ('Century Gothic',15),text_color="gray30")
label_conclusion_fin.pack(pady=5, padx=10, anchor="w")
combobox_conclusion_fin = CTk.CTkComboBox(produit_frame, values=["ne présente pas de risque particulier pour la santé humaine et répond aux exigences de l’article 3 du règlement (CE) N°1223/2009. Si le produit s'avère, suite à son utilisation par les consommateurs, à l'origine de réactions indésirables significatives déclarées auprès des services de cosmétovigilance, notamment de réactions d'irritations locales ou allergiques, le soussigné devra en être informé afin d'envisager l'éventuelle réévaluation de la sécurité pour la santé humaine du produit fini.","présente un risque particulier pour la santé humaine et ne répond pas aux exigences de l’article 3 du règlement (CE) N°1223/2009."],fg_color = "DarkOrchid4",text_color="White")
combobox_conclusion_fin.pack(pady=5, padx=10, fill="x")

entry_date_de_redaction_rapport_final = CTk.CTkEntry(master = produit_frame, width = 2200,placeholder_text="Adresse",fg_color="DarkOrchid4",placeholder_text_color="White")
entry_date_de_redaction_rapport_final.pack(pady = 5, padx = 10,anchor ='w')
date_de_redaction_rapport_final_label = CTk.CTkLabel(produit_frame, text="Date de rédaction du rapport final", font = ('Century Gothic',15),text_color="gray30")
date_de_redaction_rapport_final_label.pack(pady=5, padx=10,anchor = 'w')
date_de_redaction_rapport_final = DateEntry(produit_frame, date_pattern = 'dd/mm/yyyy')
date_de_redaction_rapport_final.pack(pady = 10, padx=10, anchor = 'w')

#Ajouter un bouton pour valider les champs
valider_button = CTkButton(main_frame, text="Valider", command=valider_formulaire, fg_color="purple3", text_color='White')
valider_button.pack(pady=10, padx=15, anchor='w')

# Ajouter un bouton pour exporter les données en Excel
exporter_button = CTkButton(main_frame, text="Exporter en Excel", command=exporter_en_excel, fg_color="purple3", text_color='White')
exporter_button.pack(pady=10, padx=15, anchor='w')

#Ajouter un bouton pour supprimer les champs
#supprimer_button = CTkButton(main_frame, text="Supprimer",command=effacer_champs_formulaire, fg_color="purple3", text_color='White')
#supprimer_button.pack(pady=10, padx=15, anchor='w')

app.mainloop()


#------------------------------------- [ SUPPRIMER UNE ENTRÉE DE LA BDD ] -----------------------------------------------------------------
'''

# Fonction pour remplir les champs du formulaire avec les données de l'entrée sélectionnée
def load_selected_entry_data(result):
    (
        id,
        denomination_commerciale,
        type_produit,
        population_cible,
        description_produit,
        aspect,
        couleur,
        odeur,
        ph_20c,
        densite_20c,
        indice_refraction_20c,
        point_eclair,
        point_fusion,
        auto_inflammation,
        ebullition,
        acidite,
        indice_peroxyde,
        solubilite,
        viscosite,
        activite_eau,
        date_mise_sur_marche,
        type_contenant,
        type_fermeture,
        conclusion_rapport,
    ) = result[:24]

    # Définir les valeurs dans les variables Tkinter.
    denomination_var.set(denomination_commerciale)
    type_produit_var.set(type_produit)
    population_cible_var.set(population_cible)

    # Définir le contenu du widget Texte pour la "Description".
    text_description_produit.delete(1.0, tk.END)  # Efface le contexte existant
    text_description_produit.insert(tk.END, description_produit)

    aspect_var.set(aspect)
    couleur_var.set(couleur)
    odeur_var.set(odeur)
    ph_20c_var.set(ph_20c)
    densite_20c_var.set(densite_20c)
    indice_refraction_20c_var.set(indice_refraction_20c)
    point_eclair_var.set(point_eclair)
    point_fusion_var.set(point_fusion)
    auto_inflammation_var.set(auto_inflammation)
    ebullition_var.set(ebullition)
    acidite_var.set(acidite)
    indice_peroxyde_var.set(indice_peroxyde)
    solubilite_var.set(solubilite)
    viscosite_var.set(viscosite)
    activite_eau_var.set(activite_eau)
    date_mise_sur_marche_var.set(date_mise_sur_marche)
    type_contenant_var.set(type_contenant)
    type_fermeture_var.set(type_fermeture)
    conclusion_rapport_var.set(conclusion_rapport)


# Fonction pour vider les champs après la suppression ou l'annulation de la suppression
def clear_form_fields():
    entry_denomination.delete(0, tk.END)
    combobox_type_produit.set("---")
    combobox_population_cible.set("---")
    text_description_produit.delete("1.0", tk.END)
    entry_aspect.delete(0, tk.END)
    entry_couleur.delete(0, tk.END)
    combobox_type_odeur.set("---")
    entry_ph_20c.delete(0, tk.END)
    entry_densite_20c.delete(0, tk.END)
    entry_indice_refraction_20c.delete(0, tk.END)
    entry_point_eclair.delete(0, tk.END)
    entry_point_fusion.delete(0, tk.END)
    entry_auto_inflammation.delete(0, tk.END)
    entry_ebullition.delete(0, tk.END)
    entry_acidite.delete(0, tk.END)
    entry_indice_peroxyde.delete(0, tk.END)
    entry_solubilite.delete(0, tk.END)
    entry_viscosite.delete(0, tk.END)
    entry_activite_eau.delete(0, tk.END)
    combobox_type_contenant.set("---")
    combobox_type_fermeture.set("---")
    combobox_conclusion_rapport.set("---")


# Fonction pour supprimer une entrée
def delete_entry():
    # Ouvre la boîte de dialogue d'autocomplétion pour sélectionner une entrée.
    autocomplete_dialog = BoiteDialogueAutocomplete(root, "Select Entry", "Sélectionner une Entrée à Supprimer", get_all_denominations())
    selected_denomination = autocomplete_dialog.result

    if selected_denomination:
        # Récupère les données de l'entrée sélectionnée depuis la base de données.
        conn = sqlite3.connect(chemin_db)
        query = f"SELECT * FROM produits WHERE denomination_commerciale = ?"
        result = conn.execute(query, (selected_denomination,)).fetchone()
        conn.close()

        if result:
            # Remplie les champs du formulaire avec les données de l'entrée sélectionnée.
            load_selected_entry_data(result)

            # Affiche une boîte de dialogue de confirmation
            confirmation = messagebox.askyesno("Confirmation", f"Voulez vous vraiment supprimer l'entrée {selected_denomination}?")

            if confirmation:
                # Supprime l'entrée de la base de données en utilisant la clé primaire (id).
                id_to_delete = result[0]
                conn = sqlite3.connect(chemin_db)
                query = "DELETE FROM produits WHERE id = ?"
                conn.execute(query, (id_to_delete,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Succès", "Entrée Supprimé avec Succès.")
                clear_form_fields()  # Vide les champs du formulaire après que l'entrée sois supprimé
            else:
                messagebox.showinfo("Annulation", "Suppression Annulé.")
                clear_form_fields()  # Vide les champs du formulaire après annulation de la suppression
        else:
            messagebox.showerror("Erreur", "L'Entrée Sélectionné n'a pas été Trouvé dans la Base de Donnée.")

'''
