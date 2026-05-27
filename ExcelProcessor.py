app_code = """
import os, logging, json, gradio as gr
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

w = WorkspaceClient()
ENDPOINT = "mas-2a2cd4e8-endpoint"

def chat(message, history):
    try:
        response = w.api_client.do(
            "POST",
            f"/serving-endpoints/{ENDPOINT}/invocations",
            body={"input": [{"role": "user", "content": message}]}
        )
        log.info(f"Response: {str(response)[:300]}")
        if isinstance(response, dict):
            for key in ["final_response", "output", "choices", "predictions"]:
                if key in response and response[key]:
                    val = response[key]
                    if key == "choices":
                        return val[0]["message"]["content"]
                    if key == "output":
                        return val[0]["content"][0]["text"]
                    return str(val) if not isinstance(val, str) else val
        return str(response)
    except Exception as e:
        log.error(str(e))
        return f"Error: {str(e)}"

demo = gr.ChatInterface(
    fn=chat,
    title="Feature Discovery Agent",
    description="Data Engineering · Databricks Agent Bricks",
    examples=[
        "I'm building a Trust Propensity Model. What features do we have?",
        "Which features have data quality issues?",
        "What signals are missing for a wealth transfer model?",
    ],
    chatbot=gr.Chatbot(height=450),
)

port = int(os.environ.get("DATABRICKS_APP_PORT", 8080))
demo.launch(server_name="0.0.0.0", server_port=port)
"""

path = "/Workspace/Users/swaroop.udgaonkar@wipro.com/feature-discovery-agent-app/app.py"
with open(path, "w") as f:
    f.write(app_code)

# Verify input is correct
with open(path) as f:
    content = f.read()

assert '"input"' in content, "WRONG - still has messages"
assert '"messages"' not in content, "WRONG - still has messages"
print("✅ File verified - input field correct")
print("Now deploy the app")
