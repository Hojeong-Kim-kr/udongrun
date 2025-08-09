import streamlit as st

st.set_page_config(page_title="우동런 - Our Neighborhood Running Club 세종", page_icon="🏃")

params = st.query_params
raw = params.get("page", "public")
page = raw[0] if isinstance(raw, list) else raw

def header():
    st.markdown("### 🏃 우동런 - Our Neighborhood Running Club 세종")
    st.caption("토요일 08:00 @ 세종 호수공원")

def public_page():
    header()
    st.subheader("퍼블릭 페이지")

    st.write("아래 폼으로 RSVP 제출하세요.")
    with st.form("rsvp_form", clear_on_submit=True):
        name = st.text_input("이름")
        email = st.text_input("이메일")
        pace = st.text_input('예상 페이스 (예: 6.00"/km)')
        submitted = st.form_submit_button("제출")
        if submitted:
            if not name or not email:
                st.error("이름과 이메일을 입력해주세요.")
            else:
                st.success(f"감사합니다, {name}님! 제출 완료 ✅")
                # TODO: 여기서 구글시트/DB 저장 로직 실행

def admin_page():
    header()
    st.subheader("운영진 대시보드")

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    key_from_qs = params.get("key", None)
    if key_from_qs and not st.session_state.is_admin:
        key_from_qs = key_from_qs[0] if isinstance(key_from_qs, list) else key_from_qs
        if str(key_from_qs) == st.secrets.get("ADMIN_TOKEN", ""):
            st.session_state.is_admin = True

    if st.session_state.is_admin:
        st.success("관리자 인증 완료")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
        st.write("여기에 RSVP 관리/체크인/공지 기능을 배치하세요.")
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
