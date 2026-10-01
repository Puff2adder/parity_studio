"""Shared light course theme; no chapter prose or financial calculations."""
import streamlit as st

def apply():
    st.markdown('''<style>
    .stApp {background:#FFFFFF!important;color:#142B49!important;color-scheme:light;}
    [data-testid="stHeader"] {background:#FFFFFF!important;}
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {background:#EAF4FF!important;}
    h1,h2,h3,h4 {color:#0756A3!important;}
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stMetric"], .katex {color:#142B49!important;}
    [data-testid="stCaptionContainer"] p,[data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] label,[data-testid="stSidebar"] p {color:#142B49!important;}
    [data-testid="stCaptionContainer"] {opacity:1!important;}
    [data-testid="stTable"] {overflow-x:auto;}
    input,textarea,[data-baseweb="select"]>div,[role="option"],[role="listbox"] {
      background:#FFFFFF!important;color:#142B49!important;-webkit-text-fill-color:#142B49!important;}
    input::placeholder,textarea::placeholder {color:#345575!important;}
    [data-testid="stButton"] button,[data-testid="stDownloadButton"] button {
      background:#EAF4FF!important;color:#142B49!important;border:1px solid #54799B!important;}
    [data-testid="stButton"] button:hover {background:#D7EAFB!important;}
    [data-testid="stExpander"] details {background:#FFFFFF!important;color:#142B49!important;}
    [data-testid="stExpander"] summary {background:#EAF4FF!important;color:#142B49!important;}
    :focus-visible {outline:3px solid #007F86!important;outline-offset:3px;}
    </style>''',unsafe_allow_html=True)

def plot_style(fig):
    fig.update_layout(template='plotly_white',paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',
                      font_color='#142B49',legend=dict(orientation='h',y=-.25),margin=dict(t=45,b=100))
    fig.update_xaxes(gridcolor='#D4E2EF',zerolinecolor='#54799B')
    fig.update_yaxes(gridcolor='#D4E2EF',zerolinecolor='#54799B')
    return fig
