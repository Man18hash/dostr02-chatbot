import logging
import time
import threading
import gradio as gr

from src.router import hybrid_answer
from src.model_cache import get_vectorstore, get_reranker, get_llm
from src.official_store import load_official
from config import OFFICIAL_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dost-hybrid")

# ---------------------------
# Theme + CSS (pass to launch in Gradio 6.x)
# ---------------------------
APP_THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate",
)

APP_CSS = """
body { background-color: #f4f4f5; }

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

/* Hide footer */
footer,
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
  margin-top: 1.25rem;
}

/* mini quick cards below chat */
.mini-cards-row{
  width: 100%;
  gap: 10px;
  margin-top: 6px;
}
.mini-card{
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(15,23,42,0.06);
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
  user-select: none;
}
.mini-card:hover{
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(15,23,42,0.10);
  border-color: #3b82f6;
}
.mini-card-text{
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 !important;
  line-height: 1.1;
  white-space: nowrap;
}

/* Optional: visually indicate disabled textbox */
textarea[disabled], input[disabled] {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
}

/* Logo row styling */
.logo-row {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 30px;
  padding: 20px 10px;
  border-top: 1px solid #e5e7eb;
  max-width: 960px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.dost-logo-container {
  height: 60px;
  width: auto;
  min-width: 100px;
  max-width: 160px;
  object-fit: contain;
  filter: grayscale(20%);
  transition: filter 0.3s ease, transform 0.3s ease;
  border-radius: 4px;
  background: transparent;
  padding: 0;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  -webkit-touch-callout: none;
  flex-shrink: 0;
  flex-grow: 0;
  flex-basis: auto;
}

.dost-logo-container:hover {
  filter: grayscale(0%);
  transform: scale(1.05);
}

/* Hide Gradio controls */
.dost-logo-container .download-btn,
.dost-logo-container .screenshot-btn,
.dost-logo-container .zoom-btn {
  display: none !important;
}

/* Responsive design for all devices */
@media (max-width: 768px) {
  .logo-row {
    gap: 12px;
    padding: 15px 8px;
  }
  
  .dost-logo-container {
    height: 50px;
    min-width: 80px;
    max-width: 120px;
  }
}

@media (max-width: 480px) {
  .logo-row {
    gap: 8px;
    padding: 12px 5px;
  }
  
  .dost-logo-container {
    height: 45px;
    min-width: 70px;
    max-width: 100px;
  }
}

@media (max-width: 390px) {
  .logo-row {
    gap: 6px;
    padding: 10px 3px;
    justify-content: center;
  }
  
  .dost-logo-container {
    height: 40px;
    min-width: 60px;
    max-width: 85px;
  }
}

@media (max-width: 320px) {
  .logo-row {
    gap: 4px;
    padding: 8px 2px;
  }
  
  .dost-logo-container {
    height: 35px;
    min-width: 50px;
    max-width: 70px;
  }
}

/* Landscape orientation */
@media (max-height: 500px) and (orientation: landscape) {
  .logo-row {
    gap: 10px;
    padding: 8px 5px;
  }
  
  .dost-logo-container {
    height: 35px;
    min-width: 80px;
    max-width: 120px;
  }
}
"""

# ---------------------------
# Helpers: always enforce messages format
# ---------------------------
def ensure_messages(history):
    if history is None:
        return []
    if not isinstance(history, list):
        return []

    cleaned = []
    for item in history:
        if isinstance(item, dict) and "role" in item and "content" in item:
            cleaned.append({"role": str(item["role"]), "content": item["content"]})
            continue

        # Convert (user, bot) tuples if they ever sneak in
        if isinstance(item, (tuple, list)) and len(item) == 2:
            u, a = item
            if u is not None:
                cleaned.append({"role": "user", "content": str(u)})
            if a is not None:
                cleaned.append({"role": "assistant", "content": str(a)})
            continue

    return cleaned


# ---------------------------
# Chat logic:
# - beating dot (pulse frames)
# - disable input while thinking
# ---------------------------
def chat_response(query, history):
    history = ensure_messages(history)

    if not query or not query.strip():
        # keep as-is
        yield history, history, query, gr.update(interactive=True), gr.update(interactive=True)
        return

    user_text = query.strip()

    # Disable textbox + Ask button immediately
    yield history, history, "", gr.update(interactive=False), gr.update(interactive=False)

    # Append user
    history.append({"role": "user", "content": user_text})

    # Append assistant placeholder
    history.append({"role": "assistant", "content": "●"})
    yield history, history, "", gr.update(interactive=False), gr.update(interactive=False)

    # Background compute
    result = {"done": False, "answer": None, "error": None}

    def worker():
        try:
            result["answer"] = hybrid_answer(user_text)
        except Exception as e:
            logger.exception(e)
            result["error"] = e
        finally:
            result["done"] = True

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # Beating dot frames (pulse 느낌)
    # You can tweak these for a different "beat"
    frames = ["·", "●", "●●", "●●●", "●●", "●"]
    i = 0

    while not result["done"]:
        history[-1] = {"role": "assistant", "content": frames[i % len(frames)]}
        i += 1
        yield history, history, "", gr.update(interactive=False), gr.update(interactive=False)
        time.sleep(0.18)

    answer = "Sorry, an error occurred." if result["error"] else (result["answer"] or "Sorry, I couldn't generate an answer.")
    history[-1] = {"role": "assistant", "content": answer}

    # Re-enable textbox + Ask button after answering
    yield history, history, "", gr.update(interactive=True), gr.update(interactive=True)


def on_card_click(card_id):
    questions = {
        "tech-card": "Tell me about DOST's latest technologies and innovations.",
        "programs-card": "What are the current DOST programs and projects?",
        "services-card": "What services does DOST Region II offer?",
    }
    return questions.get(card_id, "")


def clear_all():
    # chat, state, textbox, textbox interactive, ask interactive
    return [], [], "", gr.update(interactive=True), gr.update(interactive=True)


# ---------------------------
# UI
# ---------------------------
with gr.Blocks(title="DOST Hybrid Chatbot") as gui:
    with gr.Column(elem_classes=["dost-page"]):
        gr.Image(
            value="img/dost.png",
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
            chatbot = gr.Chatbot(
                label=None,
                height=420,
                elem_classes=["dost-chatbot"],
            )

            with gr.Row(elem_classes=["dost-input-row"]):
                q = gr.Textbox(
                    placeholder="Ask anything about DOST Region II…",
                    lines=1,
                    show_label=False,
                    scale=8,
                )
                ask = gr.Button("Ask", variant="primary", scale=1)
                clear = gr.Button("Clear", variant="secondary", scale=1)

            with gr.Row(elem_classes=["mini-cards-row"]):
                with gr.Column(scale=1, min_width=150, elem_classes=["mini-card"], elem_id="tech-card"):
                    gr.Markdown("🔍 Technologies", elem_classes="mini-card-text")
                with gr.Column(scale=1, min_width=150, elem_classes=["mini-card"], elem_id="programs-card"):
                    gr.Markdown("📋 Programs", elem_classes="mini-card-text")
                with gr.Column(scale=1, min_width=150, elem_classes=["mini-card"], elem_id="services-card"):
                    gr.Markdown("🏢 Services", elem_classes="mini-card-text")

            gr.Markdown(
                """
                <div class="dost-footer">
                    This assistant uses an internal DOST Region II knowledge base and public documents.
                    For the most up-to-date official information, please contact DOST Region II directly.
                </div>
                """
            )

    state = gr.State([])

    # Ask + Enter:
    # Outputs: chatbot, state, textbox(value), textbox(interactive), ask(interactive)
    ask.click(
        chat_response,
        inputs=[q, state],
        outputs=[chatbot, state, q, q, ask],
    )
    q.submit(
        chat_response,
        inputs=[q, state],
        outputs=[chatbot, state, q, q, ask],
    )

    # Clear:
    clear.click(clear_all, outputs=[chatbot, state, q, q, ask])

    # Hidden buttons for card -> fill textbox
    tech_btn = gr.Button("Tech Button", visible=False, elem_id="tech-btn")
    programs_btn = gr.Button("Programs Button", visible=False, elem_id="programs-btn")
    services_btn = gr.Button("Services Button", visible=False, elem_id="services-btn")

    tech_btn.click(lambda: on_card_click("tech-card"), outputs=[q])
    programs_btn.click(lambda: on_card_click("programs-card"), outputs=[q])
    services_btn.click(lambda: on_card_click("services-card"), outputs=[q])

    gr.HTML(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const techCard = document.getElementById('tech-card');
            if (techCard) techCard.onclick = () => document.getElementById('tech-btn')?.click();

            const programsCard = document.getElementById('programs-card');
            if (programsCard) programsCard.onclick = () => document.getElementById('programs-btn')?.click();

            const servicesCard = document.getElementById('services-card');
            if (servicesCard) servicesCard.onclick = () => document.getElementById('services-btn')?.click();
        });
        </script>
        """
    )
    
    # Add logos at the bottom
    with gr.Row(elem_classes=["logo-row"]):
        gr.Image(
            value="img/dost.png",
            show_label=False,
            container=False,
            height=80,
            width=None,
            elem_classes=["dost-logo-container"],
        )
        gr.Image(
            value="img/one-cagayan.png",
            show_label=False,
            container=False,
            height=80,
            width=None,
            elem_classes=["dost-logo-container"],
        )
        gr.Image(
            value="img/bagong-pilipinas.png",
            show_label=False,
            container=False,
            height=80,
            width=None,
            elem_classes=["dost-logo-container"],
        )
        gr.Image(
            value="img/ihub.png",
            show_label=False,
            container=False,
            height=80,
            width=None,
            elem_classes=["dost-logo-container"],
        )


if __name__ == "__main__":
    print("Loading models (may take a while on first run)...")
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

    gui.queue()

    gui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=APP_THEME,
        css=APP_CSS,
    )
