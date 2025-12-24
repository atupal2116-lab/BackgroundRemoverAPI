from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io
import gc

app = FastAPI()

@app.get("/")
def home():
    # Bu sayfa artik hic RAM yemez, aninda acilir.
    return {"message": "Background Remover API (Lazy Mode) Calisiyor!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 1. Dosyayi oku
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    
    # 2. Resim boyutunu kucult (RAM korumasi)
    max_dimension = 600
    if input_image.width > max_dimension or input_image.height > max_dimension:
        input_image.thumbnail((max_dimension, max_dimension))
    
    # 3. YAPAY ZEKAYI BURADA CAGIRIYORUZ (Sadece istek gelince calisir)
    # u2netp (Lite model) kullaniyoruz
    session = new_session("u2netp")
    output_image = remove(input_image, session=session)
    
    # 4. Sonucu hazirla
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 5. Temizlik yap (Hafizayi bosalt)
    del image_data
    del input_image
    del output_image
    del session # Oturumu kapat
    gc.collect()
    
    return Response(content=img_byte_arr, media_type="image/png")