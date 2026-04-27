
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="Data Mapping Tool", layout="wide")
st.title("🔗 Data Mapping Tool")

# -------------------------------
# Similarity Function
# -------------------------------
def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

# -------------------------------
# Load File
# -------------------------------
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

# -------------------------------
# Upload Files
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    source_file = st.file_uploader("Upload Source File", type=["csv", "xlsx"])

with col2:
    target_file = st.file_uploader("Upload Target File", type=["csv", "xlsx"])

if not source_file or not target_file:
    st.info("Please upload both files to continue.")
    st.stop()

source_df = load_file(source_file)
target_df = load_file(target_file)

source_cols = source_df.columns.tolist()
target_cols = target_df.columns.tolist()

# -------------------------------
# Auto Mapping
# -------------------------------
mapping = {}
for s_col in source_cols:
    best_match = None
    best_score = 0

    for t_col in target_cols:
        score = similarity(s_col, t_col)
        if score > best_score:
            best_score = score
            best_match = t_col

    mapping[s_col] = {
        "suggested": best_match,
        "confidence": round(best_score * 100, 2)
    }

st.subheader("🤖 Column Mapping")

# -------------------------------
# Mapping UI
# -------------------------------
final_mapping = {}

for s_col in source_cols:
    c1, c2, c3 = st.columns([3, 3, 2])

    with c1:
        st.write(f"**{s_col}**")

    with c2:
        selected = st.selectbox(
            f"Map {s_col}",
            options=target_cols,
            index=target_cols.index(mapping[s_col]["suggested"])
            if mapping[s_col]["suggested"] in target_cols else 0,
            key=s_col
        )

    with c3:
        st.write(f"{mapping[s_col]['confidence']}%")

    final_mapping[s_col] = selected

# -------------------------------
# VALIDATIONS
# -------------------------------

# 1. Prevent duplicate target mapping
if len(set(final_mapping.values())) != len(final_mapping.values()):
    st.error("❌ Multiple source columns mapped to the same target column!")
    st.stop()

# 2. Unmapped columns warning
unmapped = [col for col in source_cols if col not in final_mapping]
if unmapped:
    st.warning(f"⚠️ Unmapped columns: {', '.join(unmapped)}")

# -------------------------------
# Mapping Table
# -------------------------------
mapping_df = pd.DataFrame([
    {"Source Column": k, "Target Column": v}
    for k, v in final_mapping.items()
])

st.subheader("📋 Final Mapping Table")
st.dataframe(mapping_df, use_container_width=True)

# -------------------------------
# Download Mapping Table (NEW)
# -------------------------------
mapping_csv = mapping_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Mapping Template",
    data=mapping_csv,
    file_name="mapping_template.csv",
    mime="text/csv"
)

# -------------------------------
# Data Type Validation
# -------------------------------
st.subheader("🧠 Data Type Validation")

type_issues = []

for src, tgt in final_mapping.items():
    src_dtype = source_df[src].dtype
    tgt_dtype = target_df[tgt].dtype

    if src_dtype != tgt_dtype:
        type_issues.append({
            "Source": src,
            "Target": tgt,
            "Source Type": str(src_dtype),
            "Target Type": str(tgt_dtype)
        })

if type_issues:
    st.warning("⚠️ Data Type Mismatch Found")
    st.dataframe(pd.DataFrame(type_issues), use_container_width=True)
else:
    st.success("✅ No Data Type Issues")

# -------------------------------
# Apply Mapping
# -------------------------------
mapped_df = pd.DataFrame()

for src, tgt in final_mapping.items():
    mapped_df[tgt] = source_df[src]

# -------------------------------
# Side-by-Side Preview
# -------------------------------
st.subheader("🔍 Data Preview")

col1, col2 = st.columns(2)

with col1:
    st.write("### Source Data")
    st.dataframe(source_df.head(10), use_container_width=True)

with col2:
    st.write("### Mapped Data")
    st.dataframe(mapped_df.head(10), use_container_width=True)

# -------------------------------
# Download Final Mapped File
# -------------------------------
csv = mapped_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Mapped File",
    data=csv,
    file_name="mapped_output.csv",
    mime="text/csv"
)
