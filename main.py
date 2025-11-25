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
        'Identifiant de document',
        'Reference document',
        '1 Articles CGI',
        '2 Articles CGI',
        '3 Articles CGI',
        '4 Articles CGI',
        '5 Articles CGI',
        'No disposition',
        'Date mutation',
        'Nature mutation',
        #'Valeur fonciere',
        'No voie',
        'B/T/Q',
        'Type de voie',
        'Code voie',
        'Voie',
        'Code postal',
        #'Commune',
        #'Code departement',
        'Code commune',
        'Prefixe de section',
        #'Section',
        'No plan',
        'No Volume',
        '1er lot',
        'Surface Carrez du 1er lot',
        '2eme lot',
        'Surface Carrez du 2eme lot',
        '3eme lot',
        'Surface Carrez du 3eme lot',
        '4eme lot',
        'Surface Carrez du 4eme lot',
        '5eme lot',
        'Surface Carrez du 5eme lot',
        #'Nombre de lots',
        'Code type local',
        'Type local',
        'Identifiant local',
        #'Surface reelle bati',
        'Nombre pieces principales',
        'Nature culture',
        'Nature culture speciale',
        'Surface terrain'
]
df = df.drop(columns=exclusions)

#remove the lines having NaN
df.dropna(inplace=True)
#print(df.head())

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
print(df.head())

logging.info("Cleansed data written in " + output_file)
df.to_csv(output_file, index=False)