import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="우동런 · Our Neighborhood Running Club", page_icon="🏃")

# ---------- Google Sheets ----------
def get_gsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(st.secrets["SHEET_URL"])

    # 👉 'rsvps' 시트로 강제 연결 (없으면 생성)
    try:
        ws = sh.worksheet("rsvps")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title="rsvps", rows=1000, cols=10)

    # 헤더 없으면 추가
    headers = ws.row_values(1)
    if not headers:
        ws.insert_row(["timestamp", "name", "email", "pace"], 1)

    return ws

def append_rsvp(name, email, pace):
    ws = get_gsheet()
    ws.append_row([datetime.now().isoformat(timespec="seconds"), name, email, pace])

def read_rsvp():
    ws = get_gsheet()
    rows = ws.get_all_records()
    return rows

# ---------- Routing ----------
params = st.query_params
raw = params.get("page", "public")
page = raw[0] if isinstance(raw, list) else raw

def header():
    st.markdown("### 🏃 우동런 · Our Neighborhood Running Club 세종")
    st.caption("매주 토요일 08:00 @ 세종 호수공원")

# ---------- Public ----------
def public_page():
    header()
    st.subheader("퍼블릭 페이지")

    st.write("아래 폼으로 RSVP 제출하세요.")
    with st.form("rsvp_form", clear_on_submit=True):
        name = st.text_input("이름")
        email = st.text_input("이메일")
        pace = st.text_input("예상 페이스 (예: 6.00\"/km)")
        submitted = st.form_submit_button("제출")
        if submitted:
            if not name or not email:
                st.error("이름과 이메일을 입력해주세요.")
            else:
                try:
                    append_rsvp(name, email, pace)
                    st.success(f"감사합니다, {name}님! 제출 완료 ✅")
                except Exception as e:
                    st.error("제출 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                    st.caption(f"(관리자용 디버그: {e})")

# ---------- Admin ----------
def admin_page():
    header()
    st.subheader("운영진 대시보드")

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    # URL로 바로 인증(원치 않으면 제거)
    key_from_qs = params.get("key", None)
    if key_from_qs and not st.session_state.is_admin:
        key_from_qs = key_from_qs[0] if isinstance(key_from_qs, list) else key_from_qs
        if str(key_from_qs) == st.secrets.get("ADMIN_TOKEN", ""):
            st.session_state.is_admin = True

    # 로그인 상태
    if st.session_state.is_admin:
        st.success("관리자 인증 완료")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("로그아웃", use_container_width=True):
                st.session_state.is_admin = False
                st.rerun()
        with col2:
            if st.button("데이터 새로고침", use_container_width=True):
                st.rerun()

        # RSVP 데이터 보기
        st.markdown("#### RSVP 목록")
        try:
            data = read_rsvp()
            if data:
                st.dataframe(data, use_container_width=True, hide_index=True)
            else:
                st.info("아직 RSVP 데이터가 없습니다.")
        except Exception as e:
            st.error("구글시트 연결에 실패했습니다. Secrets와 시트 공유 설정을 확인하세요.")
            st.caption(f"(관리자용 디버그: {e})")

        # 간단한 상태 토글 예시(필요 시 시트/kv 저장 가능)
        st.markdown("#### 이벤트 상태")
        status = st.selectbox("상태", ["ON", "OFF"], index=0)
        st.caption("※ 저장 기능을 붙일 수 있어요. 지금은 UI만 동작.")

        return

    # 미인증 → 로그인 폼
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

# ---------- Entry ----------
if page == "public":
    public_page()
elif page == "admin":
    admin_page()
else:
    st.error("올바르지 않은 페이지입니다.")
