import streamlit as st

from database import get_session
from models import Test

def show_delete_test():
    session = get_session()
    st.markdown(f"<div class='app-header'><div class='app-title'>❌ Delete Test</div><div class='app-subtitle'>Remove test data and associated subjects</div></div>", unsafe_allow_html=True)
    
    tests = session.query(Test).all()
    if not tests:
        st.warning("⚠️ No tests available to delete.")
    else:
        test_options = [f"{t.id} - {t.name} ({t.date})" for t in tests]
        selected = st.selectbox("🔍 Select Test to Delete", test_options)
        selected_test_id = int(selected.split(" - ")[0])
        
        st.warning("⚠️ **Warning**: Deleting this test will also remove all associated subject scores. This action cannot be undone.")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                test = session.get(Test, selected_test_id)
                test_name = test.name
                session.delete(test)
                session.commit()
                st.success(f"✅ Test '{test_name}' and its subjects have been deleted successfully!")
                st.rerun()
