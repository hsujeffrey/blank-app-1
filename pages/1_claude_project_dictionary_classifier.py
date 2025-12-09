import streamlit as st
import pandas as pd
import io

# Page configuration
st.set_page_config(
    page_title="Marketing Tactic Classifier",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'dictionaries' not in st.session_state:
    st.session_state.dictionaries = {
        'urgency_marketing': [
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they are gone',
            'selling out', 'selling fast', 'act now', 'do not wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        ],
        'exclusive_marketing': [
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        ]
    }

if 'results_df' not in st.session_state:
    st.session_state.results_df = None

def classify_statement(text, dictionaries):
    """Classify a statement based on marketing tactic dictionaries."""
    if pd.isna(text):
        return {}
    
    text_lower = str(text).lower()
    results = {}
    
    for tactic, keywords in dictionaries.items():
        matches = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        results[tactic] = {
            'present': len(matches) > 0,
            'count': len(matches),
            'matches': matches
        }
    
    return results

def process_dataframe(df, dictionaries):
    """Process the dataframe and add classification columns."""
    # Find the statement column
    statement_col = None
    for col in df.columns:
        if col.lower() in ['statement', 'text', 'content']:
            statement_col = col
            break
    
    if statement_col is None:
        statement_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    # Apply classification
    df['classification'] = df[statement_col].apply(lambda x: classify_statement(x, dictionaries))
    
    # Extract results to separate columns
    for tactic in dictionaries.keys():
        df[f'{tactic}_present'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('present', False))
        df[f'{tactic}_count'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('count', 0))
        df[f'{tactic}_matches'] = df['classification'].apply(lambda x: ', '.join(x.get(tactic, {}).get('matches', [])))
    
    return df, statement_col

# Title and description
st.title("📊 Marketing Tactic Classifier")
st.markdown("Upload your dataset and classify statements using customizable marketing tactic dictionaries")

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 Upload Dataset")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} rows")
            st.session_state.uploaded_df = df
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

with col2:
    st.header("⚙️ Actions")
    
    if st.button("🔍 Run Classification", use_container_width=True, type="primary"):
        if 'uploaded_df' in st.session_state:
            with st.spinner("Classifying statements..."):
                result_df, statement_col = process_dataframe(
                    st.session_state.uploaded_df.copy(),
                    st.session_state.dictionaries
                )
                st.session_state.results_df = result_df
                st.session_state.statement_col = statement_col
                st.success("Classification complete!")
        else:
            st.warning("Please upload a dataset first")
    
    if st.session_state.results_df is not None:
        # Convert results to CSV
        csv_buffer = io.StringIO()
        st.session_state.results_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Results",
            data=csv_data,
            file_name="classified_data.csv",
            mime="text/csv",
            use_container_width=True
        )

# Dictionary Management
st.header("📚 Marketing Tactic Dictionaries")

# Add new tactic
with st.expander("➕ Add New Tactic Category"):
    new_tactic = st.text_input("Tactic name (e.g., scarcity_marketing)")
    if st.button("Add Tactic"):
        if new_tactic and new_tactic not in st.session_state.dictionaries:
            st.session_state.dictionaries[new_tactic] = []
            st.success(f"Added tactic: {new_tactic}")
            st.rerun()
        elif new_tactic in st.session_state.dictionaries:
            st.warning("This tactic already exists")
        else:
            st.warning("Please enter a tactic name")

# Manage existing tactics
for tactic in list(st.session_state.dictionaries.keys()):
    with st.expander(f"📝 {tactic} ({len(st.session_state.dictionaries[tactic])} keywords)"):
        
        # Add keyword
        col_input, col_add = st.columns([4, 1])
        with col_input:
            new_keyword = st.text_input(
                f"Add keyword to {tactic}",
                key=f"keyword_{tactic}",
                label_visibility="collapsed",
                placeholder="Enter keyword..."
            )
        with col_add:
            if st.button("Add", key=f"add_{tactic}"):
                if new_keyword and new_keyword not in st.session_state.dictionaries[tactic]:
                    st.session_state.dictionaries[tactic].append(new_keyword)
                    st.rerun()
        
        # Display keywords
        keywords = st.session_state.dictionaries[tactic]
        if keywords:
            for i, keyword in enumerate(keywords):
                col_kw, col_del = st.columns([5, 1])
                with col_kw:
                    st.text(keyword)
                with col_del:
                    if st.button("🗑️", key=f"del_{tactic}_{i}"):
                        st.session_state.dictionaries[tactic].remove(keyword)
                        st.rerun()
        
        # Remove tactic button
        st.divider()
        if st.button(f"🗑️ Remove {tactic}", key=f"remove_tactic_{tactic}", type="secondary"):
            del st.session_state.dictionaries[tactic]
            st.rerun()

# Display Results
if st.session_state.results_df is not None:
    st.header("📊 Classification Results")
    
    # Summary Statistics
    st.subheader("Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    total_statements = len(st.session_state.results_df)
    any_tactic_cols = [col for col in st.session_state.results_df.columns if '_present' in col]
    statements_with_tactics = st.session_state.results_df[any_tactic_cols].any(axis=1).sum()
    
    with col1:
        st.metric("Total Statements", total_statements)
    with col2:
        st.metric("With Any Tactic", statements_with_tactics)
    with col3:
        match_rate = (statements_with_tactics / total_statements * 100) if total_statements > 0 else 0
        st.metric("Match Rate", f"{match_rate:.1f}%")
    
    # Tactic breakdown
    st.subheader("Tactic Breakdown")
    for tactic in st.session_state.dictionaries.keys():
        present_col = f'{tactic}_present'
        if present_col in st.session_state.results_df.columns:
            count = st.session_state.results_df[present_col].sum()
            percentage = (count / total_statements * 100) if total_statements > 0 else 0
            st.progress(percentage / 100, text=f"{tactic}: {count}/{total_statements} ({percentage:.1f}%)")
    
    # Detailed Results
    st.subheader("Detailed Results")
    
    # Filter options
    filter_option = st.selectbox(
        "Filter results",
        ["All statements", "Only statements with matches", "Only statements without matches"]
    )
    
    filtered_df = st.session_state.results_df.copy()
    if filter_option == "Only statements with matches":
        filtered_df = filtered_df[filtered_df[any_tactic_cols].any(axis=1)]
    elif filter_option == "Only statements without matches":
        filtered_df = filtered_df[~filtered_df[any_tactic_cols].any(axis=1)]
    
    # Display results
    for idx, row in filtered_df.iterrows():
        statement_col = st.session_state.statement_col
        has_match = any([row[col] for col in any_tactic_cols if col in row])
        
        # Color code based on matches
        if has_match:
            st.success(f"**ID:** {row.get('ID', row.get('id', idx))}  \n**Statement:** {row[statement_col]}")
        else:
            st.info(f"**ID:** {row.get('ID', row.get('id', idx))}  \n**Statement:** {row[statement_col]}")
        
        # Show classification results
        for tactic in st.session_state.dictionaries.keys():
            present_col = f'{tactic}_present'
            matches_col = f'{tactic}_matches'
            
            if present_col in row and row[present_col]:
                st.markdown(f"- ✅ **{tactic}**: {row[matches_col]}")
            else:
                st.markdown(f"- ❌ **{tactic}**: No matches")
        
        st.divider()

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Marketing Tactic Classifier v1.0")
