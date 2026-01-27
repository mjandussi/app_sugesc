# core/auth.py
import os
from pathlib import Path
import streamlit as st

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

if load_dotenv is not None:
    base_dir = Path(__file__).resolve().parents[1]
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path, override=False)


def _read_env_file(env_path: Path) -> dict:
    data = {}
    try:
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    except Exception:
        pass
    return data


def _get_credentials():
    username = os.environ.get("APP_USERNAME")
    password = os.environ.get("APP_PASSWORD")

    if (not username or not password) and hasattr(st, "secrets"):
        try:
            auth = st.secrets.get("auth", {})
            username = username or auth.get("username")
            password = password or auth.get("password")
        except Exception:
            pass

    if not username or not password:
        env_path = Path(__file__).resolve().parents[1] / ".env"
        env_data = _read_env_file(env_path)
        username = username or env_data.get("APP_USERNAME")
        password = password or env_data.get("APP_PASSWORD")

    return username, password


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def require_login(app_name: str = "APP SUGESC") -> None:
    if is_authenticated():
        return

    username, password = _get_credentials()

    if not username or not password:
        st.warning(
            "Login não configurado. Defina APP_USERNAME/APP_PASSWORD no .env "
            "ou st.secrets['auth'] para ativar."
        )
        st.stop()

    st.markdown(
        """
        <style>
        .login-wrap { margin-top: 0.5rem; }
        </style>
        <div class="login-wrap"></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"## 🔐 Login — {app_name}")
    with st.form("login_form", clear_on_submit=False):
        input_user = st.text_input("Usuário")
        input_password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if input_user == username and input_password == password:
            st.session_state["authenticated"] = True
            st.session_state["auth_user"] = input_user
            st.success("Login realizado com sucesso.")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()


def render_logout(label: str = "Sair") -> None:
    if not is_authenticated():
        return

    if st.sidebar.button(label, use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("auth_user", None)
        st.rerun()
