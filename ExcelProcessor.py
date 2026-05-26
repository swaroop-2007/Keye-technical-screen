%%writefile /Workspace/Users/swaroop.udgaonkar@wipro.com/feature-agent-app/app.py

import os
import gradio as gr
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
# Databricks Apps auto-injects these — no hardcoding needed
WORKSPACE_URL   = os.environ.get("DATABRICKS_HOST", "")
TOKEN           = os.environ.get("DATABRICKS_TOKEN", "")
ENDPOINT_NAME   = "feature-discovery-supervisor"   # ← your supervisor endpoint name

# ── Client pointing to your Supervisor endpoint ───────────────────────────────
client = OpenAI(
    api_key=TOKEN,
    base_url=f"{WORKSPACE_URL}/serving-endpoints"
)

# ── Chat function ─────────────────────────────────────────────────────────────
def chat(message, history):
    try:
        response = w.serving_endpoints.query(
            name=ENDPOINT_NAME,
            messages=[{"role": "user", "content": message}]
        )

        # Response is a dict — parse it directly
        if isinstance(response, dict):
            return response["choices"][0]["message"]["content"]
        else:
            # Fallback for object-style response
            return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error: {str(e)}\n\nRaw: {str(response)}"

# ── UI ────────────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="Feature Discovery Agent",
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("IBM Plex Mono"),
    ),
    css="""
        .gradio-container { max-width: 960px !important; margin: auto; }
        footer { display: none !important; }
        #header-band {
            background: #0B1A35;
            border-bottom: 3px solid #00C2E0;
            padding: 16px 24px;
            margin-bottom: 16px;
            border-radius: 8px;
        }
        #tag {
            display: inline-block;
            background: #00C2E0;
            color: #060E1F;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 2px;
            padding: 3px 10px;
            border-radius: 3px;
            margin-bottom: 8px;
        }
    """
) as demo:

    # ── Header ──
    gr.HTML("""
        <div id="header-band">
            <div id="tag">EDWARD JONES · DATA ENGINEERING · DATABRICKS AGENT BRICKS</div>
            <h2 style="color:#FFFFFF; margin:0; font-size:22px;">
                🔍 Feature Discovery Agent
            </h2>
            <p style="color:#94A3B8; margin:4px 0 0 0; font-size:13px;">
                Describe your ML objective in plain English — powered by Supervisor Agent, 
                Knowledge Assistant, Genie Space & Vector Search
            </p>
        </div>
    """)

    with gr.Row():

        # ── Main chat ──
        with gr.Column(scale=3):
            chatbot = gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=480,
                    show_label=False,
                    placeholder="Ask me what features are available for your ML model...",
                    render_markdown=True,
                ),
                textbox=gr.Textbox(
                    placeholder="e.g. What features do we have for a trust propensity model?",
                    container=False,
                    lines=2
                ),
                examples=[
                    "I'm building a Trust Propensity Model for wealth transfer prediction. What features do we have?",
                    "Which features have data quality issues or missed their freshness SLA?",
                    "What signals would you expect for a trust propensity model that we don't currently have?",
                    "Find all advisor engagement and relationship features in the feature store",
                    "What features did the long-term care model use previously?",
                ],
                retry_btn=None,
                undo_btn=None,
                clear_btn="🗑️  Clear chat",
            )

        # ── Sidebar ──
        with gr.Column(scale=1, min_width=220):
            gr.Markdown("### 🤖 Agent Squad")
            gr.Markdown("""
**Supervisor**
Routes your question to the right agent

**Knowledge Assistant**
Feature definitions & lineage

**Genie Space**
Freshness, null rates & DQ metrics

**UC Function**
Semantic similarity ranking
            """)

            gr.Markdown("---")
            gr.Markdown("### 💡 Try asking")
            gr.Markdown("""
- *What features exist for wealth modeling?*
- *Which features are stale today?*
- *What signals are missing for my model?*
- *Where does client_net_worth_band come from?*
            """)

            gr.Markdown("---")
            gr.Markdown("### 📦 Feature Store")
            gr.Markdown("""
`uc_wealthai_dev`
- `ml_feature_store`
- `ml_client_exploitation`
- `advisors`
- `portfolios`
- `accounts`
            """)

demo.launch(server_name="0.0.0.0", server_port=8080)
