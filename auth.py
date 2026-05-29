"""
auth.py — Login & session management for the platform
"""
import streamlit as st
from config import USERS, PLATFORM_NAME, C, GLOBAL_CSS


def require_auth():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    if st.session_state.get("authenticated"):
        return True
    _render_login()
    st.stop()


def _render_login():
    """Full-screen login page."""
    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, #040c18 0%, #071526 60%, #040c18 100%) !important;
    }}
    [data-testid="stSidebar"] {{ display:none !important; }}
    </style>
    <div style="max-width:420px; margin:60px auto 0 auto; padding:0 8px;">
        <div style="text-align:center; margin-bottom:28px;">
            <div style="font-size:48px; margin-bottom:8px;">🛢️</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:28px; font-weight:700;
                        color:#3aafff; letter-spacing:3px; text-transform:uppercase;">
                {PLATFORM_NAME}
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:9px;
                        color:#1a4a6a; letter-spacing:2px; margin-top:4px;">
                RESERVOIR &amp; DRILLING INTELLIGENCE — SECURE ACCESS
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:

        # ── Login box header ───────────────────────────────────────────────
        st.markdown(
            '<div style="background:#071526;border:1px solid #0d2540;border-radius:14px;'
            'padding:18px 22px 8px;box-shadow:0 20px 60px rgba(0,0,0,0.5);">'
            '<div style="font-family:Share Tech Mono,monospace;font-size:9px;'
            'color:#1a4a6a;text-align:center;margin-bottom:14px;letter-spacing:2px;">'
            'ENTER CREDENTIALS</div></div>',
            unsafe_allow_html=True,
        )

        username = st.text_input("Username", key="_login_user", placeholder="username",
                                  label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="_login_pass",
                                  placeholder="password", label_visibility="collapsed")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if st.button("🔐  LOGIN", use_container_width=True, key="_login_btn"):
            user = USERS.get(username.strip())
            if user and user["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username.strip()
                st.session_state["role"]          = user["role"]
                st.session_state["display_name"]  = user["name"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

        # ── Credits panel — single concatenated string, no nested quotes ──
        credits_html = (
            '<div style="margin-top:20px;'
            'background:linear-gradient(135deg,#071d38 0%,#0a2540 100%);'
            'border:1px solid #1a5a8a;border-radius:10px;'
            'padding:14px 18px 16px;'
            'box-shadow:0 4px 24px rgba(58,175,255,0.10);">'

            # header
            '<div style="font-family:Share Tech Mono,monospace;font-size:8px;'
            'color:#3a6a8a;text-align:center;letter-spacing:2px;'
            'text-transform:uppercase;border-bottom:1px solid #0d2540;'
            'padding-bottom:8px;margin-bottom:12px;">◈ PROJECT TEAM ◈</div>'

            '<div style="display:flex;flex-direction:column;gap:10px;">'

            # Prepared
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<span style="font-family:Share Tech Mono,monospace;font-size:7.5px;'
            'color:#3a8abf;text-transform:uppercase;letter-spacing:1.5px;'
            'white-space:nowrap;min-width:78px;">✦ Prepared</span>'
            '<span style="font-family:Rajdhani,sans-serif;font-size:15px;'
            'font-weight:700;color:#3aafff;letter-spacing:0.5px;'
            'text-shadow:0 0 12px rgba(58,175,255,0.4);">'
            'Zainulabdeen Salah Hasan</span>'
            '</div>'

            # Supervised
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<span style="font-family:Share Tech Mono,monospace;font-size:7.5px;'
            'color:#3a8abf;text-transform:uppercase;letter-spacing:1.5px;'
            'white-space:nowrap;min-width:78px;">✦ Supervised</span>'
            '<span style="font-family:Rajdhani,sans-serif;font-size:15px;'
            'font-weight:700;color:#f5c542;letter-spacing:0.5px;'
            'text-shadow:0 0 12px rgba(245,197,66,0.4);">'
            'Mustafa A. Jaed</span>'
            '</div>'

            # Approved
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<span style="font-family:Share Tech Mono,monospace;font-size:7.5px;'
            'color:#3a8abf;text-transform:uppercase;letter-spacing:1.5px;'
            'white-space:nowrap;min-width:78px;">✦ Approved</span>'
            '<span style="font-family:Rajdhani,sans-serif;font-size:15px;'
            'font-weight:700;color:#2ecc71;letter-spacing:0.5px;'
            'text-shadow:0 0 12px rgba(46,204,113,0.4);">'
            'Firas Nadhim Hasan</span>'
            '</div>'

            '</div></div>'
        )
        st.markdown(credits_html, unsafe_allow_html=True)


def is_admin() -> bool:
    return st.session_state.get("role") in ("admin", "engineer")


def get_role() -> str:
    return st.session_state.get("role", "viewer")


def get_display_name() -> str:
    return st.session_state.get("display_name", "User")


def logout():
    for k in ["authenticated", "username", "role", "display_name"]:
        st.session_state.pop(k, None)
    st.rerun()
