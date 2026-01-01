import hashlib
import json
import time

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.pending_alerts = []
        # Genesis bloğunu sabit verilerle oluşturuyoruz
        self.create_block(previous_hash='0', sender="GENESIS") 

    def create_block(self, previous_hash, sender=None):
        # Eğer Genesis bloğu (index 1) ise sabit zaman değilse şimdiki zaman
        current_time = 1700000000.0 if len(self.chain) == 0 else time.time()
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': current_time, 
            'alerts': self.pending_alerts,
            'previous_hash': previous_hash,
            'sender': sender
        }
        # Hash hesaplama ve ekleme işlemleri
        block['hash'] = self.calculate_hash(block)
        self.pending_alerts = []
        self.chain.append(block)
        return block
    def add_alert(self, sender, alert_type, confidence):
        alert = {
            'sender': sender,
            'type': alert_type,
            'confidence': round(float(confidence), 4),
            'timestamp': time.time()
        }
        self.pending_alerts.append(alert)
        return self.get_last_block()['index'] + 1

    
    @staticmethod
    def calculate_hash(block):
        # Veriyi sıralı (sort_keys) ve temiz bir stringe çeviriyoruz
        # separatos=(',', ':') ekleyerek gereksiz boşlukları siliyoruz daha kararlı hash için.
        block_content = {k: v for k, v in block.items() if k != 'hash'}
        block_string = json.dumps(block_content, sort_keys=True, separators=(',', ':')).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_last_block(self):
        return self.chain[-1]

    def validate_chain(self, chain_to_check):
        for i in range(1, len(chain_to_check)):
            current = chain_to_check[i]
            prev = chain_to_check[i-1]
            if current['hash'] != self.calculate_hash(current): return False
            if current['previous_hash'] != prev['hash']: return False
        return True
