import os
import uuid
import requests
import argparse
import numpy as np 
from flask import Flask, jsonify, request
from core.blockchain import Blockchain
from core.detector import SentinelDetector
from core.contracts import ContractEngine
from utils.data_helper import load_scaler, get_test_sample

app = Flask(__name__)

#  DÜĞÜM AYARLARI 
node_id = str(uuid.uuid4())[:8]
blockchain = Blockchain()
peers = set()

# Proof-of-Reputation (PoR) Parametreleri
REPUTATION = {
    "score": 10,       # Başlangıç puanı
    "threshold": 50,   # Blok üretmek için gereken minimum puan
    "reward": 5        # Başarılı blok üretimi ödülü
}

# YZ VE VERİ BİLEŞENLERİ 
scaler = load_scaler('utils/scaler.pkl')
try:
    detector = SentinelDetector(
        model_path='models/saved_models/autoencoder.pth', 
        threshold_path='models/saved_models/ae_threshold.npy', 
        input_dim=77 
    )
    print(f"✅ Sentinel AI Detector Aktif (Node ID: {node_id})")
except Exception as e:
    detector = None
    print(f"❌ YZ Modeli yüklenemedi: {e}")

# SMART CONTRACT ENGINE
contract_engine = ContractEngine()
print(f"📜 Smart Contract Engine initialized with {len(contract_engine.contracts)} contracts")

#1. AĞ TARAMA VE TESPİT (YZ AJANI) 
@app.route('/scan', methods=['GET'])
def scan_network():
    """AI Ajanını kullanarak ağ trafiğini simüle eder ve anomali tarar."""
    if detector is None or scaler is None:
        return jsonify({"error": "AI Engine not ready"}), 500

    # Simülasyon: Test setinden rastgele bir veri satırı çek
    random_index = np.random.randint(0, 2000) 
    sample = get_test_sample('data/processed/X_test_scaled.npy', index=random_index)
    
    if sample is None:
        return jsonify({"error": "Test data not found"}), 404

    # Yapay Zeka Analizi
    is_anomaly, mse_loss = detector.predict(sample)

    if is_anomaly:
        # AI tehdit bulursa, otomatik olarak Blockchain havuzuna ekler
        blockchain.add_alert(
            sender=node_id,
            alert_type="AI_ANOMALY_DETECTED",
            confidence=mse_loss
        )
        
        # Smart Contract Evaluation - trigger automated responses
        simulated_ip = f"192.168.1.{random_index % 255}"
        executed_actions = contract_engine.evaluate(
            alert_type="AI_ANOMALY_DETECTED",
            confidence=mse_loss,
            source_ip=simulated_ip
        )
        
        return jsonify({
            "result": "ANOMALY DETECTED!",
            "loss": mse_loss,
            "status": "Alert added to pending pool",
            "contracts_triggered": len(executed_actions),
            "actions": [a.action.value for a in executed_actions]
        }), 201
    
    return jsonify({"result": "Traffic Normal", "loss": mse_loss}), 200

# 2. BLOK ÜRETİMİ (POR KONTROLÜ)
@app.route('/mine', methods=['GET'])
def mine():
    """PoR protokolüne göre blok üretir ve düğüme itibar kazandırır."""
    # Güvenlik Kontrolü: İtibar puanı barajın altındaysa izin verme
    if REPUTATION["score"] < REPUTATION["threshold"]:
        return jsonify({
            "error": "Unauthorized", 
            "message": f"Reputation too low ({REPUTATION['score']}/{REPUTATION['threshold']})"
        }), 403

    # Havuz Kontrolü: Bekleyen alarm yoksa blok üretme
    if not blockchain.pending_alerts:
        return jsonify({"message": "No pending alerts in pool"}), 200

    last_block = blockchain.get_last_block()
    new_block = blockchain.create_block(last_block['hash'], node_id)
    
    if new_block:
        #otomatik ödül: Başarılı blok mühürlendiği için itibar artar
        REPUTATION["score"] += REPUTATION["reward"]
        print(f"Reputation Score Updated: {REPUTATION['score']}")
    
    return jsonify({
        "message": "New Block Successfully Mined", 
        "block": new_block,
        "new_reputation": REPUTATION["score"]
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Düğümün sağlık ve ağ bilgisini raporlar."""
    return jsonify({
        "id": node_id,
        "reputation": REPUTATION["score"],
        "pending_alerts": len(blockchain.pending_alerts),
        "chain_length": len(blockchain.chain),
        "peer_count": len(peers),
        "peers": list(peers),
        "status": "Active"
    }), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

@app.route('/nodes/register', methods=['POST'])
def register():
    data = request.get_json()
    nodes = data.get('nodes')
    if nodes:
        for node in nodes: peers.add(node)
    return jsonify({"total_peers": list(peers)}), 201

@app.route('/nodes/resolve', methods=['GET'])
def resolve():
    longest_chain = None
    max_length = len(blockchain.chain)
    
    print(f"🔍 Resolve tetiklendi. Mevcut uzunluk: {max_length}")
    print(f"📡 Kontrol edilen peer listesi: {list(peers)}")

    for peer in peers:
        try:
            # peer değişkeni zaten 'http://...' içerdiği için tekrar eklemiyoruz
            url = f"{peer}/chain" if peer.startswith('http') else f"http://{peer}/chain"
            print(f"🌐 {url} adresine bağlanılıyor...")
            
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                print(f"📊 Peer uzunluğu: {length} | Benimki: {max_length}")
                
                if length > max_length:
                    print("⚙️ Zincir daha uzun, doğrulama (validation) başlatılıyor...")
                    if blockchain.validate_chain(chain):
                        max_length = length
                        longest_chain = chain
                        print("✅ Zincir geçerli bulundu!")
                    else:
                        print("❌ Zincir doğrulama hatası! (Genesis uyuşmazlığı olabilir)")
        except Exception as e:
            print(f"⚠️ {peer} düğümüne ulaşılamadı: {e}")
            continue
        
    if longest_chain:
        blockchain.chain = longest_chain
        return jsonify({"message": "Synchronized", "new_length": max_length}), 200
    
    return jsonify({"message": "Already up to date or validation failed"}), 200

# 4. GELİŞTİRME VE TEST ARAÇLARI
@app.route('/reputation/boost', methods=['GET', 'POST'])
def boost():
    """Sadece test/sunum amaçlı manuel itibar artırıcı."""
    REPUTATION["score"] += 10
    return jsonify({"message": "Test Boost Applied", "new_score": REPUTATION["score"]}), 200

@app.route('/alert/new', methods=['POST'])
def manual_alert():
    """Dışarıdan manuel alarm enjekte etmek için."""
    values = request.get_json()
    required = ['sender', 'type', 'confidence']
    if not all(k in values for k in required): return 'Missing data', 400
    index = blockchain.add_alert(values['sender'], values['type'], values['confidence'])
    return jsonify({'message': f'Manual alert added to block {index}'}), 201

# 5. SMART CONTRACT API
@app.route('/contracts', methods=['GET'])
def get_contracts():
    """List all smart contracts and their current status."""
    return jsonify({
        "contracts": contract_engine.get_contracts_info(),
        "status": contract_engine.get_status()
    }), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sentinel Mesh Node")
    
    # -p veya --port port belirlenir (varsayılan 5000)
    parser.add_argument('-p', '--port', default=5000, type=int)
    
    # --peers ile başlangıçta bağlanılacak düğümler alınır
    parser.add_argument('--peers', nargs='*', help='Initial peer list (e.g. 127.0.0.1:5000)')
    
    args = parser.parse_args()

    # Eğer başlangıçta peer adresleri verilmişse, bunları peers listesine ekle
    if args.peers:
        for peer_addr in args.peers:
            # Başına http:// ekli değilse :
            formatted_peer = peer_addr if peer_addr.startswith('http') else f"http://{peer_addr}"
            peers.add(formatted_peer)
            print(f"🔗 Startup: Registered initial peer: {formatted_peer}")

    # Sunucuyu başlat
    app.run(host='0.0.0.0', port=args.port)