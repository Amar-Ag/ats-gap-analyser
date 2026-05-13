import streamlit as st
import streamlit.components.v1
import json
import os
import sys
import glob

# Add parent directory to path to import doc_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(parent_dir, "data")

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.agent.agent import instructions
except ImportError:
    instructions = "Instructions not found."    

def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        return json.load(f)
    
def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)   

def get_results_path(input_path):
    """Given an input JSON path, return the corresponding _results.json path."""
    base, ext = os.path.splitext(input_path)
    return base + "_results" + ext

def find_next_unlabelled(data, start_index):
    """Find the next unlabelled item starting from start_index+1, wrapping around."""
    n = len(data)
    for offset in range(1, n):
        i = (start_index + offset) % n
        if data[i].get('label') is None:
            return i
    return None

st.set_page_config(layout="wide", page_title="Agent Eval Labeling")

# ── Scroll anchor ──────────────────────────────────────────────────────────
st.markdown('<div id="scroll-top-anchor"></div>', unsafe_allow_html=True)

if st.session_state.get('_scroll_top', False):
    st.session_state._scroll_top = False
    js = """
        <script>
        function scrollToTop(attempts) {
            const doc = window.parent.document;
            const anchor = doc.getElementById('scroll-top-anchor');
            if (anchor) {
                anchor.scrollIntoView({behavior: 'instant', block: 'start'});
                return;
            }
            if (attempts > 0) {
                setTimeout(function() { scrollToTop(attempts - 1); }, 50);
            }
        }
        // Try multiple times as Streamlit may still be rendering
        setTimeout(function() { scrollToTop(10); }, 100);
        </script>
    """
    st.components.v1.html(js, height=0)

# ── File Selection ──────────────────────────────────────────────────────────
st.sidebar.header("📂 File Selection")
json_files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
input_files = [f for f in json_files if "eval" in os.path.basename(f)]

if not input_files:
    st.error("No JSON files found in the data directory.")
    st.stop()

selected_file = st.sidebar.selectbox(
    "Select evaluation file",
    input_files,
    format_func=lambda f: os.path.basename(f),
    key="file_selector"
)

results_file = get_results_path(selected_file)

# ── Load Data ───────────────────────────────────────────────────────────────
if 'selected_file' not in st.session_state or st.session_state.selected_file != selected_file:
    st.session_state.selected_file = selected_file
    if os.path.exists(results_file):
        st.session_state.data = load_data(results_file)
    else:
        st.session_state.data = load_data(selected_file)
        for item in st.session_state.data:
            if 'label' not in item:
                item['label'] = None
            if 'comments' not in item:
                item['comments'] = ""
    first_unlabelled = next(
        (i for i, item in enumerate(st.session_state.data) if item.get('label') is None), 0
    )
    st.session_state.current_index = first_unlabelled

if not st.session_state.data:
    st.error(f"Could not load data from {selected_file}")
    st.stop()

# ── Navigation ──────────────────────────────────────────────────────────────
st.sidebar.header("🧭 Navigation")
selection = st.sidebar.selectbox(
    "Select Run Result",
    range(len(st.session_state.data)),
    index=st.session_state.current_index,
    format_func=lambda i: f"{'✅' if st.session_state.data[i].get('label') == 'good' else '❌' if st.session_state.data[i].get('label') == 'bad' else '⬜'} {i+1}: {st.session_state.data[i].get('name', 'unknown')}")

if selection != st.session_state.current_index:
    st.session_state.current_index = selection
    st.session_state._scroll_top = True
    st.rerun()

# Progress
labeled_count = sum(1 for item in st.session_state.data if item.get('label') is not None)
st.sidebar.progress(labeled_count / len(st.session_state.data))
st.sidebar.text(f"Labeled: {labeled_count} / {len(st.session_state.data)}")

# ── Completion banner ───────────────────────────────────────────────────────
if labeled_count == len(st.session_state.data):
    st.success("🎉 Everything is labeled! Great job!")
    st.divider()

item = st.session_state.data[st.session_state.current_index]

st.title(f"Run {st.session_state.current_index + 1} / {len(st.session_state.data)}")

# metadata
st.markdown(f"**Session:** `{item.get('name', 'unknown')}` | **Category:** `{item.get('category', 'unknown')}` | **Status:** `{item.get('status', 'unknown')}`")
st.divider()

# inputs
col1, col2 = st.columns(2)
with col1:
    st.subheader("CV")
    st.text_area("CV Input", value=item.get('cv', 'empty'), height=300, disabled=True, label_visibility="collapsed")
with col2:
    st.subheader("Job Description")
    st.text_area("JD Input", value=item.get('jd', 'empty'), height=300, disabled=True, label_visibility="collapsed")

st.divider()

# agent result
st.subheader("Agent Response")
st.markdown(item.get('result', 'No result'))

st.divider()

# labeling
st.subheader("Label this response")

current_label = item.get('label')
current_failure = item.get('failure_category', '')
current_comments = item.get('comments', '')

col_good, col_bad = st.columns(2)

with col_good:
    if st.button("✅ Good", use_container_width=True, type="primary" if current_label == 'good' else "secondary"):
        item['label'] = 'good'
        item['failure_category'] = ''
        save_data(st.session_state.data, results_file)
        next_idx = find_next_unlabelled(st.session_state.data, st.session_state.current_index)
        if next_idx is not None:
            st.session_state.current_index = next_idx
            st.session_state._scroll_top = True
        st.rerun()

with col_bad:
    if st.button("❌ Bad", use_container_width=True, type="primary" if current_label == 'bad' else "secondary"):
        item['label'] = 'bad'
        save_data(st.session_state.data, results_file)
        st.rerun()

# show failure category only when bad
if item.get('label') == 'bad':
    failure_category = st.selectbox(
        "Failure category",
        ['', 'hallucination', 'missed_key_gap', 'wrong_score', 
         'poor_cover_letter', 'incomplete', 'correct_refusal', 'incorrect_refusal'],
        index=['', 'hallucination', 'missed_key_gap', 'wrong_score',
               'poor_cover_letter', 'incomplete', 'correct_refusal', 'incorrect_refusal'].index(current_failure) if current_failure in ['', 'hallucination', 'missed_key_gap', 'wrong_score', 'poor_cover_letter', 'incomplete', 'correct_refusal', 'incorrect_refusal'] else 0
    )
    if failure_category != current_failure:
        item['failure_category'] = failure_category
        save_data(st.session_state.data, results_file)
        st.rerun()

# comments
comments = st.text_area("Comments (optional)", value=current_comments, height=100)
if comments != current_comments:
    item['comments'] = comments
    save_data(st.session_state.data, results_file)