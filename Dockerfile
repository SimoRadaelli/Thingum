# Utilizza un'immagine base con Python
FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt nella directory di lavoro
COPY requirements.txt /app/

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del progetto nella directory di lavoro
COPY . /app/

# Esponi la porta 8000 (la porta predefinita di FastAPI)
EXPOSE 8000

# Comando per avviare il server FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
