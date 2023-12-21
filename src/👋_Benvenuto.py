import streamlit as st

st.set_page_config(
    page_title='Conca Future Cup',
    page_icon='👋',
    layout='wide'
)

st.title('👋 Benvenuto')

col1, col2, col3 = st.columns(3)
with col1:
    st.write()
    st.markdown('#### La Conca Future Cup é qui')
    st.image('src/assets/coppa.png', width=200)
    