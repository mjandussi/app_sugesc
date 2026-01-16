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
# Funções Auxiliares DE EXPORTAÇÃO (NOVAS)
# ═══════════════════════════════════════════════════════════════

def to_excel_buffer(df: pd.DataFrame, sheet_name: str = 'Dados'):
    """
    Converte um Pandas DataFrame para um buffer BytesIO no formato XLSX.
    Retorna o buffer no início para o download.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Garante que o nome da aba não exceda 31 caracteres
        sheet_name_safe = sheet_name[:31] 
        df.to_excel(writer, sheet_name=sheet_name_safe, index=False)
    buffer.seek(0)
    return buffer

def download_data_as_xlsx(df: pd.DataFrame, file_name: str, button_label: str = "⬇️ Exportar para Excel"):
    """
    Exibe um botão de download para exportar um DataFrame como XLSX.
    """
    file_name_safe = file_name if file_name.lower().endswith(".xlsx") else f"{file_name}.xlsx"
    excel_buffer = to_excel_buffer(df, sheet_name=file_name_safe.replace(".xlsx", "")[:31])
    
    st.download_button(
        label=button_label,
        data=excel_buffer.getvalue(),
        file_name=file_name_safe,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"download_xlsx_{file_name_safe.replace('.', '_')}" 
    )

# --- Geradores de Dados de Exemplo (Simulação) ---

def gerar_df_bloqueios_siaferio():
    """Gera um DataFrame com a tabela de bloqueios (exemplo do usuário)."""
    data = {
        'Etapa': ['Antes da Virada', 'Antes da Virada', 'Após a Virada', 'Após a Virada'],
        'Contexto': ['Banco de Abertura', 'Banco de Abertura', 'Banco de Encerramento', 'Banco de Abertura'],
        'Ação': [
            'Liberar Funcionalidades de Configuração e Órgão Central', 
            'Liberar Funcionalidades de Visualização/Relatórios', 
            'Bloqueia Pagamentos/Execução Financeira', 
            'Bloqueia Itens de Cadastro para Encerramento (até inscrição RP)'
        ],
        'Observação': [
            'Usuários admins e centrais (SUBCONT/TESOURO)', 
            'Para consulta', 
            'Pagamentos seguem a data corrente (Banco de Abertura)', 
            'Itens configurados para cadastro no Banco de Encerramento'
        ]
    }
    return pd.DataFrame(data)

# Mapeamento: O 'path' do link no MD é a chave, o gerador de DataFrame é o valor.
EXPORTABLE_DATA_SOURCES = {
    "DATA_BLOQUEIOS_SIAFERIO": gerar_df_bloqueios_siaferio,
    # Adicione outros mapeamentos de dados aqui, se necessário.
}

# ═══════════════════════════════════════════════════════════════
# Funções Auxiliares EXISTENTES (MODIFICADA)
# ═══════════════════════════════════════════════════════════════

# A função agora recebe um novo argumento: exportable_data_map
def process_and_display_markdown(md_text, base_manual_dir, exportable_data_map):
    """
    Processa o texto Markdown, detecta links de imagens e exportação de dados, 
    substituindo-os por st.expander apropriados.
    """
    linhas = md_text.split('\n')
    
    # Expressão regular para encontrar links no formato: [Texto](Caminho)
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    
    for raw_line in linhas:
        match = link_pattern.search(raw_line)
        
        if match:
            link_texto = match.group(1).strip()
            link_caminho_relativo = match.group(2).strip()

            # -----------------------------------------------------------------
            # Lógica para Exportação de Dados (XLSX)
            # -----------------------------------------------------------------
            if link_caminho_relativo in exportable_data_map:
                data_generator = exportable_data_map[link_caminho_relativo]
                
                # Encapsula a exportação em um Expander
                with st.expander(f"📊 {link_texto} (Exportar para Excel)", expanded=False):
                    try:
                        df_to_export = data_generator() # Chama a função para gerar o DF
                        
                        st.info(f"O arquivo Excel **'{link_texto}'** contém {len(df_to_export)} linhas. Visualize e baixe abaixo.")
                        
                        # Mostra um preview do DataFrame
                        st.dataframe(df_to_export, use_container_width=True, hide_index=True)

                        # Chamar a função de download
                        download_data_as_xlsx(
                            df=df_to_export,
                            file_name=f"{link_texto.replace(' ', '_')}_{CURRENT_YEAR}.xlsx",
                            button_label=f"⬇️ Baixar {link_texto}.xlsx"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar dados para exportação '{link_caminho_relativo}': {e}")
                
                continue # Evita que o link cru seja exibido no Markdown

            # -----------------------------------------------------------------
            # Lógica Existente para Imagens (.png, .jpg, etc.)
            # -----------------------------------------------------------------
            elif link_caminho_relativo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                
                # 1. Resolver o caminho absoluto da imagem
                caminho_imagem_abs = (base_manual_dir / link_caminho_relativo).resolve()
                
                # 2. Encapsular a imagem em um expander com o texto do link como título
                with st.expander(f"🖼️ {link_texto}", expanded=False):
                    if caminho_imagem_abs.exists():
                        # 3. Exibir a imagem
                        st.image(
                            str(caminho_imagem_abs), 
                            caption=link_texto, 
                            use_container_width=False
                        )
                        continue # O continue aqui evita que a linha original do Markdown seja exibida
                    else:
                        st.warning(f"❌ Imagem não encontrada: {link_caminho_relativo} (Procurado em: {caminho_imagem_abs})")
                        
            # -----------------------------------------------------------------
            # Lógica para Outros Links
            # -----------------------------------------------------------------
            # Se for um link que não é imagem, nem exportação de dados, exibe a linha original do Markdown
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
    retorna um dicionário {titulo_secao: [ {Anexo/Manual, Etapa, Atividade}, ... ]}.
    """
    # Divide o manual por títulos H3
    pattern = r"(^###\s+.+?$)"
    parts = re.split(pattern, md_text, flags=re.MULTILINE)
    checklists = {}

    if len(parts) == 1:
        return checklists

    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        body = parts[i+1] if (i+1) < len(parts) else ""
        title = heading.lstrip("#").strip() # Título H3 principal (Ex: "Bloqueios Funcionalidades Usuários...")

        if "- [" not in body:
            i += 2
            continue

        # current_stage guarda o título em negrito (**...**) ou o título H3 se não houver **
        current_stage = title 
        rows = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # 1. Lógica para capturar as etapas em negrito: **Banco de Abertura**
            # TORNANDO ESTE REGEX MAIS TOLERANTE A ESPAÇOS E CARACTERES NO FINAL DA LINHA
            stage_match = re.match(r"^\s*\*\*(.+?)\*\*\s*:?\s*$", line)
            if stage_match:
                current_stage = stage_match.group(1).strip()
                continue

            # 2. Lógica para capturar o item do checklist: - [ ] Alterar Credor Genérico
            task_match = re.match(r"^-\s*\[(?: |x|X)\]\s*(.+)$", line)
            if task_match:
                # ADICIONANDO A TERCEIRA INFORMAÇÃO: O título da seção (Anexo/Manual)
                rows.append({
                    "Anexo/Manual": title, 
                    "Etapa": current_stage,
                    "Atividade": task_match.group(1).strip()
                })

        # Somente adiciona se houver linhas
        if rows:
             checklists[title] = rows

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
    
    **NOVO: Adicione exportação de dados com links:**
    - `[Título do Relatório](DATA_ID_DA_FONTE)`
    - O `DATA_ID_DA_FONTE` deve ser mapeado na variável `EXPORTABLE_DATA_SOURCES`.
    """)
    st.stop()

# Seletor de manual
st.markdown("# Selecione um Manual:")
st.subheader("Opções:")

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
            st.markdown("# Selecione uma seção:")
            secao_selecionada_idx = st.selectbox(
                "Opções:",
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
                                # APLICAR PROCESSAMENTO DE IMAGEM/EXPORTAÇÃO AO CONTEÚDO DA SUBSEÇÃO
                                process_and_display_markdown(sub_content, manual_base_dir, EXPORTABLE_DATA_SOURCES)
                    else:
                        # APLICAR PROCESSAMENTO DE IMAGEM/EXPORTAÇÃO AO CONTEÚDO DA SEÇÃO
                        process_and_display_markdown(content, manual_base_dir, EXPORTABLE_DATA_SOURCES)

    # Visualização completa
    else:
        with card_container():
            st.markdown("## 📖 Visualização Completa")

            with st.expander("ℹ️ Sobre este modo de visualização", expanded=False):
                st.info("""
                **Modo Manual Completo** exibe todo o conteúdo do documento de uma vez.

                Para uma navegação mais fácil durante apresentações, utilize o modo **Por Seções**.
                """)

            # APLICAR PROCESSAMENTO DE IMAGEM/EXPORTAÇÃO AO CONTEÚDO COMPLETO
            process_and_display_markdown(manual_text, manual_base_dir, EXPORTABLE_DATA_SOURCES)

    # ═══════════════════════════════════════════════════════════════
    # Bloco de Checklist (AJUSTADO PARA USAR NOVAS FUNÇÕES)
    # ═══════════════════════════════════════════════════════════════
    if checklist_sections:
        with card_container("manual-checklist-card"):
            st.markdown("### ✅ Itens do Manual que podem ser Exportados")
            # Agora este expander apenas gerencia a seleção
            with st.expander("Opcional: visualizar ou exportar dados", expanded=False):
                checklist_titles = list(checklist_sections.keys())
                selected_title = st.selectbox(
                    "Selecione o dado a ser analisado:",
                    options=checklist_titles,
                    format_func=lambda x: x
                )

                selected_rows = checklist_sections[selected_title]
                checklist_df = pd.DataFrame(selected_rows)
                st.dataframe(checklist_df, use_container_width=True, hide_index=True)

                # Novo Expander para o Download (consistente com a abordagem de links)
                with st.expander("📥 Exportar Dados para Excel", expanded=False):
                    file_name = f"{selected_title.replace(' ', '_')}_Checklist_{CURRENT_YEAR}_{NEXT_YEAR}"
                    
                    download_data_as_xlsx(
                        df=checklist_df, 
                        file_name=file_name,
                        button_label=f"⬇️ Baixar {selected_title} Dados.xlsx ({len(checklist_df)} itens)"
                    )


# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)