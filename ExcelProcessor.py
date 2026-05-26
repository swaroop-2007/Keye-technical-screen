import os
import logging
import json
import gradio as gr
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

log.info("Starting Feature Discovery Agent app...")
w = WorkspaceClient()
log.info("WorkspaceClient initialized successfully")

ENDPOINT_NAME = "mas-2a2cd4e8-endpoint"

def call_supervisor(message):
    """Use SDK's internal authenticated HTTP session directly."""
    
    path = f"/serving-endpoints/{ENDPOINT_NAME}/invocations"
    
    payload = {
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    
    log.info(f"Calling path: {path}")
    log.info(f"Payload: {json.dumps(payload)[:200]}")
    
    # Use SDK's internal _api_client which handles OAuth automatically
    response = w.api_client.do(
        "POST",
        path,
        body=payload
    )
    
    log.info(f"Response type: {type(response)}")
    log.info(f"Response: {str(response)[:500]}")
    
    # Parse response
    if isinstance(response, dict):
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        elif "final_response" in response:
            return response["final_response"]
        elif "output" in response:
            return response["output"][0]["content"][0]["text"]
        else:
            log.warning(f"Keys found: {list(response.keys())}")
            return str(response)
    
    return str(response)

def chat(message, history):
    log.info(f"Query received: {message}")
    try:
        result = call_supervisor(message)
        log.info(f"Success: {result[:200]}")
        return result
    except Exception as e:
        log.error(f"Error: {str(e)}")
        return f"⚠️ Error: {str(e)}"

demo = gr.ChatInterface(
    fn=chat,
    title="🔍 Feature Discovery Agent",
    description="** · Data Engineering · Databricks Agent Bricks**\n\nDescribe your ML objective — I'll find relevant features from the feature store.",
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
