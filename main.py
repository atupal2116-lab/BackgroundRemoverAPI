import os
# --- KRITIK RAM AYARLARI (En Basa Yazilmali) ---
# Islemciyi tek cekirdekle sinirliyoruz ki RAM tasmasin.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
# -----------------------------------------------

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io
import gc

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Background Remover API (Final Mode) Calisiyor!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 1. Dosyayi oku
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    
    # 2. Resmi Garanti Boyuta Getir (350px)
    # 512MB RAM icin en guvenli limittir. Kalite mobilde hala iyidir.
    max_dimension = 350
    if input_image.width > max_dimension or input_image.height > max_dimension:
        input_image.thumbnail((max_dimension, max_dimension))
    
    # 3. Yapay Zekayi Baslat (u2netp - Lite Model)
    # Lazy Loading: Sadece istek gelince calisir.
    session = new_session("u2netp")
    output_image = remove(input_image, session=session)
    
    # 4. Sonucu Hazirla
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 5. RAM Temizligi (Cok Agresif)
    del session
    del image_data
    del input_image
    del output_image
    gc.collect() # Copleri hemen at
    
    return Response(content=img_byte_arr, media_type="image/png")