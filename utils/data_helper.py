import numpy as np
import joblib
import os

def load_scaler(path='utils/scaler.pkl'):
    """Eğitim sırasında kaydedilen scaler nesnesini yükler."""
    if os.path.exists(path):
        return joblib.load(path)
    else:
        print(f"⚠️ Uyarı: {path} bulunamadı!")
        return None

def get_test_sample(path='data/processed/X_test_scaled.npy', index=0):
    """
    Test veri setinden simülasyon için tek bir satır veri çeker.
    Bu veri, node'un YZ modeline 'yeni trafik' gibi beslenebilir.
    """
    try:
        # mmap_mode='r' sayesinde devasa dosyayı RAM'e yüklemeden sadece ilgili satırı okuruz
        data = np.load(path, mmap_mode='r')
        if index < len(data):
            return data[index].reshape(1, -1)
        else:
            return data[0].reshape(1, -1)
    except Exception as e:
        print(f"⚠️ Test verisi okuma hatası: {e}")
        return None

def preprocess_data(raw_data, scaler):
    """Ham veriyi modelin anlayacağı 0-1 arasına ölçekler."""
    if scaler:
        return scaler.transform(raw_data)
    return raw_data
