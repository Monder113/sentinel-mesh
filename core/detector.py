import torch
import torch.nn as nn
import numpy as np

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        # Encoder: Veriyi sıkıştırır
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.Tanh(),
            nn.Linear(64, 32), nn.Tanh(),
            nn.Linear(32, 16), nn.Tanh()
        )
        # Decoder: Veriyi eski haline getirmeye çalışır
        self.decoder = nn.Sequential(
            nn.Linear(16, 32), nn.Tanh(),
            nn.Linear(32, 64), nn.Tanh(),
            nn.Linear(64, input_dim), nn.Sigmoid()
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

class SentinelDetector:
    def __init__(self, model_path, threshold_path, input_dim):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Autoencoder(input_dim).to(self.device)
        
        # Modeli ve eşik değerini yükle
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.threshold = np.load(threshold_path)[0]
            self.model.eval() # Modeli test/çıkarım moduna al
            print(f"✅ AI Model loaded with threshold: {self.threshold:.6f}")
        except Exception as e:
            print(f"❌ Critical Error loading model: {e}")
            raise

    def predict(self, sample):
        """Tek bir veri satırı üzerinde anomali tespiti yapar."""
        with torch.no_grad():
            # Veriyi Tensor formatına çevir ve GPU/CPU'ya gönder
            sample_tensor = torch.FloatTensor(sample).to(self.device)
            # Geri kurgula
            reconstructed = self.model(sample_tensor)
            # MSE Hatasını hesapla
            mse = torch.mean((reconstructed - sample_tensor)**2).item()
            
            # Karar: Hata > Eşik ise Saldırı (True)
            is_anomaly = mse > self.threshold
            return is_anomaly, mse