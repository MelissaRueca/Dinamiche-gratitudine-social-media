# -*- coding: utf-8 -*-
import json
import re 
import spacy 
from collections import Counter

"""
Input: diz[codice utente]=lista_commenti, dal quale ho già rimosso tutti gli utenti che hanno commentato meno di un numero x di volte

PART OF SPEECH TAGGING
Considero solo: 
    - nomi, pronomi, aggettivi, avverbi, interiezioni, verbi
    -parole con almeno 4 lettere e al massimo 45

Calcolo soglia percentuale per ogni utente e, in base a quella, prendo il numero di giusto di parole ricorrenti per ogni utente e le inserisco nel set di parole ricorrenti finale


Output: set globale delle parole ricorrenti
"""

'''
righe commentate sono state utilizzate per capire la formula della soglia percentuale
'''

def paroleRicorrenti(diz):

    with open(diz, 'r', encoding='utf-8') as file_json:
        diz_commenti_utente = json.load(file_json)
      
    parole_ricorrenti = set()
    nlp = spacy.load("en_core_web_sm")   #carico il modello linguistico per la lingua inglese   
    c = 0
 #   d_utente = {}
 #   media = 0
  #  tt = 0
   # nct = 0
    #diz_soglia = {}
    for utente, commenti in diz_commenti_utente.items():
        print(c)
        par_ut = 0
       # t = 0
        #nc = 0
       # min_u = float('inf')
        #max_u = float('-inf')
        #media_u = float('-inf')
        parole_utente = set()  
        parole_da_considerare = []
        diz_ricorrenti = Counter()
        for commento in commenti: 
            parole = eliminazioneCaratteri(commento, nlp)
            #p = 0
            for parola in parole:
                    # nlp(parola) restituisce un oggetto Doc che rappresenta la parola analizzata da spaCy
                    # con [0] accedo al primo token del documento, che contiene la parola (dato che la parola è singola ci interessa solo il primo token)
                    token = nlp(parola)[0]
                    # restituisce la categoria grammaticale a cui appartiene la parola
                    pos = token.pos_
                    if pos in ('NOUN', 'PRON', 'ADJ', 'ADV', 'INTJ', 'VERB') and len(parola)>=4 and len(parola)<45 and not(re.search(r'(.)\1\1', parola)):  #verifica se è un sostantivo o un verbo e se ha almeno 5 lettere ma non più di 45
                        s = token.lemma_
                        if len(s)>=4:
                            print(token.lemma_.lower())
                            parole_da_considerare.append(token.lemma_.lower())
                            #p += 1 
                            par_ut += 1
            #t += p
            #nc += 1
            #tt += p
            #nct +=1
            #if p <= min_u:
             #   min_u = p
            #if p >= max_u:
             #   max_u = p
            #if nc != 0:
             #   media_u = t / nc
        #d_utente[utente] = (min_u, max_u, media_u)
                        
        diz_ricorrenti.update(parole_da_considerare)
        
        soglia_percentuale = min(45/(par_ut+100)+0.05, 0.5)
        n_parole_utente_daconsiderare = int(par_ut * soglia_percentuale)

        #lista di tuple (parole, ricorrenza) ordinata in ordine decrescente di ricorrenza
        lista_ricorrenze = sorted(diz_ricorrenti.items(), key = lambda x: x[1], reverse = True)
                            
        parole_utente.update(parola for parola, _ in lista_ricorrenze[:n_parole_utente_daconsiderare])
        
        parole_ricorrenti.update(parole_utente)
        c += 1
        
        #diz_soglia[utente] = soglia_percentuale
    #if nct != 0:
     #   media = tt / nct
    
    #with open('d_min_max_media_4length.json', 'w', encoding = 'utf-8') as file_json:
      #  json.dump(d_utente, file_json)
    
    #with open('n_media_4length.json', 'w', encoding = 'utf-8') as file_json:
     #   json.dump(media, file_json)
    
    with open('set_ricorrenti.json', 'w', encoding = 'utf-8') as file_json:
        json.dump(list(parole_ricorrenti), file_json)
        
    #with open('soglia_4length.json', 'w', encoding = 'utf-8') as file_json:
     #   json.dump(diz_soglia, file_json)
        
    return parole_ricorrenti 

def eliminazioneCaratteri(commento, nlp):
    #rimuovo le email
    # r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' : expr regolare per individuare email, dove:
    #        -'\b' rappresentano il "bordo" iniziale e finale della parola e garantisce che l'indirizzo inizi e finisca con un confine di parola
    #        -'[A-Za-z0-9._%+-]+' prende il nome utente della mail
    #        -'[A-Za-z0-9.-]+' cattura l'estenzione del dominio
    #        -'\.' cattura il punto che separa il nome di dominio dall'estensione del dominio
    #        -'[A-Z|a-z]{2,}' cattura l'estensione del dominio che deve contenere almeno due lettere
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    #con re.sub sostutisco tutte le occorrenze di indirizzi email nella frase con una stringa vuota, ottenendo la frase senza mail
    testo_senza_email = re.sub(email_pattern, '', commento)
    
    #rimuovo i link 
    # approccio con regex analogo al precedente
    # 'r'\b(?:https?://|www\.)[^\s]+'' cattura gli URL che iniziano con http://, https:// o www.
    #       -'(?:https?://|www\.)' utilizza un gruppo non catturante '(?:..)' per specificare che l'URL può iniziare con i sopra indicati
    #       -'[^\s]+' cattura uno o più caratteri, eccetto spazi bianchi, rappresentando il resto dell'URL
    url_pattern = re.compile(r'\b(?:https?://|www\.)[^\s]+')
    testo_senza_url_mail = re.sub(url_pattern, '', testo_senza_email)
    
    #cattura parole complete che contengono solo lettere, numeri e alcuni caratteri di interpunzione specifici 
    #come virgole, punti e virgole, punti esclamativi e punti interrogativi
    #       -'\b': indica un confine di parola (word boundary), assicurandoci che la parola sia separata da altri caratteri non alfanumerici
    #       -'[a-zA-Z0-9.,;!?]+': corrisponde a una sequenza (una o più occorrenze) di caratteri che sono lettere maiuscole o minuscole, numeri, virgole, punti e virgole, punti esclamativi o punti interrogativi

    testo = nlp(testo_senza_url_mail)
    #estrae i token considerando solo parole e ellissi
    parole = [token.text for token in testo if token.is_alpha or token.text == "..."]
    
    return parole
    
print(paroleRicorrenti("C:\\Users\\HP\\OneDrive\\Desktop\\Tirocinio\\dizionario_utentiConSubmissionsECommenti.json"))