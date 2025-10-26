# app.py
import os, json, pandas as pd, streamlit as st
from dotenv import load_dotenv

# NEW SDK
from google import genai
from google.genai.types import Content, Part, GenerateContentConfig

from heuristics import NIELSEN_HEURISTICS
from agents import (
    CLARIFIER_AGENT, SCORER_AGENT, ETHICS_AGENT,
    clarifier_user_payload, scorer_user_payload, ethics_user_payload,
)

# setup 
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash" 

st.set_page_config(page_title="ExplainUX – Heuristic Helper", page_icon="🧠")
st.title("🧠 ExplainUX – Heuristic Helper")
st.caption("Powered by Gemini 2.5 for adaptive, transparent UX evaluation.")

# state init 
if "has_run" not in st.session_state:
    st.session_state.has_run = False

st.session_state.setdefault("context_summary", None)
st.session_state.setdefault("chosen", None)
st.session_state.setdefault("clarifier", {})
st.session_state.setdefault("fu_answers", {})
st.session_state.setdefault("rerun_requested", False)
st.session_state.setdefault("last_rows", [])
st.session_state.setdefault("recompute", False) 

# ---------- helpers ----------
def _chat_json(system_prompt: str, user_payload):
    # Ensure string payload
    if not isinstance(user_payload, str):
        user_payload = json.dumps(user_payload, ensure_ascii=False)

    # Include an explicit instruction to return JSON only
    prompt = (
        f"{system_prompt}\n\nUser Input:\n{user_payload}\n\n"
        "Return ONLY valid JSON. Do not add explanations or code fences."
    )

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[Content(role="user", parts=[Part.from_text(text=prompt)])],
            config=GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        text = (resp.text or "").strip()

        # Be resilient to accidental code fences
        if text.startswith("```"):
            # remove ```json ... ``` or ``` ...
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline + 1:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)

    except json.JSONDecodeError as e:
        st.error(f"Model returned non-JSON: {e}\nRaw text: {text[:500]}")
        return {}
    except Exception as e:
        st.error(f"Model call failed: {e}")
        raise

def render_results_table_or_cards(df: pd.DataFrame):
    # If segmented_control isn't available in your Streamlit, swap to st.radio (see fallback below)
    try:
        view_mode = st.segmented_control(
            "View as",
            options=["Cards", "Table"],
            default="Cards",
            help="Cards are easier for long text; Table is good for scanning."
        )
    except Exception:
        view_mode = st.radio(
            "View as",
            options=["Cards", "Table"],
            index=0,
            help="Cards are easier for long text; Table is good for scanning."
        )

    if view_mode == "Table":
        st.data_editor(
            df,
            use_container_width=True,
            height=800,
            disabled=True,
            column_config={
                "Heuristic": st.column_config.TextColumn(width="medium"),
                "Score (0–10)": st.column_config.NumberColumn(width="small"),
                "Why": st.column_config.TextColumn(width="large"),
                "Improvements": st.column_config.TextColumn(width="large"),
                "Ethical Reflection": st.column_config.TextColumn(width="large"),
                "Confidence": st.column_config.NumberColumn(width="small"),
                "Mitigation": st.column_config.TextColumn(width="large"),
            },
        )
    else:
        st.markdown("### 📊 Evaluation Results")
        for i, row in df.iterrows():
            with st.expander(f"{i+1}. {row['Heuristic']} — Score: {row['Score (0–10)']}"):
                st.markdown(f"**Why**\n\n{row.get('Why') or '—'}")
                st.markdown(f"**Improvements**\n\n{row.get('Improvements') or '—'}")
                st.markdown(f"**Ethical Reflection**\n\n{row.get('Ethical Reflection') or '—'}")
                if row.get("Confidence"):
                    st.markdown(f"**Confidence**\n\n{row['Confidence']}")
                st.markdown(f"**Mitigation**\n\n{row.get('Mitigation') or '—'}")

    st.session_state.setdefault("download_key_counter", 0)
    st.session_state.download_key_counter += 1
    st.download_button(
        "⬇️ Download Report as CSV",
        df.to_csv(index=False).encode("utf-8"),
        "ExplainUX_Report.csv",
        "text/csv",
        key=f"download_csv_{st.session_state.download_key_counter}",
    )

def run_pipeline(context_summary, chosen):
    """Runs Scorer + Ethics and returns list[dict] rows WITHOUT calling Clarifier."""
    scorer_payload = scorer_user_payload(context_summary, chosen)
    scored = _chat_json(SCORER_AGENT, scorer_payload)
    if isinstance(scored, dict): scored = [scored]
    if not isinstance(scored, list): scored = []

    ethics_payload = ethics_user_payload(context_summary, scored)
    ethics = _chat_json(ETHICS_AGENT, ethics_payload)
    if isinstance(ethics, dict): ethics = [ethics]
    if not isinstance(ethics, list): ethics = []

    rows = []
    for i, s in enumerate(scored):
        e = ethics[i] if i < len(ethics) else {}
        rows.append({
            "Heuristic": s.get("heuristic"),
            "Score (0–10)": s.get("score"),
            "Why": s.get("why"),
            "Improvements": "; ".join(s.get("improvements", [])) if isinstance(s.get("improvements"), list) else s.get("improvements"),
            "Ethical Reflection": e.get("ethical_reflection"),
            "Confidence": e.get("confidence"),
            "Mitigation": e.get("mitigation"),
        })
    return rows

# ---------- main logic ----------
interface_summary = st.text_area(
    "Describe the interface you're evaluating:",
    placeholder="e.g., A student dashboard showing assignments with colour-coded deadlines."
)
selected_labels = st.multiselect(
    "Choose which heuristics to evaluate:",
    [f"{h['id']}. {h['name']}" for h in NIELSEN_HEURISTICS],
    default=[f"1. {NIELSEN_HEURISTICS[0]['name']}"]
)
run = st.button("Run Evaluation")

if run:
    if not interface_summary:
        st.warning("Please describe your interface first.")
    else:
        with st.spinner("Running Clarifier → Scorer → Ethics..."):
            # 1) Clarifier (only on explicit Run)
            clarifier_payload = clarifier_user_payload(interface_summary)
            clarifier = _chat_json(CLARIFIER_AGENT, clarifier_payload) or {}
            context_summary = clarifier.get("context_summary", interface_summary)

            # 2) Choose heuristics
            selected_ids = []
            for s in selected_labels:
                try:
                    selected_ids.append(int(s.split(".")[0].strip()))
                except Exception:
                    pass
            chosen = [h for h in NIELSEN_HEURISTICS if int(h["id"]) in selected_ids] or NIELSEN_HEURISTICS[:1]

            # 3) Scorer + Ethics (via helper)
            rows = run_pipeline(context_summary, chosen)

            # 4) Persist essentials for follow-ups and rendering
            st.session_state.has_run = True
            st.session_state.context_summary = context_summary
            st.session_state.chosen = chosen
            st.session_state.clarifier = clarifier
            st.session_state.last_rows = rows

if st.session_state.has_run:
    clarifier = st.session_state.clarifier or {}
    if isinstance(clarifier.get("follow_up_questions"), list) and clarifier["follow_up_questions"]:
        st.markdown("### Follow-up questions to improve accuracy")
        for i, q in enumerate(clarifier["follow_up_questions"]):
            st.markdown(f"- **Q{i+1}. {q}**")

        # Form prevents recompute while typing
        with st.form("fu_form", clear_on_submit=False):
            user_msg = st.text_input("💬 Add an answer (mention the Q number).")
            submitted = st.form_submit_button("Save answer")
        if submitted and user_msg:
            st.session_state.fu_answers[str(len(st.session_state.fu_answers) + 1)] = user_msg

        if st.session_state.fu_answers:
            st.markdown("**Your answers so far:**")
            for k, v in st.session_state.fu_answers.items():
                st.markdown(f"- A{k}: {v}")

        # Only set a flag here; compute happens in the gated block below
        if st.button("🔁 Re-run with collected answers"):
            st.session_state.recompute = True

# Single compute gate — runs only when the user clicks "Re-run with collected answers"
if st.session_state.get("recompute"):
    with st.spinner("Re-running with your follow-up answers..."):
        context_summary = st.session_state.context_summary or ""
        chosen = st.session_state.chosen or []

        enriched_context = (
            f"{context_summary}\n\n---\nUser's follow-up answers:\n"
            + json.dumps(st.session_state.fu_answers, ensure_ascii=False, indent=2)
            if st.session_state.fu_answers else context_summary
        )

        st.session_state.last_rows = run_pipeline(enriched_context, chosen)

    st.session_state.recompute = False

# If we have rows from either initial run or a re-run, render them
if st.session_state.last_rows:
    df = pd.DataFrame(st.session_state.last_rows)
    render_results_table_or_cards(df)

# 🔧 --- DEBUG UTILITIES ---
with st.expander("Debug: list available models"):
    if st.button("List models now"):
        try:
            models = client.models.list()
            st.code("\n".join(
                m.name for m in models if getattr(m, "name", None)
            ))
        except Exception as e:
            st.error(f"Could not list models: {e}")

st.markdown("---")
st.caption("Outputs generated with Gemini 2.5. Review all scores manually.")
