# --- EN HAFIF BASLANGIC KODU ---
# Burada sadece sunucuyu ayakta tutacak
# en temel seyleri cagiriyoruz.
# Agir kutuphaneleri (rembg, PIL) bilerek buraya yazmiyoruz.
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
import io
import gc

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API Hazir ve Hizli!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # --- SIHIRLI DOKUNUS BURADA ---
    # Render "Start" dediginde bu kisim calismaz, o yuzden aninda acilir.
    # Bu agir kutuphaneleri SADECE biri resim gonderince cagiriyoruz.
    from rembg import remove, new_session
    from PIL import Image
    
    # 1. Dosyayi oku
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    
    # 2. Boyutlandirma (RAM Korumasi - 300px)
    # 512MB RAM icin en guvenli ve hizli boyut budur.
    max_dimension = 300
    if input_image.width > max_dimension or input_image.height > max_dimension:
        input_image.thumbnail((max_dimension, max_dimension))
    
    # 3. Islemci Ayarlari (RAM Tasmasini Engeller)
    os.environ["OMP_NUM_THREADS"] = "1"
    
    # 4. Yapay Zekayi Calistir (Lite Model)
    session = new_session("u2netp")
    output_image = remove(input_image, session=session)
    
    # 5. Sonucu Kaydet
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 6. Temizlik (Garbage Collector)
    del session
    del input_image
    del output_image
    del image_data
    gc.collect()
    
    return Response(content=img_byte_arr, media_type="image/png")