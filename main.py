from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io
import gc # Cop kutusunu bosaltmak icin gerekli

app = FastAPI()

# Lite model (Hafiza dostu)
model_name = "u2netp"
session = new_session(model_name)

@app.get("/")
def home():
    return {"message": "Background Remover API (Ultra Safe Mode) Calisiyor!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 1. Dosyayi oku
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    
    # --- ULTRA HAFIZA AYARI ---
    # 512MB RAM cok az oldugu icin resmi 600 piksele dusuruyoruz.
    # Bu boyut ucretsiz sunucu icin en guvenli limittir.
    max_dimension = 600 
    if input_image.width > max_dimension or input_image.height > max_dimension:
        input_image.thumbnail((max_dimension, max_dimension))
    # ---------------------------
    
    # 2. Arka plani sil (Lite model ile)
    output_image = remove(input_image, session=session)
    
    # 3. Sonucu gonder
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Copleri temizle (Hafizayi rahatlat)
    del image_data
    del input_image
    del output_image
    gc.collect()
    
    return Response(content=img_byte_arr, media_type="image/png")