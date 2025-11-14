# ┌───────────────────────────────────────────────────────────────
# │ pages/08_📚 Manuais.py
# │ Visualização de Manuais de Procedimentos em Markdown
# └───────────────────────────────────────────────────────────────

import streamlit as st
from pathlib import Path
import re
from datetime import datetime
from core.layout import setup_page, sidebar_menu, get_app_menu
import pandas as pd
from io import BytesIO

# Configuração da página
setup_page(page_title="Manuais da SUGESC (SUBCONT)", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

# ═══════════════════════════════════════════════════════════════
# Configurações e Utilitários
# ═══════════════════════════════════════════════════════════════

# Diretório de manuais
MANUAIS_DIR = Path(__file__).parent.parent / "manuais"

# Ano atual
CURRENT_YEAR = datetime.now().year
NEXT_YEAR = CURRENT_YEAR + 1

# CSS customizado para melhor visualização
st.markdown("""
<style>
    /* Cards informativos */
    .info-card {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .success-card {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .warning-card {
        background: rgba(251, 146, 60, 0.1);
        border-left: 4px solid #fb923c;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Melhorar visualização de listas */
    .stMarkdown ul {
        margin-left: 1.5rem;
    }

    .stMarkdown ol {
        margin-left: 1.5rem;
    }

    /* Melhorar visualização de código */
    .stMarkdown code {
        background: rgba(0, 0, 0, 0.05);
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Funções Auxiliares
# ═══════════════════════════════════════════════════════════════

def listar_manuais():
    """Lista todos os arquivos .md na pasta manuais."""
    if not MANUAIS_DIR.exists():
        return []
    return sorted(MANUAIS_DIR.glob("*.md"))


def split_markdown_sections(md_text, skip_h2=0):
    """Divide o markdown em seções de nível H2 (##)."""
    pattern = r"(^##\s+.+?$)"
    parts = re.split(pattern, md_text, flags=re.MULTILINE)
    sections = []

    if len(parts) == 1:
        sections.append(("Manual", md_text))
        return sections

    i = 1
    h2_count = 0
    while i < len(parts):
        heading = parts[i].strip()
        content = parts[i+1] if (i+1) < len(parts) else ""
        title = heading.lstrip("#").strip()
        h2_count += 1
        if h2_count > skip_h2:
            sections.append((title, heading + "\n" + content))
        i += 2

    return sections


def split_subsections(content):
    """Divide o conteúdo de uma seção em subseções baseadas em H3 (###)."""
    pattern = r"(^###\s+.+?$)"
    parts = re.split(pattern, content, flags=re.MULTILINE)
    subsections = []

    if len(parts) == 1:
        return [("Conteúdo", content)]

    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        subcontent = parts[i+1] if (i+1) < len(parts) else ""
        subtitle = heading.lstrip("#").strip()
        subsections.append((subtitle, heading + "\n" + subcontent))
        i += 2

    return subsections


def extract_checklist_from_manual(md_text, section_title="Anexo D - Checklist Cronograma SATI 2025/2026"):
    """
    Procura pelo checklist específico no manual e retorna uma lista de dicts com etapa e atividade.
    Isso permite disponibilizar os itens em tabela e exportá-los em formatos como Excel.
    """
    pattern = rf"###\s+{re.escape(section_title)}\s*(.*?)(?=^###\s+|\Z)"
    match = re.search(pattern, md_text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return []

    section_body = match.group(1).strip()
    current_stage = None
    checklist_rows = []

    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        stage_match = re.match(r"^\*\*(.+?)\*\*$", line)
        if stage_match:
            current_stage = stage_match.group(1).strip()
            continue

        task_match = re.match(r"^-\s*\[(?: |x|X)\]\s*(.+)$", line)
        if task_match and current_stage:
            checklist_rows.append({
                "Etapa": current_stage,
                "Atividade": task_match.group(1).strip()
            })

    return checklist_rows


# ═══════════════════════════════════════════════════════════════
# Interface Principal
# ═══════════════════════════════════════════════════════════════

st.title("🏦 Manuais da SUGESC (SUBCONT)")
st.markdown("Documentação técnica e guias de procedimentos do sistema")
st.markdown("---")

# Verificar se existe a pasta de manuais
if not MANUAIS_DIR.exists():
    st.error(f"❌ Diretório de manuais não encontrado: `{MANUAIS_DIR}`")
    st.info("💡 Crie a pasta `manuais/` na raiz do projeto e adicione arquivos `.md`")
    st.stop()

# Listar manuais disponíveis
manuais = listar_manuais()

if not manuais:
    st.warning("⚠️ Nenhum manual encontrado na pasta `manuais/`")
    st.info("""
    💡 **Como adicionar manuais:**
    1. Crie arquivos `.md` na pasta `manuais/`
    2. Use formatação Markdown padrão
    3. Use `## Título` para seções principais
    4. Use `### Subtítulo` para subseções
    """)
    st.stop()

# Seletor de manual
st.subheader("📖 Selecione um Manual")

manual_selecionado = st.selectbox(
    "Manual:",
    options=manuais,
    format_func=lambda x: x.stem,
    label_visibility="collapsed"
)

if manual_selecionado:
    # Ler conteúdo do manual
    try:
        manual_text = manual_selecionado.read_text(encoding="utf-8")
        sections = split_markdown_sections(manual_text)
        checklist_rows = extract_checklist_from_manual(manual_text)
    except Exception as e:
        st.error(f"❌ Erro ao ler o manual: {e}")
        st.stop()

    st.markdown("---")

    # Informações do manual
    col1, col2, col3 = st.columns([70, 10, 20])
    with col1:
        st.metric("📄 Arquivo", manual_selecionado.name)
    with col2:
        st.metric("📊 Seções", len(sections))
    with col3:
        st.metric("📅 Ano", f"{CURRENT_YEAR}/{NEXT_YEAR}")

    if checklist_rows:
        st.markdown("### 📋 Checklist Cronograma SATI")
        with st.expander("Visualizar e exportar checklist (Anexo D)", expanded=False):
            checklist_df = pd.DataFrame(checklist_rows)
            st.dataframe(checklist_df, use_container_width=True, hide_index=True)

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                checklist_df.to_excel(writer, sheet_name="Checklist SATI", index=False)
            buffer.seek(0)

            st.download_button(
                "⬇️ Exportar checklist para Excel",
                data=buffer.getvalue(),
                file_name=f"Checklist_SATI_{CURRENT_YEAR}_{NEXT_YEAR}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.markdown("---")

    # Opções de visualização
    modo_vis = st.radio(
        "Modo de visualização:",
        ["📑 Por Seções", "📖 Manual Completo"],
        horizontal=True
    )

    st.markdown("---")

    # Visualização por seções
    if modo_vis == "📑 Por Seções":
        if not sections:
            st.warning("⚠️ Nenhuma seção encontrada no manual.")
        else:
            # Criar selectbox para navegação entre seções
            secoes_opcoes = [f"{i+1}. {title}" for i, (title, _) in enumerate(sections)]

            secao_selecionada_idx = st.selectbox(
                "Selecione uma seção:",
                options=range(len(secoes_opcoes)),
                format_func=lambda x: secoes_opcoes[x]
            )

            # Exibir seção selecionada
            if secao_selecionada_idx is not None:
                title, content = sections[secao_selecionada_idx]

                st.markdown(f"## {secao_selecionada_idx + 1}. {title}")
                st.caption(f"Seção {secao_selecionada_idx + 1} de {len(sections)}")

                st.markdown("---")

                # Dividir em subseções
                subsections = split_subsections(content)

                # Se houver subseções, usar tabs
                if len(subsections) > 1:
                    tab_names = [sub_title for sub_title, _ in subsections]
                    tabs = st.tabs(tab_names)

                    for tab, (sub_title, sub_content) in zip(tabs, subsections):
                        with tab:
                            st.markdown(sub_content, unsafe_allow_html=True)
                else:
                    st.markdown(content, unsafe_allow_html=True)

    # Visualização completa
    else:
        st.markdown("## 📖 Visualização Completa")

        with st.expander("ℹ️ Sobre este modo de visualização", expanded=False):
            st.info("""
            **Modo Manual Completo** exibe todo o conteúdo do documento de uma vez.

            Para uma navegação mais fácil durante apresentações, utilize o modo **Por Seções**.
            """)

        #st.markdown("---")
        st.markdown(manual_text, unsafe_allow_html=True)


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
