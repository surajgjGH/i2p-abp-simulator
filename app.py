import streamlit as st
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

@st.cache_data
def load_abp():
    with open("abp.json") as f:
        return json.load(f)

@st.cache_data
def load_invoices():
    with open("data/invoices.json") as f:
        return json.load(f)

abp = load_abp()
invoices = load_invoices()["invoices"]

st.title("Invoice-to-Pay ABP Simulator (Streamlit Edition)")

if st.button("Run Simulation"):
    logs = []
    audit = []

    for invoice in invoices:
        state = set(invoice["trigger_objects"])
        anomaly = invoice.get("anomaly", None)
        logs.append(f"\n== Invoice {invoice['invoice_id']} ({invoice['path']}) ==")
        if anomaly:
            logs.append(f"⚠️ Anomaly Detected: {anomaly}")

        for agent in abp["agents"]:
            can_trigger = all(obj in state for obj in agent["triggers"])
            if can_trigger:
                logs.append(f"✅ Agent {agent['id']} executed.")
                for o in agent["creates"]:
                    state.add(o)
                status = "executed"
            else:
                logs.append(f"⏳ Agent {agent['id']} skipped.")
                status = "skipped"

            audit.append({
                "invoice_id": invoice["invoice_id"],
                "agent_id": agent["id"],
                "goal": agent["goal"],
                "status": status,
                "timestamp": pd.Timestamp.now(),
                "anomaly": anomaly or ""
            })

    st.subheader("Simulation Log")
    st.code("\n".join(logs), language="text")

    st.subheader("Audit Trail")
    st.dataframe(pd.DataFrame(audit))