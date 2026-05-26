import os
import logging
import requests
import gradio as gr
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

log.info("Starting Feature Discovery Agent app...")
w = WorkspaceClient()
log.info("WorkspaceClient initialized successfully")

ENDPOINT_NAME = "mas-2a2cd4e8-endpoint"

def call_supervisor(message):
    """Call Supervisor endpoint via direct REST API."""
    # Get workspace host and token from SDK config
    host  = w.config.host
    token = w.config.token

    url = f"{host}/serving-endpoints/{ENDPOINT_NAME}/invocations"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Supervisor Agent uses messages format via REST
    payload = {
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    log.info(f"Calling: {url}")
    log.info(f"Payload: {payload}")

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    log.info(f"Status code: {response.status_code}")
    log.info(f"Raw response: {response.text[:500]}")

    response.raise_for_status()
    data = response.json()

    # Parse response
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    elif "final_response" in data:
        return data["final_response"]
    elif "output" in data:
        return data["output"][0]["content"][0]["text"]
    else:
        log.warning(f"Unknown structure: {list(data.keys())}")
        return str(data)

def chat(message, history):
    log.info(f"Query received: {message}")
    try:
        result = call_supervisor(message)
        log.info(f"Success: {result[:100]}")
        return result
    except Exception as e:
        log.error(f"Error: {str(e)}")
        return f"⚠️ Error: {str(e)}"

demo = gr.ChatInterface(
    fn=chat,
    title="🔍 Feature Discovery Agent",
    description="**Data Engineering · Databricks Agent Bricks**\n\nDescribe your ML objective — I'll find relevant features from the feature store.",
    examples=[
        "I'm building a Trust Propensity Model. What features do we have?",
        "Which features have data quality issues or missed freshness SLA?",
        "What signals are missing for a wealth transfer model?",
        "Find all advisor engagement features in the feature store",
    ],
    chatbot=gr.Chatbot(height=450),
)

port = int(os.environ.get("DATABRICKS_APP_PORT", 8080))
log.info(f"Launching on port {port}")
demo.launch(server_name="0.0.0.0", server_port=port)
