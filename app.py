import streamlit as st

st.set_page_config(page_title="우동런-우리동네 런 클럽 세종", page_icon="🏃")

params = st.query_params
page = params.get("page", "public")  # public 또는 admin

def header():
    st.markdown("### 🏃 우동런-우리동네 런 클럽 세종")
    st.caption("토요일 08:00 @ 세종 호수공원")

def public_page():
    header()
    st.subheader("퍼블릭 페이지")
    st.write("참가자 안내/RSVP 등을 보여주세요.")

def admin_page():
    header()
    st.subheader("운영진 대시보드")

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    key_from_qs = params.get("key", None)
    if key_from_qs and not st.session_state.is_admin:
        if str(key_from_qs) == st.secrets.get("ADMIN_TOKEN", ""):
            st.session_state.is_admin = True

    if st.session_state.is_admin:
        st.success("관리자 인증 완료")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
        st.write("여기에 RSVP/체크인/공지 기능 배치")
        return

    st.info("관리자 토큰을 입력하세요.")
    with st.form("admin_login"):
        token = st.text_input("관리 토큰", type="password")
        if st.form_submit_button("로그인"):
            if token == st.secrets.get("ADMIN_TOKEN", ""):
                st.session_state.is_admin = True
                st.success("로그인 성공")
                st.rerun()
            else:
                st.error("토큰이 올바르지 않습니다.")

if page == "public":
    public_page()
elif page == "admin":
    admin_page()
else:
    st.error("올바르지 않은 페이지입니다.")
