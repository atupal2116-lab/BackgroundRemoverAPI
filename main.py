import os
from fastapi import FastAPI, UploadFile, File
from rembg import remove, new_session
from starlette.responses import Response

# --- AYARLAR ---
# 1. Kütüphaneye, model dosyasını projenin olduğu yerde (.u2net klasöründe) aramasını söylüyoruz.
# Bu satır, importlardan ve işlemlerden önce çalışmalı.
os.environ["U2NET_HOME"] = os.getcwd()

app = FastAPI()

# --- MODEL YÜKLEME ---
# 2. Sunucu başlarken modeli bir kere yükleyip hafızaya alıyoruz (Global Session).
# 'u2netp' kullanıyoruz çünkü hafif ve hızlı.
# 'CPUExecutionProvider' diyerek sadece işlemciyi zorluyoruz (GPU hatasını önler).
print("Model yükleniyor...")
try:
    my_session = new_session("u2netp", providers=['CPUExecutionProvider'])
    print("Model başarıyla yüklendi ve CPU modunda hazır.")
except Exception as e:
    print(f"Model yüklenirken hata oluştu: {e}")

@app.get("/")
def home():
    return {"message": "API calisiyor. /remove-bg adresine POST istegi atabilirsiniz."}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # 3. Gelen resmi okuyoruz
    input_image = await file.read()
    
    # 4. Hazırda bekleyen 'my_session' ile arka planı siliyoruz.
    # Bu yöntem her seferinde modeli yeniden yüklemekten çok daha hızlıdır.
    output_image = remove(input_image, session=my_session)
    
    # 5. Sonucu geri döndürüyoruz
    return Response(content=output_image, media_type="image/png")