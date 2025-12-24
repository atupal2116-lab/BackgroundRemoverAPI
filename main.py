import os
import gc # Çöp toplayıcı (RAM temizlemek için)
from fastapi import FastAPI, UploadFile, File
from rembg import remove, new_session
from starlette.responses import Response

# --- AYARLAR ---
os.environ["U2NET_HOME"] = os.getcwd()

app = FastAPI()

# Global değişken
my_session = None

@app.on_event("startup")
def load_model():
    global my_session
    print("--- SUNUCU BAŞLATILIYOR ---")
    
    model_path = "u2netp.onnx"
    if os.path.exists(model_path):
        print(f"Dosya bulundu: {model_path}")
    else:
        print(f"UYARI: {model_path} bulunamadı! Lütfen dosyanın yüklendiğinden emin olun.")

    print("Model hafızaya yükleniyor (CPU Modu)...")
    try:
        # Modeli yüklüyoruz
        my_session = new_session("u2netp", providers=['CPUExecutionProvider'])
        print("Model BAŞARIYLA yüklendi.")
    except Exception as e:
        print(f"Model yüklenirken hata: {e}")

@app.get("/")
def home():
    return {"message": "API calisiyor. Durum: Aktif."}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    if my_session is None:
        return {"error": "Model yuklenemedi."}
        
    # 1. Resmi oku
    input_image = await file.read()
    
    try:
        # 2. İşlemi yap
        output_image = remove(input_image, session=my_session)
        
        # 3. Başarılıysa sonucu döndür
        return Response(content=output_image, media_type="image/png")
    
    except Exception as e:
        return {"error": str(e)}
        
    finally:
        # --- KRİTİK BÖLÜM: RAM TEMİZLİĞİ ---
        # İşlem bitince (başarılı olsun veya olmasın)
        # Değişkenleri silip hafızayı temizlemeye zorluyoruz.
        del input_image
        # Eğer output_image tanımlıysa onu return ettik ama garbage collector halleder.
        gc.collect() # Çöpleri topla ve RAM'i boşalt