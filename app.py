import hashlib
import os
import re
from datetime import datetime
from pathlib import Path

import pymupdf
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ---------- Configuration ----------
load_dotenv()
st.set_page_config(
    page_title="BenchBuddy AI | Electronics Workspace",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()

client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )
    if API_KEY
    else None
)

# ---------- High-contrast styling ----------
st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp {
        background: #0b1120;
        color: #f1f5f9;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.96);
    }

    [data-testid="stSidebar"] {
        background: #101a2d;
        border-right: 1px solid #34445e;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, h5, h6, label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] em {
        color: #f1f5f9 !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #cbd5e1 !important;
    }

    [data-testid="stMetric"] {
        background: #152238;
        border: 1px solid #354560;
        border-radius: 12px;
        padding: 0.8rem 1rem;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #d4deec !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    [data-baseweb="tab-list"] {
        gap: 0.35rem;
        border-bottom: 1px solid #354560;
    }

    [data-baseweb="tab"] {
        background: #152238;
        border-radius: 8px 8px 0 0;
        color: #edf4ff !important;
        padding: 0.7rem 1rem;
    }

    [data-baseweb="tab"] * {
        color: #edf4ff !important;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        background: #075985;
        border-bottom: 3px solid #67e8f9;
    }

    [data-baseweb="tab"][aria-selected="true"] * {
        color: #ffffff !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {
        background: #101a2d !important;
        color: #ffffff !important;
        border: 1px solid #657895 !important;
        border-radius: 8px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #c1ccdc !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploader"] {
        background: #121e33;
        border: 1px dashed #657895;
        border-radius: 12px;
        padding: 0.6rem;
    }

    [data-testid="stFileUploader"] * {
        color: #f1f5f9 !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: #075985;
        color: #ffffff !important;
        border: 1px solid #38bdf8;
        border-radius: 9px;
        font-weight: 700;
        min-height: 2.5rem;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #0e7490;
        border-color: #a5f3fc;
        color: #ffffff !important;
    }

    [data-testid="stAlert"] p {
        color: #ffffff !important;
    }

    [data-testid="stExpander"] {
        background: #111d31;
        border: 1px solid #34445e;
        border-radius: 10px;
    }

    hr {
        border-color: #354560;
    }

    code {
        color: #a5f3fc !important;
        background: #111d31 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- PDF and search helpers ----------
STOP_WORDS = set(
    """
    a about above after again all also am an and any are as at be because
    been before being below between both but by can could did do does doing
    down during each few for from further get give had has have having he her
    here hers him his how i if in into is it its just me more most my no nor
    not of off on once only or other our out over own please same she should
    so some such than that the their them then there these they this those
    through to too under until up very was we were what when where which
    while who why will with would you your
    """.split()
)


def tokenize(text):
    """Extract useful searchable terms and part numbers."""
    words = re.findall(
        r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)?",
        text.lower(),
    )
    return {
        word
        for word in words
        if len(word) > 1 and word not in STOP_WORDS
    }


def extract_pdf(pdf_bytes):
    """Read selectable text from every PDF page."""
    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    ) as pdf:
        for number, page in enumerate(pdf, start=1):
            pages.append(
                {
                    "page": number,
                    "text": page.get_text("text").strip(),
                }
            )

    if not pages:
        raise ValueError("This PDF has no pages.")

    return pages


def load_document(upload, state_key):
    """Parse an uploaded PDF only when its contents change."""
    if upload is None:
        return

    raw = upload.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    previous = st.session_state.get(state_key)

    if previous and previous.get("hash") == digest:
        return

    try:
        with st.spinner(f"Reading {upload.name}..."):
            pages = extract_pdf(raw)

        st.session_state[state_key] = {
            "name": upload.name,
            "hash": digest,
            "size": len(raw),
            "pages": pages,
            "loaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        if state_key == "primary_doc":
            for key in (
                "search_results",
                "last_search",
                "ai_answer",
                "ai_sources",
                "test_plan",
                "test_sources",
            ):
                st.session_state.pop(key, None)
        else:
            st.session_state.pop("comparison_answer", None)
            st.session_state.pop("comparison_sources", None)

        st.success(f"Loaded {upload.name}")

    except Exception as exc:
        st.error(f"Couldn't read {upload.name}: {exc}")


def rank_pages(pages, query, limit=8):
    """Rank pages using keyword coverage and repeated matches."""
    terms = tokenize(query)

    if not terms:
        return []

    found = []

    for page in pages:
        text = page.get("text", "")

        if not text:
            continue

        page_terms = tokenize(text)
        matched = terms.intersection(page_terms)

        if matched:
            coverage = len(matched) / len(terms)
            repeat = sum(
                text.lower().count(term)
                for term in matched
            )

            score = min(
                coverage * 0.8 + min(repeat, 20) / 100,
                1.0,
            )

            found.append(
                {
                    "page": page["page"],
                    "text": text,
                    "matched": sorted(matched),
                    "score": score,
                }
            )

    found.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return found[:limit]


def get_context(document, query, limit=6, chars=3200):
    """Select relevant page excerpts for AI requests."""
    if not document:
        return "", []

    selected = rank_pages(
        document["pages"],
        query,
        limit=limit,
    )

    if not selected:
        selected = [
            {
                "page": page["page"],
                "text": page["text"],
                "score": 0,
                "matched": [],
            }
            for page in document["pages"]
            if page.get("text")
        ][:min(limit, 4)]

    context = "\n\n".join(
        f"PAGE {item['page']}:\n{item['text'][:chars]}"
        for item in selected
    )

    return context, selected


def ask_model(prompt, max_tokens=1000):
    """Send a prompt to the configured OpenRouter model."""
    if client is None:
        raise RuntimeError(
            "AI is not configured. Add OPENROUTER_API_KEY to your .env file."
        )

    result = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=max_tokens,
    )

    answer = result.choices[0].message.content

    if not answer:
        raise RuntimeError("The AI service returned an empty answer.")

    return answer.strip()


def text_page_count(doc):
    """Count pages containing selectable text."""
    if not doc:
        return 0

    return sum(
        bool(page.get("text"))
        for page in doc["pages"]
    )


def generic_test_plan(component, goal):
    """Provide a generic checklist if AI is unavailable."""
    return f"""# Virtual Bench-Test Checklist: {component}

**Goal:** {goal or 'Basic functional verification'}

> Generic planning template only—not a verified procedure for this part. Confirm pinout, recommended operating conditions, absolute maximum ratings, and the manufacturer's test method before applying power.

## Before testing
- [ ] Confirm the exact part number, package, pinout, and variant.
- [ ] Read recommended operating conditions and absolute maximum ratings in the datasheet.
- [ ] Check instrument ratings and inspect leads, probes, and the test fixture.
- [ ] Power off before wiring; check polarity and ground requirements.
- [ ] Use a current-limited supply where applicable and remain within datasheet limits.

## Procedure
- [ ] Record the setup, equipment, supply settings, and ambient conditions.
- [ ] Verify wiring and continuity before applying power.
- [ ] Power up conservatively; stop if current, temperature, or behavior is unexpected.
- [ ] Measure only signals within device and instrument ratings.
- [ ] Change one condition at a time and record the response.
- [ ] Compare readings against the datasheet's test conditions and tolerances.
- [ ] Power down and discharge stored energy where applicable before changing wiring.

## Results to record
- [ ] Supply voltage and current
- [ ] Input conditions and measured output
- [ ] Equipment, setup, and ambient conditions
- [ ] Expected datasheet value/range and its source page
- [ ] Actual result, deviation, and pass/fail reasoning

## Safety and limitations
Do not exceed absolute maximum ratings. Do not connect this generic plan directly to mains or hazardous voltages. This is a planning aid, not a substitute for the manufacturer's test procedure or qualified lab supervision.
"""


def make_report(primary, comparison):
    """Create a downloadable summary of this workspace session."""
    lines = [
        "# BenchBuddy AI Workspace Report",
        "",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
        "",
    ]

    for label, doc in (
        ("Primary datasheet", primary),
        ("Comparison datasheet", comparison),
    ):
        lines.append(f"## {label}")

        if doc:
            lines += [
                f"- File: {doc['name']}",
                f"- PDF pages: {len(doc['pages'])}",
                f"- Pages with selectable text: {text_page_count(doc)}",
                f"- File size: {doc['size'] / 1024:.1f} KB",
                "",
            ]
        else:
            lines += [
                "No document loaded.",
                "",
            ]

    query = st.session_state.get("last_search", "")
    results = st.session_state.get("search_results", [])

    if query:
        lines += [
            f"## Search: {query}",
            "",
        ]

        for item in results:
            lines += [
                f"### Page {item['page']} ({item['score']:.0%} term score)",
                f"Matched terms: {', '.join(item['matched'])}",
                item["text"][:1800],
                "",
            ]

    question = st.session_state.get("ai_question", "")
    answer = st.session_state.get("ai_answer", "")

    if question and answer:
        lines += [
            "## AI question",
            question,
            "",
            "## AI answer",
            answer,
            "",
        ]

    if st.session_state.get("comparison_answer"):
        lines += [
            "## Component comparison",
            st.session_state["comparison_answer"],
            "",
        ]

    if st.session_state.get("test_plan"):
        lines += [
            "## Virtual bench-test plan",
            st.session_state["test_plan"],
            "",
        ]

    lines += [
        "---",
        "Verify important electrical values and test procedures in the original manufacturer's documentation.",
    ]

    return "\n".join(lines)


# ---------- Sidebar ----------
with st.sidebar:
    st.title("🔧 BenchBuddy AI")
    st.caption("Electronics datasheet workspace")
    st.divider()

    if client:
        st.success("AI connection configured")
        st.caption(f"Model route: {MODEL_NAME}")
    else:
        st.warning("AI connection not configured")
        st.caption(
            "Add OPENROUTER_API_KEY to .env to enable AI features."
        )

    st.divider()
    st.markdown("**Workflow**")
    st.markdown(
        "1. Upload datasheet(s)\n"
        "2. Search specifications\n"
        "3. Ask source-grounded AI\n"
        "4. Compare components\n"
        "5. Generate a test checklist\n"
        "6. Export a report"
    )

    st.divider()
    st.caption(
        "Educational aid only. Verify limits and procedures against "
        "the manufacturer documentation."
    )


# ---------- Header ----------
st.title("🔧 BenchBuddy AI")
st.subheader(
    "Electronics datasheets, component comparisons, and test planning"
)

st.write(
    "Spend less time hunting through PDFs. Find relevant pages, ask "
    "questions grounded in document excerpts, compare two components, "
    "and create a test checklist."
)


# ---------- Upload documents ----------
with st.container(border=True):
    st.markdown("### 1 · Load datasheets")

    upload_a, upload_b = st.columns(2)

    with upload_a:
        primary_upload = st.file_uploader(
            "Primary datasheet (PDF)",
            type=["pdf"],
            key="primary_upload",
            help="For example, your LM358 datasheet.",
        )

    with upload_b:
        comparison_upload = st.file_uploader(
            "Second datasheet (optional)",
            type=["pdf"],
            key="comparison_upload",
            help="Upload a second component datasheet to compare.",
        )

    load_document(primary_upload, "primary_doc")
    load_document(comparison_upload, "comparison_doc")


primary = st.session_state.get("primary_doc")
comparison = st.session_state.get("comparison_doc")

if primary:
    metrics = st.columns(4)

    metrics[0].metric(
        "Primary PDF pages",
        len(primary["pages"]),
    )
    metrics[1].metric(
        "Pages with text",
        f"{text_page_count(primary)}/{len(primary['pages'])}",
    )
    metrics[2].metric(
        "File size",
        f"{primary['size'] / 1024:.0f} KB",
    )
    metrics[3].metric(
        "Second PDF",
        "Loaded" if comparison else "Not loaded",
    )
else:
    st.info("Upload a PDF above to activate the workspace.")


# ---------- Tabs ----------
t_overview, t_search, t_ai, t_compare, t_test, t_export = st.tabs(
    [
        "Overview",
        "Search",
        "Ask AI",
        "Compare components",
        "Bench-test plan",
        "Export report",
    ]
)


# ---------- Overview ----------
with t_overview:
    st.markdown("### Workspace overview")

    if primary:
        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                st.markdown("#### 📘 Primary datasheet")
                st.write(f"**File:** {primary['name']}")
                st.write(f"**Pages:** {len(primary['pages'])}")
                st.write(
                    "**Pages with selectable text:** "
                    f"{text_page_count(primary)}"
                )

        with right:
            with st.container(border=True):
                st.markdown("#### 📗 Comparison datasheet")

                if comparison:
                    st.write(f"**File:** {comparison['name']}")
                    st.write(f"**Pages:** {len(comparison['pages'])}")
                    st.write(
                        "**Pages with selectable text:** "
                        f"{text_page_count(comparison)}"
                    )
                else:
                    st.write(
                        "Not loaded yet. Add a second PDF above to compare components."
                    )

        st.markdown("**Suggested workflow**")
        st.markdown(
            "- Search for supply voltage, gain bandwidth, temperature, or pinout.\n"
            "- Ask a focused question and check the cited source pages.\n"
            "- Compare components only after checking the full datasheets.\n"
            "- Download a virtual test checklist and verify it before using it in a lab."
        )

    else:
        st.markdown("#### Start here")
        st.write(
            "Upload a datasheet to extract text and enable search, AI Q&A, "
            "comparison, and test-plan generation."
        )
        st.write(
            "**Designed for:** electronics students, makers, and engineers "
            "who use component datasheets."
        )


# ---------- Datasheet search ----------
with t_search:
    st.markdown("### Search the primary datasheet")

    if not primary:
        st.info("Load a primary PDF above first.")

    else:
        with st.form("search_form"):
            query = st.text_input(
                "Keywords or specification",
                placeholder="e.g. input offset voltage, operating temperature",
            )

            submitted = st.form_submit_button(
                "Search pages",
                use_container_width=True,
            )

        if submitted:
            st.session_state["last_search"] = query.strip()

            st.session_state["search_results"] = (
                rank_pages(primary["pages"], query, limit=10)
                if query.strip()
                else []
            )

        saved_query = st.session_state.get("last_search", "")
        results = st.session_state.get("search_results", [])

        if saved_query:
            st.markdown(f"**Search:** `{saved_query}`")

            if results:
                st.success(
                    f"Found {len(results)} matching page(s). "
                    "These are keyword relevance scores, not guaranteed technical relevance."
                )

                for item in results:
                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(f"#### Page {item['page']}")
                            st.caption(
                                "Matched terms: "
                                + ", ".join(item["matched"])
                            )

                        with col2:
                            st.metric(
                                "Match score",
                                f"{item['score']:.0%}",
                            )

                        st.text(item["text"][:2200])

            else:
                st.warning(
                    "No matching pages found. Try a shorter or alternate keyword."
                )


# ---------- AI Q&A ----------
with t_ai:
    st.markdown("### Ask document-grounded AI")

    st.write(
        "BenchBuddy selects relevant pages and sends excerpts to the configured "
        "model. Answers can be incomplete or wrong; verify important values in the source PDF."
    )

    if not primary:
        st.info("Load a primary PDF above first.")

    else:
        with st.form("ai_form"):
            question = st.text_area(
                "Your question",
                placeholder=(
                    "What is the operating temperature range of this component? "
                    "Cite the page."
                ),
                height=100,
            )

            ai_submitted = st.form_submit_button(
                "Ask BenchBuddy AI",
                use_container_width=True,
            )

        if ai_submitted:
            st.session_state["ai_question"] = question.strip()
            st.session_state["ai_answer"] = ""

            if not question.strip():
                st.warning("Enter a question first.")

            elif not client:
                st.error(
                    "AI isn't configured. Add OPENROUTER_API_KEY to .env "
                    "and restart Streamlit."
                )

            else:
                context, selected = get_context(
                    primary,
                    question,
                    limit=6,
                    chars=3600,
                )

                prompt = f"""You are BenchBuddy AI, an electronics engineering datasheet assistant.

Answer using only the supplied excerpts. Do not invent values, units, pin assignments, or specifications. Cite facts with page numbers like [Page 7]. If the excerpts do not contain the answer, say so rather than guessing. Distinguish facts from explanations. Explain clearly and remind the user to verify critical values against the manufacturer's original datasheet.

DOCUMENT: {primary['name']}

EXCERPTS:
{context}

QUESTION:
{question}
"""

                try:
                    with st.spinner(
                        "Reviewing excerpts and preparing an answer..."
                    ):
                        st.session_state["ai_answer"] = ask_model(
                            prompt,
                            max_tokens=900,
                        )

                        st.session_state["ai_sources"] = [
                            item["page"]
                            for item in selected
                        ]

                except Exception as exc:
                    st.error(
                        "The AI request failed. A free-model limit, "
                        "connection issue, or model availability problem "
                        "may be responsible."
                    )
                    st.caption(str(exc))

        answer = st.session_state.get("ai_answer", "")

        if answer:
            st.markdown("#### AI answer")
            st.markdown(answer)

            pages_used = st.session_state.get("ai_sources", [])

            if pages_used:
                st.caption(
                    "Source pages sent to AI: "
                    + ", ".join(map(str, pages_used))
                )

            st.caption(
                "Verify important specifications in the manufacturer's original datasheet."
            )


# ---------- Component comparison ----------
with t_compare:
    st.markdown("### Compare two component datasheets")

    if not primary:
        st.info("Load the primary datasheet above first.")

    elif not comparison:
        st.info("Load a second PDF above to enable comparison.")

    else:
        st.write(
            f"**A:** {primary['name']}  |  **B:** {comparison['name']}"
        )

        st.write(
            "The comparison cites supplied source excerpts and should flag "
            "missing information rather than assume the parts are interchangeable."
        )

        if st.button(
            "Compare components",
            use_container_width=True,
        ):
            st.session_state.pop("comparison_answer", None)

            if not client:
                st.error(
                    "AI isn't configured. Add OPENROUTER_API_KEY to .env to use comparison."
                )

            else:
                compare_query = (
                    "absolute maximum ratings recommended operating conditions "
                    "supply voltage operating temperature electrical characteristics "
                    "pin configuration package gain bandwidth slew rate "
                    "input offset voltage input bias current output current"
                )

                context_a, pages_a = get_context(
                    primary,
                    compare_query,
                    limit=7,
                    chars=3000,
                )

                context_b, pages_b = get_context(
                    comparison,
                    compare_query,
                    limit=7,
                    chars=3000,
                )

                prompt = f"""Compare these two electronics datasheets using only the excerpts. Never invent a value. Cite the file name and page for each fact. If a fact is missing or the conditions/units differ, say 'Not found in supplied excerpts' or 'Not directly comparable'. Do not claim the components are drop-in replacements without evidence.

Return a compact Markdown table where supported, covering part number, package/pinout, supply voltage, operating temperature, absolute maximum ratings, input offset voltage, input bias current, gain-bandwidth, slew rate, output drive, power, and limitations. Then add 'Compatibility cautions' and 'What to verify in the full datasheets'.

DATASHEET A: {primary['name']}
{context_a}

DATASHEET B: {comparison['name']}
{context_b}
"""

                try:
                    with st.spinner(
                        "Comparing excerpts from both PDFs..."
                    ):
                        st.session_state["comparison_answer"] = ask_model(
                            prompt,
                            max_tokens=1400,
                        )

                        st.session_state["comparison_sources"] = {
                            "A": [x["page"] for x in pages_a],
                            "B": [x["page"] for x in pages_b],
                        }

                except Exception as exc:
                    st.error(
                        "Comparison failed. Check the API connection or retry later."
                    )
                    st.caption(str(exc))

        result = st.session_state.get("comparison_answer", "")

        if result:
            st.markdown("#### Comparison result")
            st.markdown(result)

            src = st.session_state.get("comparison_sources", {})

            st.caption(
                f"Source pages sent to AI — A: {src.get('A', [])}; "
                f"B: {src.get('B', [])}"
            )

            st.download_button(
                "Download comparison (.md)",
                data=result,
                file_name="benchbuddy_component_comparison.md",
                mime="text/markdown",
                use_container_width=True,
            )


# ---------- Virtual bench-test plan ----------
with t_test:
    st.markdown("### Virtual bench-test plan")

    st.write(
        "Generate a structured checklist. This is a planning aid, not a "
        "validated manufacturer procedure or replacement for lab supervision."
    )

    default_component = (
        Path(primary["name"]).stem
        if primary
        else "Electronic component"
    )

    component_name = st.text_input(
        "Component / board name",
        value=default_component,
        key="test_component_name",
    )

    test_goal = st.text_input(
        "What do you want to verify?",
        value=st.session_state.get(
            "test_goal",
            "Basic functional verification",
        ),
        key="test_goal",
        placeholder="e.g. op-amp output response in a low-voltage test circuit",
    )

    st.caption(
        "When AI is configured, the plan uses datasheet excerpts. "
        "Without AI, a generic checklist is provided and clearly labeled."
    )

    if st.button(
        "Generate test plan",
        use_container_width=True,
    ):
        if primary and client:
            plan_query = (
                f"{component_name} {test_goal} recommended operating conditions "
                "absolute maximum ratings test circuit electrical characteristics safety"
            )

            context, selected = get_context(
                primary,
                plan_query,
                limit=6,
                chars=3000,
            )

            prompt = f"""Create a conservative, beginner-friendly virtual bench-test checklist.

Component: {component_name}
Goal: {test_goal}
Datasheet: {primary['name']}

Excerpts:
{context}

Include Objective, Equipment, Pre-test checks, Procedure, Measurements to record, Pass/fail criteria, and Safety/limitations. Use checkboxes. Never invent numerical limits, pins, supply ranges, or pass/fail thresholds. If missing, say to look up the full manufacturer datasheet before testing. Keep within recommended operating conditions; do not suggest mains or hazardous voltages. Include current limiting where appropriate, power-off wiring, and stopping if current/temperature is unexpected. Cite pages for component-specific facts. Label this as a planning aid, not a validated test procedure.
"""

            try:
                with st.spinner("Preparing the checklist..."):
                    st.session_state["test_plan"] = ask_model(
                        prompt,
                        max_tokens=1300,
                    )

                    st.session_state["test_sources"] = [
                        x["page"]
                        for x in selected
                    ]

            except Exception as exc:
                st.warning(
                    "AI plan generation failed, so a generic checklist was created instead."
                )
                st.caption(str(exc))

                st.session_state["test_plan"] = generic_test_plan(
                    component_name,
                    test_goal,
                )

                st.session_state["test_sources"] = []

        else:
            st.session_state["test_plan"] = generic_test_plan(
                component_name,
                test_goal,
            )

            st.session_state["test_sources"] = []

    plan = st.session_state.get("test_plan", "")

    if plan:
        st.markdown("#### Generated checklist")
        st.markdown(plan)

        sources = st.session_state.get("test_sources", [])

        if sources:
            st.caption(
                "Source pages sent to AI: "
                + ", ".join(map(str, sources))
            )

        st.download_button(
            "Download test plan (.md)",
            data=plan,
            file_name="benchbuddy_virtual_test_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ---------- Export report ----------
with t_export:
    st.markdown("### Export workspace report")

    st.write(
        "Create a Markdown summary of loaded PDFs and generated outputs "
        "from this session. It excludes your API key and the full PDF text."
    )

    st.download_button(
        "Download workspace report",
        data=make_report(primary, comparison),
        file_name="benchbuddy_workspace_report.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ---------- Footer ----------
st.divider()

st.caption(
    "BenchBuddy AI · Built for electronics learners · AI output can be inaccurate. "
    "Verify electrical limits and test procedures in the original manufacturer documentation."
)