from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI()

# Kucuk modelin oturumunu baslatiyoruz (u2netp sadece 4MB'dir)
model_name = "u2netp"
session = new_session(model_name)

@app.get("/")
def home():
    return {"message": "Background Remover API (Lite Mode) Calisiyor!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 1. Gelen resim dosyasini oku
    image_data = await file.read()
    
    # 2. Resmi Pillow (PIL) formatina cevir
    input_image = Image.open(io.BytesIO(image_data))
    
    # 3. YAPAY ZEKA SIHRI: Arka plani kaldir (Lite model ile)
    output_image = remove(input_image, session=session)
    
    # 4. Resmi tekrar byte formatina cevir
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 5. Sonucu PNG resmi olarak dondur
    return Response(content=img_byte_arr, media_type="image/png")