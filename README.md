# Booking Alert Backend

## Deployment on [Render.com](https://render.com)

1. Go to https://dashboard.render.com
2. Click **"New Web Service"**
3. Connect your GitHub and create a new repository with this code
4. Use these settings:
   - **Build Command**: *(leave empty)*
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - **Environment**: Python
   - **Plan**: Free

## API Endpoints

- `GET /searches` → Lista delle ricerche salvate
- `POST /searches` → Aggiungi nuova ricerca (JSON)
- `DELETE /searches/{index}` → Elimina ricerca per indice
