"""Open a file and watch a spider or rat correct spelling on screen."""

from __future__ import annotations

import hashlib
from pathlib import Path

import streamlit as st

import crawler
import spelling

ROOT = Path(__file__).parent
ICON = ROOT / "public" / "icon.png"
SAMPLES = {
    "Sample code": "buggy_code.py",
    "Sample document": "meeting_notes.txt",
}
FILE_TYPES = [
    "py",
    "txt",
    "md",
    "js",
    "ts",
    "tsx",
    "jsx",
    "html",
    "css",
    "json",
    "csv",
    "xml",
    "java",
    "c",
    "cpp",
    "cs",
    "go",
    "rs",
    "rst",
    "log",
]
TEXT_LIMIT = 150_000

st.set_page_config(
    page_title="Spider debug",
    page_icon=str(ICON),
    layout="wide",
)
st.logo(str(ICON), link="https://singareddyai.com")

st.session_state.setdefault("run_id", 0)
st.session_state.setdefault("debug_digest", "")


@st.cache_resource
def get_checker() -> spelling.SpellChecker:
    return spelling.build_checker()


@st.cache_data
def read_sample(filename: str) -> str:
    return (ROOT / "samples" / filename).read_text(encoding="utf-8")


def corrected_filename(name: str) -> str:
    path = Path(name)
    return f"{path.stem}.corrected{path.suffix or '.txt'}"


with st.sidebar:
    st.header("How to debug")
    st.markdown(
        """
:material/upload_file: Open a code or document file.

:material/pest_control: Choose a spider or a rat.

:material/play_arrow: Click **Debug code**.

The crawler enters the file and corrects each spelling mistake while you watch. A short tune plays during the crawl. Red words are mistakes. Green words are the fixes.
        """
    )

st.title("Spider debug")
st.caption(
    "Open a file, then click Debug code. A spider or a rat crawls through the text and fixes each spelling mistake on screen. A short tune plays while it works. Part of [singareddyai.com](https://singareddyai.com)."
)

uploaded = st.file_uploader(
    "Open a file",
    type=FILE_TYPES,
    help="A Python file, another code file, or a text document.",
)

with st.container(horizontal=True, vertical_alignment="bottom"):
    sample = st.segmented_control(
        "Sample",
        list(SAMPLES),
        default="Sample code",
        required=True,
        disabled=uploaded is not None,
    )
    creature_label = st.segmented_control(
        "Crawler",
        ["Spider", "Rat"],
        default="Spider",
        required=True,
    )
    icon = (
        ":material/pets:"
        if creature_label == "Rat"
        else ":material/pest_control:"
    )
    debug_clicked = st.button(
        "Debug code",
        type="primary",
        icon=icon,
        help="The crawler enters the file and replaces each red word while you watch.",
    )

if uploaded is not None:
    filename = uploaded.name
    text = uploaded.getvalue().decode("utf-8", errors="replace")
    st.caption(f"Using {filename}. Clear the uploaded file to return to the sample.")
else:
    filename = SAMPLES[sample]
    text = read_sample(filename)

trimmed = False
if len(text) > TEXT_LIMIT:
    text = text[:TEXT_LIMIT]
    trimmed = True

report = spelling.find_fixes(text, filename, get_checker())
digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]

if debug_clicked:
    st.session_state.run_id += 1
    st.session_state.debug_digest = digest

animate = (
    st.session_state.debug_digest == digest and st.session_state.run_id > 0
)

with st.container(horizontal=True, vertical_alignment="center"):
    st.metric("Spelling mistakes", len(report.fixes))
    st.caption(filename)

if trimmed:
    st.caption(f"Only the first {TEXT_LIMIT:,} characters are checked.")
if report.limited:
    st.caption("The crawl shows the first 80 mistakes so each fix stays visible.")

crawler.spell_crawler(
    text=text,
    fixes=list(report.fixes),
    creature="rat" if creature_label == "Rat" else "spider",
    run_id=int(st.session_state.run_id),
    animate=animate,
    digest=digest,
)

corrected = spelling.apply_fixes(text, report.fixes)
with st.container(horizontal=True, vertical_alignment="center"):
    st.download_button(
        "Download corrected file",
        data=corrected,
        file_name=corrected_filename(filename),
        mime="text/plain",
        icon=":material/download:",
        disabled=not report.fixes,
    )

with st.expander("Correction list"):
    if report.fixes:
        st.dataframe(
            [
                {
                    "Line": fix["line"],
                    "Mistake": fix["original"],
                    "Correction": fix["corrected"],
                }
                for fix in report.fixes
            ],
            hide_index=True,
            alt="Spelling corrections",
        )
    else:
        st.caption("Nothing to correct in this file.")
