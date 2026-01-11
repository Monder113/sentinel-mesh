# 🛡️ Sentinel Mesh: Decentralized AI-Driven Cybersecurity Network

**Sentinel Mesh** is a next-generation, decentralized cybersecurity ecosystem designed to secure networks against sophisticated cyber threats. 

By combining **Artificial Intelligence (Autoencoders)** for anomaly detection with a custom **Blockchain** protocol for immutable logging, this project creates a resilient, self-healing network where nodes collaborate to detect and block threats using a **Proof-of-Reputation (PoR)** consensus mechanism.

---

## 🚀 Key Features

* **🧠 AI-Powered Anomaly Detection:** Utilizes a PyTorch-based *Autoencoder* to detect zero-day attacks and traffic anomalies with high precision (trained on the CICIDS2017 dataset).
* **🔗 Custom Blockchain Protocol:** A fully functional, Python-based blockchain implementation featuring SHA-256 hashing, chain validation, and automatic conflict resolution.
* **⭐ Proof-of-Reputation (PoR):** An energy-efficient consensus algorithm. Unlike Proof-of-Work, nodes must earn a "Reputation Score" (>50) by performing honest network tasks to validate blocks.
* **📜 Smart Contracts:** Automated defense system that triggers actions (BLOCK_IP, RATE_LIMIT, QUARANTINE) when threats are detected.
* **📡 Decentralized P2P Sync:** Features automatic peer discovery and ledger synchronization. Nodes automatically resolve chain forks to maintain a single truth.
* **📊 Real-Time Command Center:** An interactive Streamlit dashboard to monitor network health, visualize the blockchain ledger, and audit node reputation.

### 📸 Dashboard Preview
![Sentinel Mesh Dashboard Explorer](assets/dashboard_preview.png)
*The interactive dashboard showing real-time block verification and node data in Turkish.*

---

## 🛠️ System Architecture

The system relies on a collaborative mesh network where AI Agents (Walker Nodes) continuously scan traffic and validate each other's findings via the blockchain.

![Sentinel Mesh Architecture Diagram](assets/architecture_diagram.png)

The system is composed of five main modules:

1.  **The Eye (`detector.py`):** The Deep Learning module that scans network traffic samples and calculates reconstruction error (MSE) to flag anomalies.
2.  **The Memory (`blockchain.py`):** A distributed ledger that stores verified threat alerts. It ensures data integrity using cryptographic linking.
3.  **The Brain (`node.py`):** A Flask-based REST API acting as the network node. It handles mining, P2P communication, and reputation management.
4.  **The Shield (`contracts.py`):** Smart contract engine that automatically triggers defensive actions when threats are detected.
5.  **The Interface (`dashboard.py`):** A visual front-end for network administrators to monitor nodes and control the simulation.

---

## 📦 Installation

### Prerequisites
* Python 3.8 or higher
* Git

### 1. Clone the Repository
```bash
git clone https://github.com/onder-m/sentinel-mesh.git 
cd sentinel-mesh 
```

### 2. Set Up Virtual Environment (Recommended)
--Windows--
```bash
python -m venv venv
venv\Scripts\activate
```
--macOS/Linux--
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🎮 Usage & Simulation Guide

To simulate a decentralized network, you need to run multiple nodes and the dashboard simultaneously. Open separate terminals for each command.

### Step 1: Initialize the Seed Node (Node A)
Start the first node on port 5000. This acts as the genesis peer:
```bash
python node.py -p 5000
```
### Step 2: Initialize a Peer Node (Node B)
Start a second node on port 5001 and connect it to Node A:
```bash
python node.py -p 5001 --peers localhost:5000
```
*(You can add more nodes by changing the port: `-p 5002`, `-p 5003`, etc.)*

### Step 3: Launch the Dashboard
Start the command center to visualize the network.
```bash
streamlit run dashboard.py
```

---

## 🧪 Simulation Scenarios

Once the system is running, use the Dashboard sidebar to test the following scenarios:

1.  **AI Anomaly Scan (Natural Detection):**
    * Click **"Run AI Scan"**. The node will sample random traffic data from the test set.
    * The AI model analyzes the sample in real-time.
    * *Result:* It returns either "Traffic Normal" or "ANOMALY DETECTED" (if the sampled data contains attack patterns).

2.  **Mining & Consensus (PoR Test):**
    * Initially, nodes have a reputation of 10 (Threshold is 50).
    * Try clicking **"Mine Block"** -> It will fail (Unauthorized).
    * Click **"Boost Reputation"** (Debug Tool) to increase the score above 50.
    * Click **"Mine Block"** again -> Success! The block is added to the local chain.

3.  **Ledger Synchronization:**
    * Mine a block on Node A.
    * Check Node B on the dashboard. It will automatically sync and display the same block height, proving P2P consensus is working correctly.

---

## 📂 Project Structure

```text
sentinel-mesh/
├── core/
│   ├── blockchain.py       # 🧠 Core Blockchain logic & Consensus (PoR)
│   ├── detector.py         # 👁️ PyTorch Autoencoder Model Wrapper
│   └── contracts.py        # 📜 Smart Contract Engine for auto-defense
├── utils/
│   ├── data_helper.py      # 🛠️ Data loading & preprocessing tools
│   └── scaler.pkl          # ⚖️ Pre-fitted Scaler for normalization
├── models/
│   └── saved_models/
│       ├── autoencoder.pth # 🤖 Trained AI Model weights
│       └── ae_threshold.npy# 📉 Threshold value for anomaly detection
├── data/
│   └── processed/          # 📂 Processed/Scaled test datasets
├── node.py                 # 🚀 Main P2P Node Application (Flask API)
├── dashboard.py            # 📊 User Interface (Streamlit)
├── requirements.txt        # 📦 Project dependencies
└── README.md               # 📄 Project Documentation
```

--------------------------------------------------------------------------------

## 📜 Future Roadmap

* [ ] Implementation of **Digital Signatures (RSA/ECC)** for alert verification.
* [x] ~~**Smart Contract** layer for automated response strategies.~~ ✅ Implemented!
* [ ] **Docker** support for rapid cloud deployment.
* [ ] Integration of a **Slashing Mechanism** to penalize malicious nodes.


## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

Developed as a **Computer Engineering Final Project**.
