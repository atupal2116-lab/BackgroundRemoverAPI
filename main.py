from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io
import gc

app = FastAPI()

@app.get("/")
def home():
    # Bu fonksiyon RAM harcamaz, o yuzden 502 hatasi vermeden aninda acilir.
    return {"message": "Background Remover API Calisiyor!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 1. Resmi oku
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    
    # 2. Resmi Kucult (RAM Sigortasi)
    # 512MB RAM icin 500px en guvenli limittir.
    max_dimension = 500
    if input_image.width > max_dimension or input_image.height > max_dimension:
        input_image.thumbnail((max_dimension, max_dimension))
    
    # 3. YAPAY ZEKAYI SADECE BURADA BASLAT (Lazy Load)
    # 'u2netp' (Lite model) kullaniyoruz.
    # Sunucu acilirken degil, sadece islem yapilacagi an RAM harcar.
    session = new_session("u2netp")
    output_image = remove(input_image, session=session)
    
    # 4. Sonucu hazirla
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 5. TEMIZLIK ZAMANI (Cok Onemli)
    # Is biter bitmez RAM'i bosaltiyoruz ki sunucu cokmesin.
    del session
    del image_data
    del output_image
    del input_image
    gc.collect()
    
    return Response(content=img_byte_arr, media_type="image/png")