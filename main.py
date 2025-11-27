import logging
import pandas as pd
import argparse
import os
from sklearn import preprocessing


parser = argparse.ArgumentParser(description='Process some data')
parser.add_argument('input_file', help='Input file name, should be a .txt as per data.gouv.fr valeurs foncieres datasets')
args = parser.parse_args()
print(f"Input: {args.input_file}")
input_file=args.input_file
output_file_name, extension=os.path.splitext(args.input_file)
output_file=output_file_name+".csv"

print("["+input_file + "] will be prepared into ["+output_file+"]")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

#https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/#/resources/d573456c-76eb-4276-b91c-e6b9c89d6656
df = pd.read_csv('./'+input_file, sep='|', on_bad_lines='skip')
print("INPUT")
print(df.info())

#filter the lines of interest
df = df[(
            (df['Type local'] == 'Appartement')
            #& (df['Commune'] == 'NICE')
            & (df['Nature mutation'] == 'Vente')
            #& (df['Code departement'] != '2A')
            #& (df['Code departement'] != '2B')
        )]

#drop the columns not used
exclusions = [
    #'id_mutation',
    #'date_mutation',
    'numero_disposition',
    #'nature_mutation',
    #'valeur_fonciere',
    'adresse_numero',
    'adresse_suffixe',
    'adresse_nom_voie',
    'adresse_code_voie',
    #'code_postal',
    #'code_commune',
    #'nom_commune',
    'code_departement',
    'ancien_code_commune',
    'ancien_nom_commune',
    'id_parcelle',
    'ancien_id_parcelle',
    'numero_volume',
    'lot1_numero',
    'lot1_surface_carrez',
    'lot2_numero',
    'lot2_surface_carrez',
    'lot3_numero',
    'lot3_surface_carrez',
    'lot4_numero',
    'lot4_surface_carrez',
    'lot5_numero',
    'lot5_surface_carrez',
    #'nombre_lots',
    #'code_type_local',
    #'type_local',
    #'surface_reelle_bati',
    #'nombre_pieces_principales',
    'code_nature_culture',
    'nature_culture',
    'code_nature_culture_speciale',
    'nature_culture_speciale',
    #'surface_terrain',
    #'longitude',
    #'latitude'
 ]
df = df.drop(columns=exclusions)

#drop NaN
df.dropna(inplace=True)
#drop DOM-TOM
prefixes = ('97', '988')
df = df[~df['code_postal'].astype(str).str.startswith(prefixes)]

#dataset sanity checks
if df.isna().any().any():
    logging.warning("Some NA values remain")
else:
    logging.info("No NA values")

if df.isnull().any().any():
    logging.warning("Some null values remain")
else:
    logging.info("No null values")

#add index
df.reset_index(names='Index', inplace=True)

#data preparation for encoding
df['Section'] = df['Section'].astype('category')
df['Commune'] = df['Commune'].astype('string')
df['Valeur fonciere'] = df['Valeur fonciere'].str.replace(',', '.').astype(float)
df['Code departement'] = df['Code departement'].replace({'2A': 2001, '2B': 2002})
df['Code departement'] = df['Code departement'].astype(int)

print("OUTPUT")
print(df.info())

#standardize the data (xi-avg(X1)/stdev
df[['Surface reelle bati']] = preprocessing.scale(df[['Surface reelle bati']])
df[['Nombre pieces principales']] = preprocessing.scale(df[['Nombre pieces principales']])
print(df.head())

logging.info("Cleansed data written in " + output_file)
df.to_csv(output_file, index=False)