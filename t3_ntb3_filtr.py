import os
import csv
import zipfile
import requests
import io
import re

print("Výpis adres podle zadání")
obec = input("\nZadejte název obce: ")
ulice = input("Zadejte název ulice: ")

# cesta k programu
program_path = os.path.dirname(os.path.abspath(__file__))

# doplnění aspx
url_zaklad = 'https://nahlizenidokn.cuzk.cz/StahniAdresniMistaRUIAN.aspx'
response = requests.get(url_zaklad)
html = response.text
matches = re.findall(r'href=[\'"]?([^\'" >]+_OB_ADR_csv\.zip)', html)
url = matches[0]
datum = url.split("/")[-1][:-15]

# stahování souboru do paměti
zip_data = requests.get(url).content
csv_files = "csv_files_" + datum

# vytvoření adresáře pro rozbalení souborů z zip archivu
csv_files_path = os.path.join(program_path, csv_files)
os.makedirs(csv_files_path, exist_ok=True)

# rozbalení souborů z zip archivu do adresáře
with zipfile.ZipFile(io.BytesIO(zip_data)) as myzip:
    for file in myzip.namelist():
        if "CSV" in file.upper() and file.upper().endswith(".CSV"):
            myzip.extract(file, path= csv_files_path)

# vytvoření nového csv souboru pro uložení vybraných záznamů
nazev_csv = obec +"_" + ulice + "_" + datum + ".csv"
filtered_data_path = os.path.join(program_path, nazev_csv)
with open(filtered_data_path, "w", newline="", encoding="cp1250") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    writer.writerow(["Ulice", "č.p.", "č.or.", "písmeno", "Obec", "PSČ"])
    
    # zapsání vybraných řádků do souboru
    for root, dirs, files in os.walk(csv_files_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", newline="", encoding="cp1250") as csv_file:
                reader = csv.DictReader(csv_file, delimiter=";")
                for row in reader:
                    if row["Název obce"] == obec and row["Název ulice"] == ulice:
                        writer.writerow([row["Název ulice"],  row["Číslo domovní"], row["Číslo orientační"], row["Znak čísla orientačního"], row["Název obce"], row["PSČ"]])

print(f"\nVybraná data jsou uložena v souboru {nazev_csv}\nNajdete jej ve stejném adresáři, ze kterého spouštíte tento script\nJe zde také podadresář {csv_files} s daty všech obcí")