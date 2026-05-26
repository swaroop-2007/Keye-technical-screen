import os
import logging
import gradio as gr
from databricks.sdk import WorkspaceClient

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Init ──────────────────────────────────────────────────────────────────────
log.info("Starting Feature Discovery Agent app...")
w = WorkspaceClient()
log.info("WorkspaceClient initialized successfully")

ENDPOINT_NAME = "feature-discovery-supervisor"

def chat(message, history):
    log.info(f"Query received: {message}")
    try:
        response = w.serving_endpoints.query(
            name=ENDPOINT_NAME,
            input=[{"role": "user", "content": message}]
        )
        log.info(f"Response type: {type(response)}")

        # Response is a QueryEndpointResponse SDK object
        # Supervisor Agent returns result in data field
        if hasattr(response, 'data') and response.data:
            log.info("Parsing via data field")
            return str(response.data[0])

        elif hasattr(response, 'predictions') and response.predictions:
            log.info("Parsing via predictions field")
            return str(response.predictions[0])

        elif hasattr(response, 'choices') and response.choices:
            log.info("Parsing via choices field")
            return response.choices[0].message.content

        else:
            # Log full object to see all fields
            log.warning(f"All fields empty. Full response: {vars(response)}")
            return f"Response received but empty. Check logs for full response."

    except Exception as e:
        log.error(f"Error: {str(e)}")
        return f"⚠️ Error: {str(e)}"

# ── UI ────────────────────────────────────────────────────────────────────────
demo = gr.ChatInterface(
    fn=chat,
    title="🔍 Feature Discovery Agent",
    description="**Edward Jones · Data Engineering · Databricks Agent Bricks**\n\nDescribe your ML objective — I'll find relevant features from the feature store.",
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
demo.launch(server_name="0.0.0.0", server_port=port)        neutral_hue="slate",
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
