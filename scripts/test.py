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

print(current_dir)
print(parent_dir)
print(data_dir)