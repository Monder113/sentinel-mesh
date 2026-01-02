import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px

# SAYFA AYARLARI
st.set_page_config(
    page_title="Sentinel Mesh Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# İzlenecek Düğümler
NODES = ["http://localhost:5000", "http://localhost:5001","http://localhost:5002"]

# BAŞLIK VE STİL
st.title("🛡️ Sentinel Mesh: AI-Driven Decentralized Security")
st.markdown("### *Real-Time Threat Monitoring & Blockchain Consensus Interface*")
st.markdown("---")

# KOMUTA PANELİ (SIDEBAR) 
st.sidebar.header("🕹️ Node Control Operations")
target_node = st.sidebar.selectbox("Select Target Node", NODES)

st.sidebar.subheader("Action Menu")
col_s1, col_s2 = st.sidebar.columns(2)

# 1. AI Tarama Butonu 
if col_s1.button("🔍 Run AI Scan"):
    try:
        res = requests.get(f"{target_node}/scan", timeout=2)
        data = res.json()
        if "ANOMALY" in data.get("result", ""):
            st.sidebar.error(f"🚨 {data['result']}")
        else:
            st.sidebar.success(f"✅ {data['result']}")
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")

# 2. Mining Butonu
if col_s2.button("⚒️ Mine Block"):
    try:
        res = requests.get(f"{target_node}/mine", timeout=2)
        if res.status_code == 200:
            st.sidebar.success("Block Successfully Mined! 🧱")
            st.balloons()
        elif res.status_code == 403:
            st.sidebar.warning("⚠️ Reputation too low to mine.")
        else:
            st.sidebar.error(res.json().get("message", "Error"))
    except:
        st.sidebar.error("Node not reachable")

st.sidebar.markdown("---")
st.sidebar.subheader("Debug Tools")

# 3. İtibar Boost (Sunumda Hızlandırmak İçin Gerekli Olabilir)
if st.sidebar.button("🚀 Boost Reputation (+10)"):
    try:
        requests.get(f"{target_node}/reputation/boost", timeout=2)
        st.sidebar.info("Reputation Boosted! 📈")
    except:
        st.sidebar.error("Connection Failed")

# Otomatik Yenileme
auto_refresh = st.sidebar.checkbox("Auto Refresh Data (2s)", value=True)

#VERİ ÇEKME FONKSİYONU 
def get_network_data():
    all_info = []
    for url in NODES:
        try:
            status = requests.get(f"{url}/status", timeout=1).json()
            chain_resp = requests.get(f"{url}/chain", timeout=1).json()
            
            # Get contract data
            try:
                contracts_resp = requests.get(f"{url}/contracts", timeout=1).json()
                contract_status = contracts_resp.get('status', {})
            except Exception:
                contract_status = {}
            
            all_info.append({
                "URL": url,
                "ID": status.get('id', 'Unknown'),
                "Reputation": status.get('reputation', 0),
                "Pending Alerts": status.get('pending_alerts', 0),
                "Peer Count": status.get('peer_count', 0),
                "Chain Length": chain_resp.get('length', 0),
                "Blocks": chain_resp.get('chain', []),
                "Status": "Active",
                "Color": "green",
                "Contracts": contract_status
            })
        except Exception:
            all_info.append({
                "URL": url, 
                "ID": "-", 
                "Reputation": 0, 
                "Pending Alerts": 0,
                "Peer Count": 0,
                "Chain Length": 0, 
                "Blocks": [],
                "Status": "Offline",
                "Color": "red",
                "Contracts": {}
            })
    return all_info

network_data = get_network_data()

# GÖRSELLEŞTİRME

# 1. Üst Metrikler
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
active_nodes = sum(1 for n in network_data if n["Status"] == "Active")
max_height = max([n["Chain Length"] for n in network_data]) if network_data else 0

kpi1.metric("Active Nodes", f"{active_nodes}/{len(NODES)}")
kpi2.metric("Blockchain Height", max_height)
kpi3.metric("Network Connectivity", "Mesh Active" if active_nodes > 1 else "Partitioned")
kpi4.metric("Avg Reputation", f"{sum([n['Reputation'] for n in network_data])/len(NODES):.1f}" if len(NODES)>0 else "0")

# Smart Contract Status Section
st.markdown("---")
st.subheader("📜 Smart Contract Defense System")

col_contracts, col_actions = st.columns([1, 1])

with col_contracts:
    st.markdown("**Active Contracts**")
    # Get contracts from first active node
    active_node_data = next((n for n in network_data if n['Status'] == 'Active'), None)
    if active_node_data and active_node_data.get('Contracts'):
        contracts = active_node_data['Contracts']
        st.metric("Enabled Contracts", contracts.get('enabled_contracts', 0))
        st.metric("Blocked IPs", len(contracts.get('blocked_ips', [])))
        st.metric("Actions Executed", contracts.get('total_actions_executed', 0))
    else:
        st.info("Contract data unavailable")

with col_actions:
    st.markdown("**Recent Actions**")
    if active_node_data and active_node_data.get('Contracts'):
        recent = active_node_data['Contracts'].get('recent_actions', [])
        if recent:
            for action in recent[-3:]:
                action_icon = {"BLOCK_IP": "🚫", "RATE_LIMIT": "⏱️", "QUARANTINE": "🔒", "ALERT_NETWORK": "📢"}
                icon = action_icon.get(action['action'], "⚡")
                st.success(f"{icon} {action['contract']}: {action['action']}")
        else:
            st.info("No actions triggered yet")
    else:
        st.info("No contract activity")

st.markdown("---")

# 2. Tablo ve Grafik
col_main, col_chart = st.columns([1, 1])

with col_main:
    st.subheader("📡 Live Node Status")
    df_nodes = pd.DataFrame(network_data)[["URL", "ID", "Reputation", "Peer Count", "Status"]]
    st.dataframe(df_nodes, use_container_width=True, hide_index=True)

with col_chart:
    st.subheader("📊 Trust Score (PoR)")
    if not df_nodes.empty:
        fig = px.bar(
            df_nodes, x="URL", y="Reputation", color="Reputation", 
            range_y=[0, 100], color_continuous_scale="Viridis", text="Reputation"
        )
        st.plotly_chart(fig, use_container_width=True)

# 3. Blokzinciri Defteri
st.subheader("🔗 Distributed Ledger Explorer")
cols = st.columns(len(network_data))

for i, node in enumerate(network_data):
    with cols[i]:
        status_icon = "🟢" if node['Status'] == "Active" else "🔴"
        st.markdown(f"### {status_icon} Node {5000+i}")
        st.caption(f"Addr: {node['URL']} | Peers: {node['Peer Count']}")
        
        if node['Blocks']:
            for block in reversed(node['Blocks']):
                with st.expander(f"📦 Block #{block['index']} ({len(block['alerts'])} alerts)"):
                    st.code(f"Hash: {block['hash']}", language="text")
                    st.write("**Timestamp:**", block['timestamp'])
                    st.write("**Validator:**", block.get('sender', 'Unknown'))
                    st.json(block['alerts'])
        else:
            st.warning("No blocks found")

if auto_refresh:
    time.sleep(2)
    st.rerun()