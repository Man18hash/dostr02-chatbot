import logging
import gradio as gr
from src.router import hybrid_answer
from src.model_cache import get_vectorstore, get_reranker, get_llm
from src.official_store import load_official
from config import OFFICIAL_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dost-hybrid")

def chat_response(query, history):
    """
    Gradio 6 `Chatbot` now uses a messages format:
    a list of dicts with `role` and `content`.
    We keep `history` as that list and append the
    latest user and assistant messages.
    """
    if history is None:
        history = []

    if not query or not query.strip():
        return history, history, query  # Keep the text if empty

    user_text = query.strip()

    try:
        answer = hybrid_answer(user_text)
    except Exception as e:
        logger.exception(e)
        answer = "Sorry, an error occurred."

    history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": answer},
    ]

    # Return history, history, and empty string to clear the input textbox
    return history, history, ""


def show_loader():
    """Show the full-screen loading overlay."""
    return gr.update(visible=True)


def hide_loader():
    """Hide the full-screen loading overlay."""
    return gr.update(visible=False)

APP_THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate",
)

APP_CSS = """
    body {
        background-color: #f4f4f5;
    }

    .dost-page {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 4rem;
    }

    .dost-logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .dost-logo-container img {
        max-width: 80px;
        width: auto;
        height: auto;
        object-fit: contain;
    }

    /* Hide Gradio footer elements */
    footer {
        display: none !important;
    }

    .gradio-container footer,
    .gradio-container .footer {
        display: none !important;
    }

    .dost-header-title {
        font-size: 2.1rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1.25rem;
    }

    .dost-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }

    .dost-main-card {
        width: 100%;
        max-width: 960px;
        background: white;
        border-radius: 1.5rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
        padding: 1.5rem 1.75rem 1.2rem 1.75rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .dost-chatbot {
        border-radius: 1rem;
        background: #f9fafb;
    }

    .dost-input-row {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        margin-top: 0.25rem;
    }

    .dost-footer {
        font-size: 0.75rem;
        color: #9ca3af;
        text-align: center;
        margin-top: 1.5rem;
    }

    .dost-loading-overlay {
        position: fixed;
        inset: 0;
        background: rgba(15, 23, 42, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .dost-loading-card {
        background: #020617;
        color: #e5e7eb;
        padding: 1.25rem 1.75rem;
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.9rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.6);
        font-size: 0.95rem;
    }

    .dost-spinner {
        width: 1.4rem;
        height: 1.4rem;
        border-radius: 9999px;
        border: 3px solid rgba(148, 163, 184, 0.45);
        border-top-color: #38bdf8;
        animation: dost-spin 0.9s linear infinite;
    }

    @keyframes dost-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    """

with gr.Blocks(title="DOST Hybrid Chatbot") as gui:
    with gr.Column(elem_classes=["dost-page"]):
        # DOST Logo - small size
        gr.Image(
            value="img/dost_logo150.png",
            show_label=False,
            container=False,
            height=80,
            width=None,
            elem_classes=["dost-logo-container"],
        )
        
        gr.Markdown(
            """
            <div class="dost-header-title">What can I help with?</div>
            <div class="dost-subtitle">
                Ask about DOST Region II services, programs, requirements, procedures, and more.
            </div>
            """
        )

        with gr.Column(elem_classes=["dost-main-card"]):
            # Chat area
            chatbot = gr.Chatbot(
                label=None,
                height=420,
                elem_classes=["dost-chatbot"],
            )

            # Input row similar to ChatGPT prompt bar
            with gr.Row(elem_classes=["dost-input-row"]):
                q = gr.Textbox(
                    placeholder="Ask anything about DOST Region II…",
                    lines=1,
                    show_label=False,
                    scale=8,
                )
                ask = gr.Button("Ask", variant="primary", scale=1)
                clear = gr.Button("Clear", variant="secondary", scale=1)

            gr.Markdown(
                """
                <div class="dost-footer">
                    This assistant uses an internal DOST Region II knowledge base and public documents.
                    For the most up-to-date official information, please contact DOST Region II directly.
                </div>
                """
            )

    state = gr.State([])

    # Full-screen loading overlay
    loader = gr.HTML(
        """
        <div class="dost-loading-overlay">
            <div class="dost-loading-card">
                <div class="dost-spinner"></div>
                <div><strong>Thinking…</strong><br/><span style="font-size: 0.85rem;">Generating the best answer for you.</span></div>
            </div>
        </div>
        """,
        visible=False,
    )

    # Wire interactions: show loader -> answer -> hide loader
    ask.click(show_loader, outputs=loader).then(
        chat_response, inputs=[q, state], outputs=[chatbot, state, q]
    ).then(hide_loader, outputs=loader)

    q.submit(show_loader, outputs=loader).then(
        chat_response, inputs=[q, state], outputs=[chatbot, state, q]
    ).then(hide_loader, outputs=loader)

    clear.click(lambda: ([], []), outputs=[chatbot, state])

if __name__ == "__main__":
    # Preload all models at startup for faster first response
    print("Loading models (this may take 10-15 seconds on first run)...")
    try:
        get_vectorstore()
        print("✓ Vectorstore loaded")
        get_reranker()
        print("✓ Reranker loaded")
        get_llm()
        print("✓ LLM loaded")
        load_official(OFFICIAL_DIR)
        print("✓ Official database loaded")
        print("All models ready! Starting server...")
    except Exception as e:
        print(f"Warning: Error preloading models: {e}")
        print("Models will load on first request (slower first response)")
    
    # Listen on all network interfaces (0.0.0.0) so phone can access via WiFi
    gui.launch(
        server_name="0.0.0.0",  # Allows access from other devices on same network
        server_port=7860,       # Fixed port for easier access
        share=False,
        theme=APP_THEME,
        css=APP_CSS,
    )
