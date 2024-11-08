import json
import pandas as pd
"""
scorro tutti i commenti/submission e costruisco il dizionario unico che serve per il Part of Speech Tagging : contiene, per ogni utente, tutte le sue submissions e tutti i suoi commenti
diz[author_fullname] = lista commenti/submissions 
ottenuto il dizionario lo salvo in formato json
"""

file1 = 'C:\\Users\\HP\\OneDrive\\Desktop\\Tirocinio\\offmychest\\RC_offmychest.csv'
file2 = 'C:\\Users\\HP\\OneDrive\\Desktop\\Tirocinio\\offmychest\\RS_offmychest.csv'

def dizionario_utente_commenti(file1, file2):
    
    df_commenti = pd.read_csv(file1)
    df_submissions = pd.read_csv(file2)

    d= {}
    
    for _, riga in df_submissions.iterrows():
        author_fullname = riga['author_fullname']
        testo = riga['selftext']
        
        if author_fullname not in d and testo != '[removed]':
            d[author_fullname] = [testo]
        elif testo != '[removed]':
            d[author_fullname].append(testo)
            
    for _, riga in df_commenti.iterrows():
        author_fullname = riga['author_fullname']
        testo = riga['body']
        if author_fullname not in d:
            continue
        else:
            d[author_fullname].append(testo)
        
    d = {chiave: valore for chiave, valore in d.items()}
    
    percorso_file_json = 'dizionario_prova.json'

    with open(percorso_file_json, 'w', encoding='utf-8') as file_json:
        json.dump(d, file_json, ensure_ascii=False)
    
print(dizionario_utente_commenti(file1, file2))
