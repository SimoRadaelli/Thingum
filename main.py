from fastapi import FastAPI, HTTPException 
import csv 
from typing import List, Dict
from pydantic import BaseModel
from pydantic import BaseModel, Field, ValidationError

app = FastAPI()

CSV_FILE = "dati.csv"


class Item(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str

class UpdateItem(BaseModel):
    nome: str = Field(None, description="Nnuovo Nome")
    cognome: str = Field(None, description="Nuovo Cognome")
    codice_fiscale: str = Field(None, description="Nuovo Codice fiscale")

    class Config:
        extra = "forbid"  # Non permette campi extra

#Lettura CSV
def read_csv() -> List[Dict[str, str]]:
    try:
        print(f"Tentativo di apertura del file: {CSV_FILE}")
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            print(f"Dati letti dal file CSV: {rows}")  # Log dei dati letti
            return rows
    except FileNotFoundError:
        print(f"Errore: il file {CSV_FILE} non esiste!")
        return []


#Scrivere su CSV
def write_csv(data: List[Dict[str, str]]):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "nome", "cognome", "codice_fiscale"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

#Inizializzazione file CSV
try:
    with open(CSV_FILE, mode="x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "nome", "cognome", "codice_fiscale"])
        writer.writeheader()
except FileExistsError:
    pass


#1 Creare nuovo record
@app.post("/items/")
def create_item(item: Item):
    try:
        #Controllo input
        data = read_csv()
        for row in data:
            if row["id"] == str(item.id):
                raise HTTPException(status_code=400, detail="ID già esistente")
        item_dict = item.dict()
        data.append(item_dict)
        write_csv(data)
        return item_dict
    except ValidationError as e:
        #Stampa errore
        print(e.errors())
        raise HTTPException(status_code=422, detail="Errore nella validazione dei dati")
    
#2 Ottenere tutti i record
@app.get("/items/", response_model=List[Dict[str, str]])
def get_all_items():
    return read_csv()


#3 Ottenere singolo record in base all'ID
@app.get("/items/{id}")
def get_item(id: str):
    data = read_csv()
    for row in data:
        if row["id"] == id:
            return row
    raise HTTPException(status_code=404, detail="Record non trovato")

#4 Aggiornare un record in base all'ID
@app.put("/items/{id}")
def update_item(id: str, updated_item: UpdateItem):
    data = read_csv()

    for row in data:
        if row["id"] == id:
            updated_data = updated_item.dict(exclude_unset=True)  # Prende solo i campi forniti
            row.update(updated_data)  # Aggiorna i campi esistenti
            write_csv(data)  # Scrive i dati aggiornati nel CSV
            return {"message": "Record aggiornato con successo", "updated_item": row}

    raise HTTPException(status_code=404, detail="Record non trovato")

#5 Eliminare record 
@app.delete("/items/{id}")
def delete_item(id: str):
    data = read_csv()
    new_data = [row for row in data if row["id"] != id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Record non trovato")
    write_csv(new_data)
    return {"message": "Record eliminato"}

#6 Ottenere numero righe del CSV
@app.get("/items/count")
def count_items():
    print("Funzione count_items chiamata")  # Log di debug
    data = read_csv()  # Leggi i dati dal CSV
    if not data:
        # Se i dati sono vuoti, restituisci un messaggio di errore
        return {"detail": "Record non trovato"}
    return {"count": len(data)}  # Conta le righe e restituisci il conteggio


print("Server avviato correttamente. Endpoint registrati:")
#print(app.openapi())

#uvicorn main:app --reload
#curl http://127.0.0.1:8000/items/count

#@app.get("/items/count")
#def count_items():
    #print("Funzione count_items chiamata")
    #data = read_csv()
    #return {"count": len(data)}