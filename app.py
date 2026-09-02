"""
Singlife Travel Claim — UAT Tester (Streamlit GUI)

A point-and-click front end for singlife_travel_claim.py, meant for
non-technical teammates who want to run a UAT test claim without touching
a terminal or CLI flags. Deployed on Streamlit Community Cloud.

>>> UAT ONLY <<< — see singlife_travel_claim.py's own docstring/guard.
This app refuses to start if BASE_URL there isn't the UAT host.
"""

from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import streamlit as st

import singlife_travel_claim as automation

ASSETS_DIR = Path(__file__).parent / "assets"

st.set_page_config(
    page_title="Singlife Travel Claim — UAT Tester",
    page_icon=str(ASSETS_DIR / "fermion_mark.png"),
    layout="centered",
)

# --------------------------------------------------------------------------
# Styling pass — matches the dark navy / lime-green Fermion brand palette
# used on jason.engineering (colors confirmed from that site's own computed
# styles: page bg #0A2733, card bg #0F3543, card border #1E4E60, accent
# lime #C3D700, header band #00567A, text #EAF6FA / muted #8FB6C4 — these
# also match the official Fermion Merimen deck theme's accent2/accent5).
# --------------------------------------------------------------------------
_logo_b64 = base64.b64encode((ASSETS_DIR / "fermion_mark.png").read_bytes()).decode()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* -----------------------------------------------------------------
       Force the dark navy theme directly on Streamlit's own containers.
       This is deliberately NOT left to .streamlit/config.toml alone --
       that file lives in a dotfolder that's easy to lose when uploading
       through a file picker (hidden by default in Finder/Explorer), and
       when it's missing Streamlit silently falls back to its default
       light theme with no error, which is exactly the "background looks
       wrong" symptom this is guarding against. config.toml is still
       included and still matters (it themes native widget chrome like
       button focus rings that CSS alone can't reach), but the page no
       longer *depends* on it for the core look.
       ----------------------------------------------------------------- */
    html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

    [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], [data-testid="stHeader"] {
        background-color: #0A2733 !important;
    }
    [data-testid="stHeader"] { background-image: none !important; }
    /* color (not fill) recolors the menu icon via its own fill="currentColor" --
       forcing `fill` directly here would also override the icon's separate
       invisible fill="none" hit-box path and paint it as a solid square. */
    [data-testid="stHeader"] * { color: #EAF6FA !important; }

    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 760px; }

    /* Default widget text (labels, radio/checkbox option text, captions,
       plain markdown) -- otherwise renders as dark text on the new dark
       background and becomes unreadable. */
    [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p,
    [data-testid="stRadioOption"] label p, [data-testid="stCheckbox"] label p,
    [data-testid="stCaptionContainer"] { color: #EAF6FA !important; }

    input[type="radio"], input[type="checkbox"] { accent-color: #C3D700; }

    [data-testid="stTextInputRootElement"] {
        background-color: #0F3543 !important; border-color: #1E4E60 !important;
    }
    [data-testid="stTextInputRootElement"] input { color: #EAF6FA !important; }

    [data-testid="stExpander"] {
        background-color: #0F3543 !important; border: 1px solid #1E4E60 !important;
        border-radius: 10px;
    }

    .brand-header {
        display: flex; align-items: center; gap: 14px;
        background: #00567A; border: 1px solid #1E4E60; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 1.25rem;
    }
    .brand-header img { width: 40px; height: 40px; flex-shrink: 0; }
    .brand-header .brand-title {
        color: #FFFFFF; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;
        line-height: 1.25;
    }
    .brand-header .brand-subtitle { color: #BFE6EF; font-size: 0.85rem; margin-top: 2px; }

    .uat-banner {
        background: #2E2410; border: 1px solid #6B5416; color: #F0D98C;
        border-radius: 10px; padding: 0.65rem 1rem; font-size: 0.88rem;
        margin-bottom: 1.5rem;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #C3D700; border-color: #C3D700; color: #0A2733;
        font-weight: 700; padding: 0.55rem 1.4rem;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #d4e820; border-color: #d4e820; color: #0A2733;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0F3543 !important; border: 1px solid #1E4E60 !important;
        border-radius: 12px;
    }
    code { color: #BFE6EF; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Safety guard — never let this run against anything but UAT, no matter
# what. Mirrors the exact same check singlife_travel_claim.py's CLI does.
# --------------------------------------------------------------------------
if "clientportaluat.merimen.com" not in automation.BASE_URL:
    st.error(
        "Refusing to start: the automation's BASE_URL is not the UAT host. "
        "This tool must never be pointed at a production claims portal."
    )
    st.stop()


# --------------------------------------------------------------------------
# One-time setup (cached per running server instance)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner="Setting up the browser (first run only, ~30-60s)...")
def _ensure_chromium_installed() -> bool:
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
    )
    return True


@st.cache_resource
def _get_run_lock() -> threading.Lock:
    # Shared across every visitor hitting this same server instance, so two
    # people can't accidentally launch two Chromium instances at once on
    # what is likely a memory-constrained free-tier container.
    return threading.Lock()


_ensure_chromium_installed()
run_lock = _get_run_lock()


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="brand-header">
        <img src="data:image/png;base64,{_logo_b64}" alt="Fermion" />
        <div>
            <div class="brand-title">Singlife Travel Claim — UAT Tester</div>
            <div class="brand-subtitle">Merimen Client Portal · Singlife General Insurance</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="uat-banner">⚠️ <strong>UAT / test data only.</strong> '
    "This submits a real entry into the UAT portal using dummy/placeholder "
    "details — never real customer data. It cannot reach production.</div>",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Form
# --------------------------------------------------------------------------
CASE_CHOICES = {
    "medical": "Medical Expense — auto-approved (default S$250)",
    "flight_delay": "Flight Delay — AV222 · Colombia",
    "baggage": "Baggage Loss/Damage — 2 items, max limit (default S$75 each)",
}

with st.container(border=True):
    case_key = st.radio(
        "Which claim scenario do you want to test?",
        options=list(CASE_CHOICES),
        format_func=lambda k: CASE_CHOICES[k],
    )

    with st.expander("Advanced options"):
        policy_suffix = st.text_input(
            "Policy number suffix (optional)",
            value="",
            help="Appended to the end of the auto-generated policy number, "
                 "on top of its random 3-digit prefix, if you want to tag "
                 "this run with something recognisable.",
        )
        fill_only = st.checkbox(
            "Fill the form but don't submit (stop before the final Confirm)",
            value=False,
            help="Fills out and reviews the entire claim, then stops at the "
                 "'Proceed to Submit?' step instead of confirming it.",
        )

        medical_amount = "250.00"
        baggage_item_amount = "75.00"
        if case_key == "medical":
            medical_amount = st.text_input("Medical claim amount (S$)", value="250.00")
        elif case_key == "baggage":
            baggage_item_amount = st.text_input(
                "Per-item claim amount (S$) — applied to both items", value="75.00",
            )

    show_live_view = st.checkbox(
        "Show live screenshots while it runs",
        value=True,
        help="There's no real browser window to watch on a remote server, but "
             "with this on you'll see a screenshot of the portal after each "
             "wizard step completes -- a 'flipbook' view of the run in near "
             "real time. Turning it off saves a little time per run.",
    )

    run_clicked = st.button("Run test claim", type="primary", use_container_width=True)


# --------------------------------------------------------------------------
# Live log capture — swaps sys.stdout for the duration of a run so the
# script's existing print() calls show up in the UI as they happen. Safe to
# do globally (not per-thread) because run_lock guarantees only one run is
# ever in flight on this server instance at a time.
# --------------------------------------------------------------------------
class _StreamlitLogWriter:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.lines: list[str] = []
        self._partial = ""

    def write(self, text: str) -> int:
        self._partial += text
        while "\n" in self._partial:
            line, self._partial = self._partial.split("\n", 1)
            if line.strip():
                self.lines.append(line)
        rendered = "\n".join(self.lines[-300:]) or "(waiting for output...)"
        self.placeholder.code(rendered, language=None)
        return len(text)

    def flush(self) -> None:
        pass


def _run_case(case_key: str, *, policy_suffix: str, fill_only: bool,
              medical_amount: str, baggage_item_amount: str,
              show_live_view: bool,
              status, log_placeholder, live_view_placeholder) -> None:
    run_fn = automation.CASES[case_key]
    run_kwargs = {"policy_suffix": policy_suffix, "auto_submit": not fill_only}
    if case_key == "medical":
        run_kwargs["claim_amount"] = medical_amount
    elif case_key == "baggage":
        run_kwargs["item_amount"] = baggage_item_amount

    pdf_dir = Path(tempfile.mkdtemp(prefix="singlife_uat_docs_"))
    writer = _StreamlitLogWriter(log_placeholder)
    old_stdout = sys.stdout
    sys.stdout = writer

    screenshot_path: Path | None = None
    try:
        with automation.sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox"],
            )
            page = browser.new_page()
            page.set_default_timeout(automation.DEFAULT_TIMEOUT_MS)

            def _show_live_screenshot(label: str) -> None:
                # Called from the same thread driving the automation, right
                # after a step settles -- never mid-fill -- so it's always
                # safe to touch the page here (Playwright's sync API isn't
                # safe to call concurrently from another thread).
                try:
                    shot = page.screenshot(type="jpeg", quality=60)
                except Exception:
                    return
                live_view_placeholder.image(shot, caption=label)

            on_step = _show_live_screenshot if show_live_view else None

            try:
                run_fn(page, pdf_dir, on_step=on_step, **run_kwargs)
            except Exception:
                screenshot_path = (
                    Path(tempfile.gettempdir())
                    / f"singlife_uat_failure_{int(time.time())}.png"
                )
                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                except Exception:
                    screenshot_path = None
                raise
            finally:
                browser.close()
    finally:
        sys.stdout = old_stdout

    return None


if run_clicked:
    if not run_lock.acquire(blocking=False):
        st.warning(
            "Another test claim is already running on this server right now — "
            "please wait a moment and try again."
        )
    else:
        try:
            with st.status("Running...", expanded=True) as status:
                live_view_placeholder = st.empty()
                log_placeholder = st.empty()
                try:
                    _run_case(
                        case_key,
                        policy_suffix=policy_suffix,
                        fill_only=fill_only,
                        medical_amount=medical_amount,
                        baggage_item_amount=baggage_item_amount,
                        show_live_view=show_live_view,
                        status=status,
                        log_placeholder=log_placeholder,
                        live_view_placeholder=live_view_placeholder,
                    )
                except Exception as exc:
                    status.update(label="Failed", state="error", expanded=True)
                    st.error(
                        "Something went wrong on the portal partway through. "
                        "See the screenshot and details below."
                    )
                    failure_shots = sorted(
                        Path(tempfile.gettempdir()).glob("singlife_uat_failure_*.png"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True,
                    )
                    if failure_shots:
                        st.image(
                            str(failure_shots[0]),
                            caption="Portal state at the point of failure",
                        )
                    with st.expander("Technical details (for reporting this issue)"):
                        st.exception(exc)
                else:
                    status.update(label="Done", state="complete", expanded=False)
                    if fill_only:
                        st.success(
                            "Filled out the whole claim and stopped right before "
                            "the final Confirm step, as requested — nothing was "
                            "actually submitted."
                        )
                    else:
                        st.success("Claim submitted successfully.")
        finally:
            run_lock.release()
