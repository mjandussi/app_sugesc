# ┌───────────────────────────────────────────────────────────────
# │ pages/08_📚 Manuais.py
# │ Visualização de Manuais de Procedimentos em Markdown
# └───────────────────────────────────────────────────────────────

import streamlit as st
from pathlib import Path
import re
from datetime import datetime
# Importando os arquivos e funções necessárias
from core.layout import setup_page, sidebar_menu, get_app_menu
import pandas as pd
from io import BytesIO
from contextlib import contextmanager
import os 

# Configuração da página
setup_page(page_title="Manuais da SUGESC (SUBCONT)", layout="wide", hide_default_nav=True)

# Menu lateral estruturado
# (Assumindo que estas variáveis e funções estão definidas em 'core.layout' e outras partes do seu projeto)
sections = [(f"Seção {i}", f"## Seção {i} Conteúdo") for i in range(10)]
try:
    sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)
except NameError:
    pass 

# ═══════════════════════════════════════════════════════════════
# Configurações e Utilitários
# ═══════════════════════════════════════════════════════════════

# Diretório de manuais
MANUAIS_DIR = Path(__file__).parent.parent / "manuais"
# Base do diretório do projeto (usada para resolver caminhos absolutos, se necessário)
BASE_DIR = Path(__file__).parent.parent

# Ano atual
CURRENT_YEAR = datetime.now().year
NEXT_YEAR = CURRENT_YEAR + 1

# CSS customizado para melhor visualização (mantido intacto)
st.markdown("""
<style>
    .main {
        background: radial-gradient(circle at top, rgba(59,130,246,.15), rgba(0,0,0,0)) no-repeat fixed;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    .manual-banner {
        background: linear-gradient(120deg, rgba(59,130,246,.25), rgba(147,51,234,.25));
        border: 1px solid rgba(255,255,255,.1);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px rgba(15,23,42,.25);
    }
    .manual-banner h2 {
        margin: 0;
        font-size: 1.4rem;
    }
    .manual-banner__meta {
        display: flex;
        gap: 1.5rem;
        margin-top: .75rem;
        flex-wrap: wrap;
        font-size: .9rem;
        color: rgba(255,255,255,.8);
    }
    .manual-banner__meta span {
        display: block;
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
    }
    .manual-section-card:has(*), .manual-checklist-card:has(*) {
        background: rgba(17, 24, 39, .65);
        border: 1px solid rgba(148,163,184,.25);
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 10px 30px rgba(15,23,42,.35);
        margin-bottom: 1.5rem;
    }
    /* Ocultar containers vazios */
    .manual-section-card:empty, .manual-checklist-card:empty,
    div[data-testid="stMarkdownContainer"]:empty {
        display: none !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .manual-section-card h2, .manual-section-card h3 {
        margin-top: 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: .5rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: .75rem;
        padding-bottom: .75rem;
        border-radius: 999px !important;
        background: rgba(148,163,184,.12);
        color: rgba(255,255,255,.7);
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, rgba(59,130,246,.4), rgba(147,51,234,.4)) !important;
        color: #fff !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {
        background: rgba(15,23,42,.6);
        border: 1px solid rgba(148,163,184,.4);
        border-radius: .75rem;
        box-shadow: 0 12px 25px rgba(2,6,23,.45);
        color: #fff;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 1rem;
        padding: .5rem 1rem;
        background: rgba(15,23,42,.6);
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,.3);
    }
    div[data-testid="stRadio"] label {
        font-weight: 600;
    }
    div[data-testid="stExpander"] {
        border: 1px solid rgba(148,163,184,.3);
        border-radius: .75rem;
        overflow: hidden;
    }
    div[data-testid="stExpander"] > details {
        background: rgba(15,23,42,.4);
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Funções Auxiliares
# ═══════════════════════════════════════════════════════════════

def process_and_display_markdown(md_text, base_manual_dir):
    """
    Processa o texto Markdown, detecta links de imagens no formato [legenda](caminho)
    e os substitui pelo componente st.image(), encapsulado em um expander.
    """
    linhas = md_text.split('\n')
    
    # Expressão regular para encontrar links no formato: [Texto](Caminho)
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    
    for raw_line in linhas:
        match = link_pattern.search(raw_line)
        
        if match:
            # Se for encontrado um link/imagem no formato [Texto](Caminho)
            link_texto = match.group(1).strip()
            link_caminho_relativo = match.group(2).strip()
            
            # Verificar se o link aponta para um arquivo de imagem
            if link_caminho_relativo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                
                # 1. Resolver o caminho absoluto da imagem
                caminho_imagem_abs = (base_manual_dir / link_caminho_relativo).resolve()
                
                # 2. Encapsular a imagem em um expander com o texto do link como título
                # Usamos use_container_width=False para preservar a qualidade do print
                with st.expander(f"🖼️ {link_texto}", expanded=False):
                    if caminho_imagem_abs.exists():
                        # 3. Exibir a imagem
                        st.image(
                            str(caminho_imagem_abs), 
                            caption=link_texto, 
                            use_container_width=False # Não forçar o redimensionamento para preservar a qualidade
                        )
                        # O continue aqui evita que a linha original do Markdown seja exibida
                        continue 
                    else:
                        st.warning(f"❌ Imagem não encontrada: {link_caminho_relativo} (Procurado em: {caminho_imagem_abs})")
                        
            # Se for um link que não é imagem ou se o processamento da imagem falhou
            st.markdown(raw_line, unsafe_allow_html=True) 
            
        else:
            # Linha sem links, exibe o Markdown normal
            st.markdown(raw_line, unsafe_allow_html=True)


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


def find_checklist_sections(md_text):
    """
    Identifica todas as seções (H3) que contenham checklists no formato Markdown (- [ ]) e
    retorna um dicionário {titulo_secao: [ {Etapa, Atividade}, ... ]}.
    """
    pattern = r"(^###\s+.+?$)"
    parts = re.split(pattern, md_text, flags=re.MULTILINE)
    checklists = {}

    if len(parts) == 1:
        return checklists

    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        body = parts[i+1] if (i+1) < len(parts) else ""
        title = heading.lstrip("#").strip()

        if "- [" not in body:
            i += 2
            continue

        current_stage = title
        rows = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            stage_match = re.match(r"^\*\*(.+?)\*\*:?$", line)
            if stage_match:
                current_stage = stage_match.group(1).strip()
                continue

            task_match = re.match(r"^-\s*\[(?: |x|X)\]\s*(.+)$", line)
            if task_match:
                rows.append({
                    "Etapa": current_stage,
                    "Atividade": task_match.group(1).strip()
                })

        i += 2

    return checklists


@contextmanager
def card_container(css_class="manual-section-card"):
    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


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
        checklist_sections = find_checklist_sections(manual_text)
    except Exception as e:
        st.error(f"❌ Erro ao ler o manual: {e}")
        st.stop()

    # Define o diretório base para resolver os caminhos relativos
    manual_base_dir = manual_selecionado.parent 

    info = manual_selecionado.stat()
    last_modified = datetime.fromtimestamp(info.st_mtime).strftime("%d/%m/%Y")
    file_size = info.st_size / 1024

    manual_banner = f"""
    <div class="manual-banner">
        <div>
            <h2>{manual_selecionado.stem}</h2>
            <p style="margin:0.25rem 0 0 0; color: rgba(255,255,255,.85);">Manual exibido abaixo com recursos de navegação por seções ou visualização completa.</p>
        </div>
        <div class="manual-banner__meta">
            <div>
                <small>Última atualização</small>
                <span>{last_modified}</span>
            </div>
            <div>
                <small>Total de seções</small>
                <span>{len(sections)}</span>
            </div>
            <div>
                <small>Tamanho do arquivo</small>
                <span>{file_size:.1f} KB</span>
            </div>
        </div>
    </div>
    """
    st.markdown(manual_banner, unsafe_allow_html=True)

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

                with card_container():
                    st.markdown(f"## {secao_selecionada_idx + 1}. {title}")
                    st.caption(f"Seção {secao_selecionada_idx + 1} de {len(sections)}")

                    # Dividir em subseções
                    subsections = split_subsections(content)

                    # Se houver subseções, usar tabs
                    if len(subsections) > 1:
                        tab_names = [sub_title for sub_title, _ in subsections]
                        tabs = st.tabs(tab_names)

                        for tab, (sub_title, sub_content) in zip(tabs, subsections):
                            with tab:
                                # APLICAR PROCESSAMENTO DE IMAGEM AO CONTEÚDO DA SUBSEÇÃO
                                process_and_display_markdown(sub_content, manual_base_dir)
                    else:
                        # APLICAR PROCESSAMENTO DE IMAGEM AO CONTEÚDO DA SEÇÃO
                        process_and_display_markdown(content, manual_base_dir)

    # Visualização completa
    else:
        with card_container():
            st.markdown("## 📖 Visualização Completa")

            with st.expander("ℹ️ Sobre este modo de visualização", expanded=False):
                st.info("""
                **Modo Manual Completo** exibe todo o conteúdo do documento de uma vez.

                Para uma navegação mais fácil durante apresentações, utilize o modo **Por Seções**.
                """)

            # APLICAR PROCESSAMENTO DE IMAGEM AO CONTEÚDO COMPLETO
            process_and_display_markdown(manual_text, manual_base_dir) # Chamada corrigida

    if checklist_sections:
        with card_container("manual-checklist-card"):
            st.markdown("### ✅ Checklists dos Anexos")
            with st.expander("Opcional: visualizar ou exportar checklists (Anexos)", expanded=False):
                checklist_titles = list(checklist_sections.keys())
                selected_title = st.selectbox(
                    "Selecione o anexo:",
                    options=checklist_titles,
                    format_func=lambda x: x
                )

                selected_rows = checklist_sections[selected_title]
                checklist_df = pd.DataFrame(selected_rows)
                st.dataframe(checklist_df, use_container_width=True, hide_index=True)

                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    checklist_df.to_excel(writer, sheet_name=selected_title[:31], index=False)
                buffer.seek(0)

                st.download_button(
                    "⬇️ Exportar checklist para Excel",
                    data=buffer.getvalue(),
                    file_name=f"{selected_title.replace(' ', '_')}_{CURRENT_YEAR}_{NEXT_YEAR}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{manual_selecionado.stem}"
                )


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)