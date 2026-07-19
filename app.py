# app.py
import gradio as gr
import requests
from agent import agent_instance
from llm_manager import enhance_response

API_URL = "http://127.0.0.1:8000/api/v1"

# -------------------------------------------------------------------
# CORE PIPELINE EXECUTION (API DRIVEN)
# -------------------------------------------------------------------
def run_agent(user_input):
    if not user_input.strip():
        return None, "⚠️ Please enter a query."

    try:
        # Send query payload to FastAPI endpoint so it saves to PostgreSQL
        response = requests.post(f"{API_URL}/analyze", json={"user_query": user_input})
        if response.status_code != 200:
            return None, f"❌ Engine error: {response.text}"

        data = response.json()
        symbol = data["symbol"]
        analysis_text = data["analysis"]

        # Regenerate visual plot locally for UI presentation
        df, _ = agent_instance.fetch_stock_data(symbol)
        df, _ = agent_instance.add_indicators(df)
        chart = agent_instance.generate_chart(df, symbol)

        return chart, analysis_text
    except Exception as e:
        return None, f"❌ Interface connection fault: {str(e)}"


# -------------------------------------------------------------------
# SIDEBAR / HEADER EVENT HANDLERS
# -------------------------------------------------------------------
def clear_chat_session():
    return None, "", "🔄 New chat session initialized. Ready for analysis."


def handle_auth(action_type):
    return f"🔒 {action_type} dynamic modal simulated. Backend auth logic integrates here."


def run_with_model(user_input, model_choice):
    if not user_input.strip():
        return "⚠️ Please enter a query."

    try:
        from llm_manager import call_model_with_keys
        response = call_model_with_keys(user_input, model_choice)
        return f"🤖 Model: {model_choice.upper()}\n\n{response}"
    except Exception as e:
        return f"❌ ERROR: {str(e)}"


def extract_symbol(user_input):
    query = user_input.lower()
    mapping = {
        "tesla": "TSLA",
        "apple": "AAPL",
        "amazon": "AMZN",
        "google": "GOOGL",
        "microsoft": "MSFT",
        "nvidia": "NVDA",
        "meta": "META"
    }

    for key in mapping:
        if key in query:
            return mapping[key]

    return query.upper().strip()


# -------------------------------------------------------------------
# HIGH-END SaaS STYLING (CSS) WITH SPINNING CORE REFINEMENTS
# -------------------------------------------------------------------
custom_css = """
body { 
    background-color: #0b0f19; 
}
.gradio-container { 
    background: #0b0f19; 
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
}
.header-container {
    background: #111827;
    border-bottom: 1px solid #1f2937;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 8px;
    margin-bottom: 15px;
}
.sidebar-panel {
    background-color: #111827 !important;
    border-right: 1px solid #1f2937 !important;
    padding: 20px 10px !important;
}
.action-btn {
    background: #1f2937 !important;
    color: #e5e7eb !important;
    border: 1px solid #374151 !important;
    transition: background 0.2s ease;
}
.action-btn:hover {
    background: #374151 !important;
}
.primary-action-btn {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-weight: 600 !important;
}
.primary-action-btn:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
}
textarea, input { 
    background-color: #1f2937 !important; 
    color: #ffffff !important; 
    border: 1px solid #374151 !important;
}
"""

# -------------------------------------------------------------------
# APP WORKSPACE INTERFACE LAYOUT
# -------------------------------------------------------------------
with gr.Blocks(css=custom_css, title="📊 Terminal Platform") as app:
    # 1. TOP NAVIGATION HEADER PANEL
    with gr.Row(elem_classes=["header-container"]):
        with gr.Column(scale=8):
            gr.HTML("""
                <div style='display: flex; align-items: center; gap: 12px;'>
                    <span style='font-size: 24px;'>📊</span>
                    <div>
                        <h1 style='margin: 0; font-size: 18px; font-weight: 700; color: #ffffff;'>QUANTUMEDGE</h1>
                        <p style='margin: 0; font-size: 11px; color: #9ca3af;'>Enterprise Financial Intelligence Engine</p>
                    </div>
                </div>
            """)
        with gr.Column(scale=4):
            with gr.Row():
                login_btn = gr.Button("Sign In", elem_classes=["action-btn"], size="sm")
                logout_btn = gr.Button("Log Out", elem_classes=["action-btn"], size="sm")

    # 2. APPLICATION LAYOUT SETUP (SIDEBAR + MAIN CANVAS)
    with gr.Row():
        # LEFT DRAWER CONTROL SIDEBAR
        with gr.Column(scale=3, elem_classes=["sidebar-panel"]):
            gr.Markdown("### ⚡ Workspace Navigation")
            new_chat_btn = gr.Button("➕ New Analysis", elem_classes=["primary-action-btn"])

            gr.HTML("<hr style='border-color: #1f2937; margin: 15px 0;'>")

            gr.Markdown("### 📜 Session History")
            prev_chat_1 = gr.Button("📁 Historical Run: TSLA", elem_classes=["action-btn"], size="sm")
            prev_chat_2 = gr.Button("📁 Historical Run: NVDA", elem_classes=["action-btn"], size="sm")
            prev_chat_3 = gr.Button("📁 Historical Run: AAPL", elem_classes=["action-btn"], size="sm")

            gr.HTML("<hr style='border-color: #1f2937; margin: 15px 0;'>")
            system_status = gr.HTML("""
                <div style='padding: 8px; background: #1f2937; border-radius: 6px; font-size: 11px; color: #10b981;'>
                    ● Engine Nodes Operational
                </div>
            """)

        # RIGHT MAIN ANALYTICS VIEWPORT AREA
        with gr.Column(scale=9):
            with gr.Tab("🤖 Smart Agent Execution"):
                user_input = gr.Textbox(
                    label="Market Query Prompt",
                    placeholder="e.g. Is Nvidia showing bullish technical trends over the current horizon?"
                )
                run_btn = gr.Button("🚀 Execute Real-Time Analysis", elem_classes=["primary-action-btn"])

                chart_output = gr.Plot(label="📈 Dynamic Interactive Market Technicals")
                text_output = gr.Textbox(label="Agent Intelligence Synopsis Summary", lines=12)

                # Wiring Pipeline Click Trigger Events
                run_btn.click(
                    fn=run_agent,
                    inputs=user_input,
                    outputs=[chart_output, text_output]
                )

            with gr.Tab("⚙️ Low-Level Model Selection Override"):
                user_input2 = gr.Textbox(label="Direct Pipeline Prompt Entry")
                model_dropdown = gr.Dropdown(
                    ["qwen", "kimi", "openai"],
                    label="Target Core Network Node Provider",
                    value="qwen"
                )
                output2 = gr.Textbox(label="Model Context Engine Response Payload", lines=10)
                btn2 = gr.Button("⚡ Query Direct Node", elem_classes=["action-btn"])

                btn2.click(
                    fn=run_with_model,
                    inputs=[user_input2, model_dropdown],
                    outputs=output2
                )

    # -------------------------------------------------------------------
    # CONTROL INTERFACE EVENT WIRES
    # -------------------------------------------------------------------
    new_chat_btn.click(
        fn=clear_chat_session,
        inputs=None,
        outputs=[chart_output, user_input, text_output]
    )

    login_btn.click(fn=handle_auth, inputs=gr.State("Login"), outputs=text_output)
    logout_btn.click(fn=handle_auth, inputs=gr.State("Logout"), outputs=text_output)

    prev_chat_1.click(fn=lambda: "Analyze Tesla stock positions", inputs=None, outputs=user_input)
    prev_chat_2.click(fn=lambda: "Analyze Nvidia stock targets", inputs=None, outputs=user_input)
    prev_chat_3.click(fn=lambda: "Analyze Apple stock charts", inputs=None, outputs=user_input)

if __name__ == "__main__":
    app.launch()