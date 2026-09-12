from datetime import datetime, timedelta

def get_bot_telemetry() -> dict:
    try:
        r = requests.get(f"{JSONBIN_URL}/latest", headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
        if r.status_code == 200:
            record = r.json().get("record", {})
            
            # Check if the local PC script is actively sending heartbeats
            heartbeat_str = record.get("last_heartbeat")
            if heartbeat_str:
                try:
                    hb_time = datetime.strptime(heartbeat_str, '%Y-%m-%d %H:%M:%S')
                    # If heartbeat is older than 20 seconds, PC is offline
                    if datetime.utcnow() - hb_time > timedelta(seconds=20):
                        record["pc_online"] = False
                    else:
                        record["pc_online"] = True
                except Exception:
                    record["pc_online"] = False
            else:
                record["pc_online"] = False
                
            return record
    except Exception:
        pass
    return {
        "bot_active": True, 
        "account_equity": 0.0, 
        "account_balance": 0.0, 
        "open_trades_count": 0, 
        "pc_online": False
    }

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(JSONBIN_URL, json=current, headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

def render_bot_control_widget():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Live MT5 Telemetry")
    
    telemetry = get_bot_telemetry()
    pc_online = telemetry.get("pc_online", False)
    bot_active = telemetry.get("bot_active", True)
    equity = telemetry.get("account_equity", 0.0)
    balance = telemetry.get("account_balance", 0.0)
    open_count = telemetry.get("open_trades_count", 0)
    
    # Display real-time connection status
    if not pc_online:
        st.sidebar.error("PC Status: OFFLINE 💀")
        st.sidebar.caption("Run `RichforeverAI_2.py` on your PC.")
    else:
        st.sidebar.success("PC Status: CONNECTED 🟢")
        st.sidebar.metric("Account Equity", f"${equity:,.2f}")
        st.sidebar.metric("Account Balance", f"${balance:,.2f}")
        st.sidebar.metric("Active Positions", open_count)
        
        if bot_active:
            st.sidebar.success("Engine State: ACTIVE 🟢")
            if st.sidebar.button("🔴 PAUSE ENGINE", use_container_width=True):
                set_bot_status(False)
                st.rerun()
        else:
            st.sidebar.warning("Engine State: PAUSED 🔴")
            if st.sidebar.button("🟢 RESUME ENGINE", use_container_width=True):
                set_bot_status(True)
                st.rerun()
