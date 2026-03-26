# Home.py
import streamlit as st
from core.layout import setup_page, sidebar_menu, get_app_menu
import pandas as pd


setup_page(page_title="APP SUGESC", layout="wide", hide_default_nav=True)

# menu lateral estruturado
sidebar_menu(get_app_menu(), use_expanders=True, expanded=False)

st.title("APP SUGESC — Hub Central de Análises")
st.caption("Use o menu lateral para navegar ou clique nos atalhos abaixo.")

st.divider()
st.markdown(
    """
<style>
.home-sections { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 1rem; }
.home-section { flex: 1 1 280px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.1rem 1.3rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
.home-section h4 { margin: 0 0 0.6rem 0; font-weight: 700; font-size: 1rem; }
.home-section ul { margin: 0; padding-left: 1.1rem; }
.home-section li { margin-bottom: 0.35rem; line-height: 1.45; }
.home-section li:last-child { margin-bottom: 0; }
</style>

**Sobre o Aplicativo**

<div class="home-sections">
  <div class="home-section">
    <h4>🏆 MSC e Ranking</h4>
    <ul>
      <li><strong>🥇 Ranking API</strong>: Realiza as análises completas do ranking através dos dados extraídos da API do SICONFI.</li>
      <li><strong>🗓️ Análise MSC Mensal</strong>: Validação da Matriz de Saldos Contábeis conforme as Dimensões D1 do ranking SICONFI.</li>
      <li><strong>📊 Análise MSC x FLEX</strong>: Conciliação entre a MSC e alguns relatórios do FLEX para identificar possíveis divergências de dados.</li>
      <li><strong>🗓️ Análise MSC API Acumulado Mensal</strong>: Consulta à API do SICONFI sobre os dados da Matriz de Saldos Contábeis nas Dimensões D1 do ranking.</li>
      <li><strong>📑 Extratos de Homologações</strong>: Consulta sobre os demonstrativos homologados no portal do SICONFI.</li>
      <li><strong>⚖️ Análise Novas Dimensões</strong>: Comparação do desempenho dos estados em relação às novas verificações do Ranking Siconfi.</li>
      <li><strong>🚨 Acerto de Fontes em Banco</strong>: Permite o acerto dos dados de Ativos F sem Fonte de Recursos na MSC.</li>
      <li><strong>✔️ Conferência entre Matriz e Layout da STN</strong>: Permite realizar a conferência entre a estrutura da Matriz e Layout da STN.</li>
      <li><strong>🔍 Analisar a Tabela de Dimensões do Ranking</strong>: Consulta e analisa a tabela das Dimensões do Ranking obtidas da página de metodologia do ranking.</li>
      <li><strong>🔍 Análise do CO</strong>: Realiza a análise da Informação do CO na Matriz e compara com os dados do SIAFERIO.</li>
    </ul>
  </div>
  <div class="home-section">
    <h4>📊 Dashboards</h4>
    <ul>
      <li><strong>📈 Dashboard RREO</strong>: Visualização dos demonstrativos fiscais do SICONFI com filtros interativos.</li>
    </ul>
    <h4 style="margin-top:1.1rem;">🧮 Análises Carga da LOA</h4>
    <ul>
      <li><strong>📊 Conferência de Saldos de LME</strong>: Análises dos saldos e integridade do Controle de LME.</li>
      <li><strong>🧮 Análise dos TXT de LME</strong>: Tratamento dos arquivos TXT de LME para detectar diferenças após mudanças na Regra de LME.</li>
      <li><strong>✔️ Conferência da Carga da Receita da LOA no Siaferio</strong>: Análises para a conferência da Carga da Receita da LOA no Siaferio, comparando os dados entre o arquivo de importação e os saldos contabilizados no sistema.</li>
    </ul>
  </div>
  <div class="home-section">
    <h4>🧩 Outras Análises</h4>
    <ul>
      <li><strong>🧩 Encerramento de Disponibilidades</strong>: Regras e verificações para processar o encerramento das disponibilidades financeiras por fonte.</li>
      <li><strong>🧾 Análise dos Arquivos SIG</strong>: Página para realizar as análises dos arquivos SIG em relação aos dados do SIAFERIO/Flexvision.</li>
      <li><strong>✅ Conferência do Plano de Contas</strong>: Página voltada para o processo de encerramento, analisa a integridade das contas contábeis e identifica possíveis falhas na configuração do Plano de Contas e suas regras de transferência (casos em que a conta deveria transferir saldo e não está configurada, e vice-versa).</li>
      <li><strong>❌ Conferência dos Programas de Trabalho e os Saldos de RPP</strong>: Página que permite identificar quais Programas de Trabalho possuem saldos nas contas de Restos a Pagar, mas não estão cadastrados nas tabelas de apoio do SIAFERIO.</li>
      <li><strong>⚖️ Conferência Migração de Saldos</strong>: Página destinada à verificação da Transferência Diária, esta ferramenta valida se o balancete de encerramento está em conformidade com o de abertura, respeitando as regras de transferência de cada conta no Plano de Contas.</li>
      <li><strong>🗑️ Análise de PDs Lixo</strong>: Página para realizar as análises das PDs Lixo/Flexvision.</li>
      <li><strong>🔢 Cálculo de Fator de Vencimentos de Boletos</strong>: Página para realizar o cálculo de Fator de Vencimento de Boletos.</li>
    </ul>
    <h4 style="margin-top:1.1rem;">🏦 Manuais</h4>
    <ul>
      <li><strong>🏦 Manuais SUGESC</strong>: Visualização dos Manuais da Superintendência de Gerenciamento dos Sistemas Contábeis (SUGESC) .</li>
    </ul>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Rodapé
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>APP SUGESC — Hub Central de Análises | Desenvolvido pela equipe CISSC/SUGESC/SUBCONT | © {pd.Timestamp.today().year}</small>
</div>
""", unsafe_allow_html=True)
