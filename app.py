import streamlit as st
from millify import millify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from kneed import KneeLocator
from scipy.stats import linregress

# Page config
st.set_page_config(
    page_title='Knee Finder',
    layout='centered',
    page_icon='📐',
    initial_sidebar_state='expanded'
)

# Modern CSS styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main container spacing */
    .block-container {
        padding: 2rem 1rem 4rem;
        max-width: 800px;
    }

    /* App header */
    .app-header {
        margin-bottom: 1.5rem;
    }
    .app-header h1 {
        color: #1E293B;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    .app-header p {
        color: #64748B;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.5;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1rem;
    }

    /* Info box for sample data */
    .sample-notice {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0 1rem 0;
        font-size: 0.85rem;
        color: #92400E;
    }

    /* Metric card styling */
    [data-testid="stMetric"] label {
        color: #64748B !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-size: 2rem !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F1F5F9;
        border-radius: 8px;
        font-weight: 500;
    }

    /* Footer */
    .app-footer {
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        font-size: 0.8rem;
    }
    .app-footer a {
        color: #64748B;
        text-decoration: none;
        margin: 0 1rem;
        transition: color 0.2s;
    }
    .app-footer a:hover {
        color: #0F766E;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
<div class="app-header">
    <h1>Knee Finder</h1>
    <p>Identify the knee/elbow point of a curved line. The knee is the point with maximum curvature - useful for finding optimal thresholds in data analysis.</p>
</div>
""", unsafe_allow_html=True)


def is_concave(points):
    """Determine if curve is concave or convex based on acceleration."""
    data = np.array(points, dtype=float)
    velocity = np.diff(data)
    acceleration = np.diff(velocity)
    return np.mean(acceleration) < 0


try:
    # Sidebar - Datal3x branding
    st.sidebar.markdown("""
    <a href="https://datal3x.github.io" target="_blank" style="text-decoration: none;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" width="180" height="45" style="margin-bottom: 1rem;">
            <circle cx="25" cy="25" r="22" fill="#000000"/>
            <polyline points="8,25 12,25 12,20 16,20 16,25 20,25 20,15 24,15 24,25 28,25 28,18 32,18 32,25 36,25 36,30 40,30 40,25 42,25" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"/>
            <text x="55" y="33" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="bold" fill="#000000">DATAL3x</text>
        </svg>
    </a>
    """, unsafe_allow_html=True)

    # Sidebar - Data Import
    st.sidebar.markdown("### Data Import")

    flavor = st.sidebar.radio('File format', ['csv', 'tsv'], horizontal=True)
    uploaded_file = st.sidebar.file_uploader("Upload your data", type=flavor)

    if uploaded_file is not None:
        sep = ',' if flavor == 'csv' else '\t'
        data = pd.read_csv(uploaded_file, sep=sep, on_bad_lines="skip")
    else:
        st.sidebar.markdown("""
        <div class="sample-notice">Using sample dataset</div>
        """, unsafe_allow_html=True)
        data = pd.read_csv('sample.tsv', sep='\t', on_bad_lines="skip")

    # Column selection
    st.sidebar.markdown("### Column Selection")
    cat_features = st.sidebar.multiselect(
        'Select column to analyze',
        options=list(data.columns),
        default=list(data.columns)
    )

    if len(cat_features) == 0:
        st.warning('Please select a column to analyze.')
        st.stop()

    df = data[cat_features].dropna()
    st.sidebar.caption(f'**{len(df):,}** rows')

    if df[cat_features[0]].dtypes not in ['int64', 'float64']:
        st.warning('Please select a numeric column.')
        st.stop()

    # Prepare data
    _y = df[cat_features[0]]
    _x = np.arange(1, len(df) + 1)
    direction = linregress(_x, _y).slope

    # Settings
    with st.expander("Settings", expanded=False):
        st.markdown("**Sensitivity** controls how aggressively knees are detected.")
        st.caption("Smaller values detect knees quicker; larger values are more conservative.")
        _s = st.slider("Sensitivity", min_value=0.01, max_value=10.0, value=1.0, step=0.01)

    # Find knee
    _kneeLocator = KneeLocator(
        _x, _y, S=_s,
        curve="concave" if is_concave(_y) else "convex",
        direction="increasing" if direction > 0 else "decreasing"
    )

    if _kneeLocator.knee_y is None:
        st.warning('No knee found. Try adjusting the sensitivity value.')
        st.stop()

    _knee_x = _kneeLocator.knee
    _knee_y = _kneeLocator.knee_y
    curve_type = "Concave" if is_concave(_y) else "Convex"
    direction_type = "Increasing" if direction > 0 else "Decreasing"

    # Plot
    fig = px.line(x=_x, y=_y, labels={'x': 'Index', 'y': cat_features[0]})
    fig.update_traces(line_color='#14B8A6', line_width=2)
    fig.add_trace(
        go.Scatter(
            x=[_knee_x],
            y=[_knee_y],
            mode="markers",
            marker=dict(
                color="#DC2626",
                size=14,
                symbol="x",
                line=dict(width=2, color="white"),
            ),
            name="Knee Point",
        )
    )
    fig.update_layout(
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='#F8FAFC',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(gridcolor='#E2E8F0', zerolinecolor='#E2E8F0'),
        yaxis=dict(gridcolor='#E2E8F0', zerolinecolor='#E2E8F0'),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Results
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(label="Knee Point", value=millify(_knee_y))
    with col2:
        # Download button
        result_df = pd.DataFrame({
            'knee_x': [_knee_x],
            'knee_y': [_knee_y],
            'curve_type': [curve_type],
            'direction': [direction_type],
            'sensitivity': [_s]
        })
        csv = result_df.to_csv(index=False)
        st.download_button(
            label="Download Result",
            data=csv,
            file_name="knee_result.csv",
            mime="text/csv",
        )

    # Details
    with st.expander("Details"):
        st.markdown(f"""
        | Property | Value |
        |----------|-------|
        | Curve Type | **{curve_type}** |
        | Direction | **{direction_type}** |
        | Knee X Position | **{_knee_x}** |
        | Knee Y Value | **{_knee_y:.4f}** |
        | Sensitivity Used | **{_s}** |
        """)

except Exception as e:
    print("An Error Occurred:", e)
    st.error(f"An error occurred: {e}")
    st.stop()

# Footer
st.markdown("""
<div class="app-footer">
    <a href="https://datal3x.github.io" target="_blank">DATAL3x</a>
    <a href="https://www.youtube.com/@datal3x" target="_blank">Tutorials</a>
</div>
""", unsafe_allow_html=True)
