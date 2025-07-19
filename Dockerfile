FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Copia i file di progetto
COPY . .

# Installa le dipendenze
RUN pip install --upgrade pip && pip install -r requirements.txt

# Esponi la porta
EXPOSE 10000

# Comando per avviare l'app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
