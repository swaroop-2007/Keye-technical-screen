%%writefile /Workspace/Users/swaroop.udgaonkar@wipro.com/feature-agent-app/app.py

import gradio as gr
import mlflow
import os
from langchain_core.messages import HumanMessage, AIMessage

# ── Load the registered agent from UC ────────────────────────────────────────
# Databricks Apps injects DATABRICKS_HOST and DATABRICKS_TOKEN automatically
mlflow.set_registry_uri("databricks-uc")

print("Loading agent from Unity Catalog...")
agent = mlflow.pyfunc.load_model(
    "models:/uc_wealthai_dev.feature_agent.feature_discovery_agent/3"
)
print("Agent loaded ✅")

# ── Chat function ─────────────────────────────────────────────────────────────
def chat(message, history):
    """
    Gradio passes history as list of [user, assistant] pairs.
    We forward the latest message to the agent and return its response.
    """
    try:
        response = agent.predict({
            "messages": [{"role": "user", "content": message}]
        })
        return response
    except Exception as e:
        return f"⚠️ Agent error: {str(e)}\n\nTry rephrasing your ML objective."

# ── UI ────────────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="Feature Discovery Agent",
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("IBM Plex Mono"),
    ),
    css="""
        .gradio-container { max-width: 900px !important; margin: auto; }
        .chat-message { font-size: 14px; }
        footer { display: none !important; }
        #header { 
            border-bottom: 1px solid #1e293b; 
            padding-bottom: 16px; 
            margin-bottom: 8px; 
        }
        #tag { 
            display: inline-block;
            background: #0ea5e9;
            color: white;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 3px 10px;
            border-radius: 3px;
            margin-bottom: 10px;
        }
    """
) as demo:

    with gr.Row(elem_id="header"):
        with gr.Column():
            gr.HTML('<div id="tag">EDWARD JONES · DATA ENGINEERING</div>')
            gr.Markdown("# 🔍 Feature Discovery Agent")
            gr.Markdown(
                "Describe your ML objective in plain English. "
                "I'll search the **Unity Catalog feature store** and return "
                "ranked features with source tables and relevance scores."
            )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=460,
                    show_label=False,
                    placeholder="Ask me what features are available for your model...",
                    elem_classes=["chat-message"]
                ),
                textbox=gr.Textbox(
                    placeholder="e.g. What features do we have for a trust propensity model?",
                    container=False,
                    scale=7,
                    lines=2
                ),
                examples=[
                    "What features do we have for predicting wealth transfer to a trust?",
                    "I need features for a client churn model",
                    "Find all advisor engagement features available in the feature store",
                    "What portfolio and AUM features are available for a risk scoring model?",
                    "Show me behavioral features updated in the last 30 days",
                ],
                retry_btn=None,
                undo_btn=None,
                clear_btn="🗑️  Clear",
            )

        with gr.Column(scale=1, min_width=200):
            gr.Markdown("### How to use")
            gr.Markdown("""
**1.** Type your ML objective in the box below

**2.** Agent searches the real feature store

**3.** Get back ranked features with:
- Column name
- Source table path  
- Relevance score
- Signal gaps

---
**Tips:**
- Be specific about the prediction target
- Mention the entity (client, advisor, account)
- Include time horizon if relevant
            """)

            gr.Markdown("---")
            gr.Markdown("### Feature Store")
            gr.Markdown("""
`uc_wealthai_dev`
- `ml_feature_store`
- `ml_client_exploitation`
- `advisors`
- `portfolios`
- `accounts`
            """)

demo.launch(server_name="0.0.0.0", server_port=8080)
