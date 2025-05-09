from fuzzysearch import find_near_matches
import os
import pytesseract
from pdf2image import convert_from_path
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
import math
import re
import random
import string

#pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
#poppler_path = "/usr/bin"

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
poppler_path = os.getenv("POPPLER_PATH", "/usr/bin")

currency_mapping = {
        "EUR": "Euro","USD": "US Dollar","ARS": "Argentine Peso","AUD": "Australian Dollar","BHD": "Bahraini Dinar","BWP": "Botswana Pula",
        "BRL": "Brazilian Real","GBP": "British Pound","BND": "Bruneian Dollar","BGN": "Bulgarian Lev",
        "CAD": "Canadian Dollar","CLP": "Chilean Peso","CNY": "Chinese Yuan Renminbi","COP": "Colombian Peso",
        "CZK": "Czech Koruna","DKK": "Danish Krone","AED": "Emirati Dirham","HKD": "Hong Kong Dollar","HUF": "Hungarian Forint",
        "ISK": "Icelandic Krona","INR": "Indian Rupee","IDR": "Indonesian Rupiah","IRR": "Iranian Rial","ILS": "Israeli Shekel",
        "JPY": "Japanese Yen","KZT": "Kazakhstani Tenge","KWD": "Kuwaiti Dinar","LYD": "Libyan Dinar","MYR": "Malaysian Ringgit",
        "MUR": "Mauritian Rupee","MXN": "Mexican Peso","NPR": "Nepalese Rupee","NZD": "New Zealand Dollar","NOK": "Norwegian Krone",
        "OMR": "Omani Rial","PKR": "Pakistani Rupee","PHP": "Philippine Peso","PLN": "Polish Zloty","QAR": "Qatari Riyal",
        "RON": "Romanian New Leu","RUB": "Russian Ruble","SAR": "Saudi Arabian Riyal","SGD": "Singapore Dollar","ZAR": "South African Rand",
        "KRW": "South Korean Won","LKR": "Sri Lankan Rupee","SEK": "Swedish Krona","CHF": "Swiss Franc","TWD": "Taiwan New Dollar",
        "THB": "Thai Baht","TTD": "Trinidadian Dollar","TRY": "Turkish Lira"
    }

countries = [
    "AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ",
    "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR",
    "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC",
    "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO",
    "EC", "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA",
    "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT",
    "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP",
    "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI",
    "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX",
    "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI",
    "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN",
    "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC", "WS",
    "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS",
    "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK",
    "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU",
    "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "XK", "XI", "OO", "EL"
]

country_fcomune = {
    "AF": "Afghanistan", "AX": "Isole Åland", "AL": "Albania", "DZ": "Algeria", "AS": "Samoa Americana",
    "AD": "Andorra", "AO": "Angola", "AI": "Anguila", "AQ": "Antartide", "AG": "Antigua e Barbuda",
    "AR": "Argentina", "AM": "Armenia", "AW": "Aruba", "AU": "Australia", "AT": "Austria", "AZ": "Azerbaigian",
    "BS": "Bahamas", "BH": "Bahrein", "BD": "Bangladesh", "BB": "Barbados", "BY": "Bielorussia", "BE": "Belgio",
    "BZ": "Belize", "BJ": "Benin", "BM": "Bermuda", "BT": "Bhutan", "BO": "Bolivia", "BQ": "Caribbean Netherlands",
    "BA": "Bosnia ed Erzegovina", "BW": "Botswana", "BV": "Isole Bouvet", "BR": "Brasile", "IO": "Territorio britannico dell'Oceano Indiano",
    "BN": "Brunei", "BG": "Bulgaria", "BF": "Burkina Faso", "BI": "Burundi", "KH": "Cambogia", "CM": "Camerun",
    "CA": "Canada", "CV": "Capo Verde", "KY": "Isole Cayman", "CF": "Repubblica Centrafricana", "TD": "Ciad",
    "CL": "Cile", "CN": "Cina", "CX": "Isole Christmas", "CC": "Isole Cocos", "CO": "Colombia", "KM": "Comore",
    "CG": "Congo", "CD": "Repubblica Democratica del Congo", "CK": "Isole Cook", "CR": "Costa Rica", "CI": "Costa d'Avorio",
    "HR": "Croazia", "CU": "Cuba", "CW": "Curaçao", "CY": "Cipro", "CZ": "Repubblica Ceca", "DK": "Danimarca", "DJ": "Gibuti",
    "DM": "Dominica", "DO": "Repubblica Dominicana", "EC": "Ecuador", "EG": "Egitto", "SV": "El Salvador",
    "GQ": "Guinea Equatoriale", "ER": "Eritrea", "EE": "Estonia", "ET": "Etiopia", "FK": "Isole Falkland",
    "FO": "Isole Fær Øer", "FJ": "Figi", "FI": "Finlandia", "FR": "Francia", "GF": "Guyana Francese",
    "PF": "Polinesia Francese", "TF": "Terre Australi e Antartiche Francesi", "GA": "Gabon", "GM": "Gambia",
    "GE": "Georgia", "DE": "Germania", "GH": "Ghana", "GI": "Gibilterra", "GR": "Grecia", "GL": "Groenlandia",
    "GD": "Grenada", "GP": "Guadalupa", "GU": "Guam", "GT": "Guatemala", "GG": "Guernsey", "GN": "Guinea",
    "GW": "Guinea-Bisau", "GY": "Guyana", "HT": "Haiti", "HM": "Isole Heard e McDonald", "VA": "Vaticano",
    "HN": "Honduras", "HK": "Hong Kong", "HU": "Ungheria", "IS": "Islanda", "IN": "India", "ID": "Indonesia",
    "IR": "Iran", "IQ": "Iraq", "IE": "Irlanda", "IM": "Isola di Man", "IL": "Israele",
    "JM": "Giamaica", "JP": "Giappone", "JE": "Jersey", "JO": "Giordania", "KZ": "Kazakistan", "KE": "Kenya",
    "KI": "Kiribati", "KP": "Corea del Nord", "KR": "Corea del Sud", "KW": "Kuwait", "KG": "Kirgizistan",
    "LA": "Laos", "LV": "Lettonia", "LB": "Libano", "LS": "Lesotho", "LR": "Liberia", "LY": "Libia", "LI": "Liechtenstein",
    "LT": "Lituania", "LU": "Lussemburgo", "MO": "Macau", "MK": "Macedonia del Nord", "MG": "Madagascar",
    "MW": "Malawi", "MY": "Malesia", "MV": "Maldive", "ML": "Mali", "MT": "Malta", "MH": "Isole Marshall",
    "MQ": "Martinica", "MR": "Mauritania", "MU": "Maurizio", "YT": "Mayotte", "MX": "Messico", "FM": "Micronesia",
    "MD": "Moldavia", "MC": "Monaco", "MN": "Mongolia", "ME": "Montenegro", "MS": "Montserrat", "MA": "Marocco",
    "MZ": "Mozambico", "MM": "Myanmar", "NA": "Namibia", "NR": "Nauru", "NP": "Nepal", "NL": "Paesi Bassi",
    "NC": "Nuova Caledonia", "NZ": "Nuova Zelanda", "NI": "Nicaragua", "NE": "Niger", "NG": "Nigeria", "NU": "Niue",
    "NF": "Isole Norfolk", "MP": "Isole Marianne Settentrionali", "NO": "Norvegia", "OM": "Oman", "PK": "Pakistan",
    "PW": "Palau", "PS": "Palestina", "PA": "Panama", "PG": "Papua Nuova Guinea", "PY": "Paraguay", "PE": "Perù",
    "PH": "Filippine", "PN": "Isole Pitcairn", "PL": "Polonia", "PT": "Portogallo", "PR": "Porto Rico", "QA": "Qatar",
    "RE": "Riunione", "RO": "Romania", "RU": "Russia", "RW": "Ruanda", "BL": "Saint-Barthélemy", "SH": "Sant'Elena",
    "KN": "Saint Kitts e Nevis", "LC": "Santa Lucia", "MF": "Saint-Martin", "PM": "Saint Pierre e Miquelon",
    "VC": "Saint Vincent e Grenadine", "WS": "Samoa", "SM": "San Marino", "ST": "Sao Tomé e Principe", "SA": "Arabia Saudita",
    "SN": "Senegal", "RS": "Serbia", "SC": "Seychelles", "SL": "Sierra Leone", "SG": "Singapore", "SX": "Sint Maarten",
    "SK": "Slovacchia", "SI": "Slovenia", "SB": "Isole Salomone", "SO": "Somalia", "ZA": "Sudafrica",
    "GS": "Georgia del Sud e isole Sandwich meridionali", "SS": "Sudan del Sud", "ES": "Spagna", "LK": "Sri Lanka",
    "SD": "Sudan", "SR": "Suriname", "SJ": "Svalbard e Jan Mayen", "SZ": "Eswatini", "SE": "Svezia",
    "CH": "Svizzera", "SY": "Siria", "TW": "Taiwan", "TJ": "Tagikistan", "TZ": "Tanzania", "TH": "Thailandia",
    "TL": "Timor Est", "TG": "Togo", "TK": "Tokelau", "TO": "Tonga", "TT": "Trinidad e Tobago", "TN": "Tunisia",
    "TR": "Turchia", "TM": "Turkmenistan", "TC": "Isole Turks e Caicos", "TV": "Tuvalu", "UG": "Uganda",
    "UA": "Ucraina", "AE": "Emirati Arabi Uniti", "GB": "Regno Unito", "US": "Stati Uniti", "UM": "Isole minori lontane degli Stati Uniti",
    "UY": "Uruguay", "UZ": "Uzbekistan", "VU": "Vanuatu", "VE": "Venezuela", "VN": "Vietnam",
    "VG": "Isole Vergini Britanniche", "VI": "Isole Vergini Statunitensi", "WF": "Wallis e Futuna",
    "EH": "Sahara Occidentale", "YE": "Yemen", "ZM": "Zambia", "ZW": "Zimbabwe", "XK": "Kosovo",
    "XI": "Isola di Man", "OO": "Other", "EL": "Elisabetta"
}

prompt= """
     Estrai le seguenti informazioni da un testo relativo a una fattura, distinguendo tra prestatore (fornitore), 
     committente (cliente) e trasmittente (chi invia la fattura). Se trovi più indirizzi riferiti al cliente, 
     ad esempio, indirizzo sede legale e indirizzo di spedizione, riporta l’indirizzo della sede legale. 
     Trasmittente (chi invia la fattura):
     - IdPaese_T: Primi 2 caratteri della partita IVA.
     - IdCodice_T: Parte numerica della partita IVA.
     Prestatore (fornitore):
     - IdPaese_P: Primi 2 caratteri della partita IVA.
     - IdCodice_P: Parte numerica della partita IVA.
     - Denominazione_P: Nome del prestatore (se presente azienda).
     - Indirizzo_P: Indirizzo.
     - CAP_P: CAP.
     - Comune_P: Città.
     - Nazione_P: Paese (sigla a due lettere).
     Committente (Cliente):
     - IdPaese_C: Primi 2 caratteri della partita IVA.
     - IdCodice_C: Parte numerica della partita IVA.
     - Denominazione_C: Nome del prestatore (se presente azienda).
     - Indirizzo_C: Indirizzo.
     - CAP_C: CAP.
     - Comune_C: Città.
     - Nazione_C: Paese (sigla a due lettere).
     Informazioni sulla fattura:
     - Divisa: Valuta (ISO 3 lettere).
     - Numero_fattura: Numero della fattura.
     - ImportoTotale: Importo totale (solo numerico, es. 10.00).
     - Data_pagamento: Data più recente.
     - Data_Acquisto: Data più remota.
     - oggetto_acquistato: Breve descrizione (max 35 caratteri).
     Se c'è una sola data, Data_Acquisto e Data_pagamento coincidono. Le date devono essere in formato YYYY-MM-DD. 
     Se un dato non è presente, scrivere "vuoto". L’output deve essere in formato - chiave: valore senza simboli extra (oltre il trattino) .
"""

file_data = {
        "data_dict": {},
        "original_valuta": "",
        "original_total": "",
        "varx": "",
        "errore": []
}

def extract_text_from_pdf(pdf_path, name_file):
    pages = convert_from_path(pdf_path, 150, poppler_path=poppler_path)
    page_indices = [0, len(pages) - 1]
    text = ""
    for i in page_indices:
        img_path = f"page_{name_file+str(i)}.png"
        pages[i].save(img_path, 'PNG')
        text += pytesseract.image_to_string(img_path, lang='eng+ita') #+fra+deu+ell')
        os.remove(img_path)
    return text

file_messages={}
def convert_to_euro(amount:float,divisa, from_currency, date, file_name) :
   # Funzione per ottenere il tasso di cambio dal sito x-rates
    def fetch_exchange_rate(currency, date):
        url = f"https://www.x-rates.com/historical/?from=EUR&amount=1&date={date}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        rates = {"Euro": "1"}  # Aggiungi Euro come valuta di base
        # Estrazione dei tassi di cambio dalla pagina HTML
        for tr_tag in soup.find_all('tbody')[1]:
            try:
                td_tags = tr_tag.find_all('td')
                rates[td_tags[0].text] = td_tags[1].text
            except Exception:
                pass
        if currency not in rates:
            file_data["errore"].append("Valuta non trovata.\nVerifica che la valuta sia nel formato atteso:\n standard ISO 4217 ")
        return float(rates[currency])

    # Recupera il tasso di cambio dal sito x-rates
    exchange_rate = fetch_exchange_rate(from_currency, date)

    # Se la valuta di origine non è EUR, invertiamo il tasso di cambio
    if from_currency != "EUR":
        exchange_rate = 1 / exchange_rate

    # Logica di conversione: moltiplichiamo per il tasso di cambio
    result = amount * exchange_rate
    result = math.floor(result * 100) / 100

    message1 = f"\n     Tasso di cambio\n   in data {date}:\n\n"
    message2 = f" 1 {divisa} = {exchange_rate:.4f} EUR\n"

    file_messages[file_name] = [message1, message2]

    return result

def random_string(n, charset=string.ascii_letters + string.digits):
    return ''.join(random.choices(charset, k=n))

# Funzione per normalizzare la denominazione
def normalizza_denominazione(denominazione):
    # Rimuove gli spazi e rende tutto maiuscolo
    return re.sub(r'[\s.]', '',  denominazione).lower()

# Funzione per verificare la similarità
def verifica_similarita_fuzzy(str_1, str_2, max_l_dist = 2):
    # Trova una corrispondenza fuzzy tra la denominazione e il testo
    matches = find_near_matches(str_1, str_2, max_l_dist = max_l_dist)  # max_l_dist controlla la distanza di Levenshtein
    return len(matches) > 0

# Funzione per verificare la presenza di una denominazione nel testo
def verifica_denominazione_in_testo(text, cod_iva, anagrafica):#json_file = JSON_FILE
    # Carica i dati dal file JSON
    #with open(json_file, 'r', encoding='utf-8') as file_json:
    #    aziende = json.load(file_json)

    # Normalizza anche il testo da verificare
    testo_normalizzato = normalizza_denominazione(text)

    # Verifica se una delle denominazioni normalizzate è presente nel testo normalizzato
    anagrafica_data = None
    for azienda in anagrafica:
        denominazione_normalizzata = normalizza_denominazione(azienda["Denominazione"])
        partita_iva = azienda["partita_iva"]
        if verifica_similarita_fuzzy(denominazione_normalizzata, testo_normalizzato) or verifica_similarita_fuzzy(partita_iva[2:], cod_iva):
            anagrafica_data = {
                "IdPaese_C": partita_iva[:2],
                "IdCodice_C": partita_iva[2:],
                "Denominazione_C": azienda["Denominazione"],
                "Indirizzo_C": azienda["indirizzo"],
                "CAP_C": azienda["cap"],
                "Comune_C": azienda["comune"],
                "Nazione_C": azienda["nazione"],
            }
            #return anagrafica_data # La denominazione è stata trovata

    return ("n", anagrafica_data) if anagrafica_data else ("s", None)

def text_to_dictionary(text,file_name, anagrafica):
    result = {}

    # Lista delle chiavi che stiamo cercando nel testo
    keys = [
        "IdPaese_T", "IdCodice_T", "IdPaese_P", "IdCodice_P", "Denominazione_P", "Indirizzo_P",
        "CAP_P", "Comune_P", "Nazione_P", "IdPaese_C", "IdCodice_C", "Denominazione_C", "Indirizzo_C",
        "CAP_C", "Comune_C", "Nazione_C", "Divisa", "Numero_fattura", "ImportoTotale",
        "Data_pagamento", "Data_Acquisto", "oggetto_acquistato"
    ]

    # Funzione per pulire gli asterischi ** e i trattini all'inizio della riga
    def clear_text(text_):
        return text_.replace("**", "").lstrip("-").strip()

    for key in keys:
        # La regex cerca la chiave seguita da ": " e cattura tutto il valore dopo
        pattern = r'(\*{0,2}' + re.escape(key) + r'\*{0,2})\s*:\s*(.*?)(?=\n|$)'
        match = re.search(pattern, text)

        if match:
            # Pulisce la chiave e il valore trovati, rimuovendo trattini e asterischi
            clear_value = clear_text(match.group(2))
            result[key] = clear_value
        else:
            raise KeyError

    result = {key: "" if value == "vuoto" else value for key, value in result.items()}

    original_valuta = result["Divisa"]
    original_total = result["ImportoTotale"]

    varx, anagrafica_data = verifica_denominazione_in_testo(result["Denominazione_C"], result["IdCodice_C"], anagrafica)
    if anagrafica_data and isinstance(anagrafica_data, dict):
        result["IdPaese_C"]= anagrafica_data["IdPaese_C"]
        result["IdCodice_C"]= anagrafica_data["IdCodice_C"]
        result["Denominazione_C"]= anagrafica_data["Denominazione_C"]
        result["Indirizzo_C"]= anagrafica_data["Indirizzo_C"]
        result["CAP_C"]= anagrafica_data["CAP_C"]
        result["Comune_C"]= anagrafica_data["Comune_C"]
        result["Nazione_C"]= anagrafica_data["Nazione_C"]
    else:
        pass

    # Verifica necessità di conversione valuta
    if "ImportoTotale" in result and "Divisa" in result:
        try:
            importo_val = float(result["ImportoTotale"])
            valuta = result["Divisa"]
            if valuta in currency_mapping and valuta != "EUR":
                nuovo_importo= convert_to_euro(importo_val,valuta, currency_mapping[valuta], result["Data_pagamento"],file_name)
                result["ImportoTotale"] = f"{nuovo_importo:.2f}"
                result["Divisa"] = "EUR"
        except ValueError as v:
            file_data["errore"].append(f"Qualcosa è andato storto durante\nil calcolo del cambio valuta.\n FILE: {file_name}\n{v}")
            result["ImportoTotale"] = ""
            result["Divisa"] = "EUR"

    # Numero_Fattura senza caratteri speciali
    numero_fattura = re.sub(r'[^a-zA-Z0-9]', '', result['Numero_fattura'])[-10:]
    result['Numero_fattura'] = numero_fattura

    # Indirizzo corto
    result["Indirizzo_P"] = result["Indirizzo_P"][:30]

    # Controlla "Nazione_P"
    result["CAP_P"] = "00000"

    # standardizzazione comune fornitore
    if result["Nazione_P"] in country_fcomune.keys():
        result["Comune_P"] = country_fcomune[result["Nazione_P"]]

    # aggiunge ProgressivoInvio
    result['ProgressivoInvio'] = random_string(5)

    # controlo P.iva "vuoto"
    if result["IdCodice_P"] == "":
        result["IdCodice_P"] = random_string(11, string.digits)

    # controlo P.iva "vuoto"
    if result["IdCodice_T"] == "":
        result["IdCodice_T"] = result["IdCodice_P"]

    # controlla P.iva
    if result['IdPaese_T'] not in countries:
        result['IdPaese_T'] = result['Nazione_P']

    if result['IdPaese_P'] not in countries:
        result['IdPaese_P'] = result['Nazione_P']

    if result['IdPaese_C'] not in countries:
        result['IdPaese_C'] = result['Nazione_C']

    return result, original_valuta, original_total, varx

def openai_text_processing(api_openai, text):
    client = OpenAI(api_key=api_openai)
    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def error_control(err_message):
    file_data["errore"].append(err_message)
    return file_data

def process_file(file_path,file_name, anagrafica):
    try:
        # Estrai il testo dal PDF
        text = extract_text_from_pdf(file_path, file_name)

        # API
        api_openai = os.getenv('api_openAi')

        # Legge prompt // variabile creata all'inizio
        # Estrae le informazioni usando OpenAI
        data = """
            Trasmittente (chi invia la fattura):
            IdPaese_T: EU
            IdCodice_T: 372041333

            Prestatore (fornitore):
            IdPaese_P: EU
            IdCodice_P: 372041333
            Denominazione_P: OpenAl, LLC
            Indirizzo_P: 548 Market Street, PMB 97273
            CAP_P: 94104-5401
            Comune_P: San Francisco
            Nazione_P: US

            Committente (cliente):
            IdPaese_C: IT
            IdCodice_C: 04508350875
            Denominazione_C: MOTO 2000 SRL Unipersonale
            Indirizzo_C: Via Etnea, 58
            CAP_C: 95030
            Comune_C: Gravina di Catania
            Nazione_C: IT

            Informazioni sulla fattura:
            Divisa: USD
            Numero_fattura: 6ED1216B-0002
            ImportoTotale: 20.00
            Data_pagamento: 2025-01-10
            Data_Acquisto: 2025-01-10
            oggetto_acquistato: ChatGPT Plus Subscription
        """
        """
        try:
            data = openai_text_processing(api_openai, text)
        except Exception as o:
            return error_control(f"Errore OpenAI: {o}")
        """
        # Converte i dati estratti in un formato strutturato
        try:
            data_dict, original_valuta, original_total, varx = text_to_dictionary(data, file_name, anagrafica)
        except Exception as e:
            return error_control(f"Errore nella conversione dei dati: {e}")

        file_data["data_dict"] = data_dict
        file_data["original_valuta"] = original_valuta
        file_data["original_total"] = original_total
        file_data["varx"] = varx

    except KeyError as k:
        return error_control(f"Dati estratti non validi: {k}")

    except requests.exceptions.ConnectionError as c:
        return error_control(f"Errore di Connessione: {c}")

    except requests.exceptions.RequestException as r:
        return error_control(f"Errore di richiesta: {r}")

    except Exception as e:
        return error_control(f"Errore durante l'elaborazione: {e}")

    return file_data
