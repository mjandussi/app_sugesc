# Manual de Carga do Orçamento – Início do Exercício Subsequente

---

## Introdução e Visão Geral

### Contexto do Processo

No final do Exercício Corrente (dezembro), a **SEPLAG** informa sobre a publicação de um Decreto que dispõe sobre a execução antecipada do orçamento anual do Poder Executivo para o exercício subsequente.

Com isso, são enviados por e-mail para a **SUGESC**:
1. As tabelas de apoio;
2. A regra de LME (anexos I, II e VI);
3. A carga de antecipação da LOA.

**Fluxo de Trabalho:**
Após a realização dos testes no ambiente de homologação da SEPLAG e a devida validação por parte da equipe responsável, é solicitado que os arquivos sejam importados no ambiente de Produção.

> **Nota:** É fundamental observar rigorosamente a ordem e sequência dos arquivos durante a importação.

---

## Passo 1: Importação das Tabelas de Apoio

### Procedimentos de Importação

Para iniciar a carga, o primeiro passo é importar as tabelas de apoio, respeitando estritamente a sequência de arquivos fornecida.

**Caminho no SIAFE-Rio:**
`Administração > Migração de Dados > Importar Planejamento > Importar`

[Tela de Importação de Planejamento](../imagens/Manual_Carga_Orcamento/tela_importar_planejamento.png)

**Instruções:**
1. Ao clicar em **Importar**, selecione o tipo de arquivo correspondente (veja a lista abaixo).
2. Clique em **Escolher arquivo** para localizar o arquivo TXT salvo em seu computador.
3. Confirme a importação.

> **Obs.:** Importe cada arquivo separadamente, escolhendo o tipo de arquivo conforme o nome do arquivo TXT.

### Ordem de Importação (Checklist)

Abaixo está a ordem obrigatória. Você pode baixar esta lista em Excel para controle:

[Baixar Lista de Ordem de Importação](DATA_ORDEM_IMPORTACAO_TXT)

**Sequência de Importação:**

- [ ] 1 - Poder
- [ ] 2 - Órgão
- [ ] 3 - Função
- [ ] 4 – Subfunção
- [ ] 5 – Grupo de Gasto
- [ ] 6 – Unidade Orçamentária
- [ ] 7 – Tipo de Área Geográfica
- [ ] 8 - Área Geográfica
- [ ] 9 – Identificador de Uso
- [ ] 10 – Natureza de Receita
- [ ] 11 – Categoria de Despesa
- [ ] 12 – Grupo de Despesa
- [ ] 13 – Modalidade de Aplicação
- [ ] 14 – Elemento de Despesa
- [ ] 15 – Natureza de Despesa
- [ ] 16 – Fonte (Fontes STN)
- [ ] 17 - Marcador de Fonte (Fontes RJ)
- [ ] 18 – Detalhamento de Fonte (Repete o arquivo de Fontes RJ)
- [ ] 19 – Esfera
- [ ] 20 – Programa
- [ ] 21 – Ação

**Verificação de Sucesso:**
No sistema, os arquivos importados serão exibidos na grid de histórico. A ordem visual é inversa (o último importado aparece no topo).

[Grid de Histórico de Importação](../imagens/Manual_Carga_Orcamento/grid_historico_importacao.png)

### Configuração de Tipo de Ação (Pré-requisito)

Antes da importação dos arquivos, verificar no sistema se o **Tipo de Ação (configuração)** está cadastrado. A falta dessas informações ocasionará erro na importação do arquivo de ações.

**Caminho:** `Apoio > Planejamento > Tipo de Ação (configuração)`

Caso não tenha, insira os seguintes dados:

| Tipo de Ação | Valor - Configuração |
| :--- | :--- |
| Operação especial | 0 |
| Projeto | 1,3,5,7 |
| Atividade | 2,4,6,8 |
| Reserva | 9 |

[Tela Configuração Tipo de Ação](../imagens/Manual_Carga_Orcamento/configuracao_tipo_acao.png)

---

## Passo 2: Regras de LME

### Importação dos Arquivos XLS

O segundo passo é importar os arquivos no formato **XLS** (layout estabelecido) da regra de LME.

Atualmente a SEPLAG encaminha 3 arquivos de LME principais:
* **Anexo I**: Pessoal
* **Anexo II**: Despesas Obrigatórias
* **Anexo VI**: Serviço de Utilidade Pública

> **Notas sobre LME:**
> * LME III: Tudo que não se enquadra nas demais regras.
> * LME IV: Demais poderes.
> * LME V: Sem uso.

**Procedimento:**
1. Caminho: `Importar Planejamento > Importar`.
2. Selecionar no rol: **Regra da Enquadramento LME**.
3. Escolher o arquivo XLS correspondente.

[Tela Importação LME](../imagens/Manual_Carga_Orcamento/importacao_lme.png)

**Requisitos do Arquivo:**
* Formato obrigatório: **.XLS**
* Respeitar rigorosamente os **nomes das colunas** (Exportar "Layout do Arquivo" na tela do sistema para modelo).
* Realizar uma importação individual para cada arquivo (I, II e VI).

**Ordem Recomendada:**
- [ ] Importar Anexo I (Pessoal)
- [ ] Importar Anexo II (Despesas Obrigatórias)
- [ ] Importar Anexo VI (Serviço de Utilidade Pública)

**Validação:**
Para visualizar a regra importada: `Apoio > Execução > Regra de Enquadramento da LME`.

[Visualização Regra LME](../imagens/Manual_Carga_Orcamento/visualizacao_lme.png)

---

## Passo 3: Carga da Despesa (LOA)

### Parte A: Importar Metas Financeiras

No início do exercício (janeiro), são importadas as cargas de antecipações orçamentárias. A SEPLAG envia os arquivos contendo as informações de despesa e receita prevista.

**Procedimento:**
1. Caminho: `Administração > Migração de Dados > Importar Planejamento > Importar`.
2. Selecionar a opção: **LOA – Metas Financeiras**.
3. Escolher o arquivo e confirmar.

[Seleção Metas Financeiras](../imagens/Manual_Carga_Orcamento/select_metas_financeiras.png)

> **Atenção - Erro Conhecido (Parâmetro 77):**
> Em 2024, houve erro na importação associado ao **Parâmetro de Sistema 77**.
> * **Erro:** Código de Órgão configurado como '2'.
> * **Solução:** Alterar o valor do Órgão para **'5'**.
> * **Caminho:** `Administração > Configuração > Parâmetros de Sistema`.

- [ ] Verificar Parâmetro 77 antes da importação
- [ ] Importar Arquivo LOA - Metas Financeiras

### Parte B: Gerar Nota de Dotação

Após importar as metas, é necessário gerar as Notas de Dotação. A SEPLAG deve fornecer os dados da Lei e Datas para este passo.

**Caminho:** `Execução > Execução Orçamentária > Nota de Dotação > Importar Lei Orçamentária`

**Dados para Preenchimento (Exemplo Base):**
* **Data Emissão:** 01/01/2025
* **Observação:** Antecipação 01 (ou conforme arquivo)
* **Número da Lei:** PLOA 4199 (ou Lei atualizada)
* **Data da Lei:** 30/09/2024 (ou data D.O.)
* **Tipo de Importação:** Selecionar conforme arquivo (Antecipação, Definitiva ou Cancelamento).

[Tela Importar Lei Orçamentária](../imagens/Manual_Carga_Orcamento/importar_lei_orcamentaria_despesa.png)

**Ação Final:**
1. Preencha os dados.
2. Selecione as Unidades Gestoras para o lado direito.
3. Clique em **Importar** e **NÃO saia da tela** até a conclusão.

- [ ] Gerar Notas de Dotação (Antecipação/Definitiva)

---

## Passo 4: Carga da Receita Prevista

### Importação e Geração

O processo de receita segue lógica similar ao da despesa.

**1. Importação do Arquivo:**
* **Caminho:** `Administração > Migração de Dados > Importar Planejamento > Importar`.
* **Entidade:** Selecionar **Receita**.
* **Arquivo:** Escolher arquivo enviado pela SEPLAG.

**2. Geração do Documento:**
* **Caminho:** `Execução > Execução Orçamentária > Receita Prevista > Importar Lei Orçamentária`.

**Preenchimento:**
* **Data Emissão:** 01/01/2025 (Exemplo)
* **Observação:** Carga de Receita Prevista LOA 2025

[Tela Importar Receita](../imagens/Manual_Carga_Orcamento/importar_receita_tela.png)

**Ação Final:**
1. Selecione as Unidades Gestoras.
2. Clique em **Importar** ou **Gerar Previsão do Lote**.
3. Verifique a criação do documento no menu `Receita Prevista`.

- [ ] Importar Arquivo de Receita
- [ ] Gerar Documento de Receita Prevista

---

## Anexos e Solução de Problemas

### Erros Comuns

**Erro ao cadastrar Natureza de Despesa:**
* **Causa:** Falta da Modalidade 00.
* **Solução:** Cadastrar a Modalidade 00 nas tabelas de apoio antes de prosseguir.

**Tipos de Importação (Menu Suspenso):**
* **Antecipação:** Usado no início do ano (janeiro) para liberar cota provisória.
* **Definitiva:** Usado (geralmente em fevereiro) quando a LOA é sancionada.
* **Cancelamento:** Usado para estornar cargas anteriores se necessário.

[Tipos de Importação](../imagens/Manual_Carga_Orcamento/tipos_importacao.png)


## Extração de Saldos

Extração das Contas Contábeis que compõem o roteiro da Antecipação da LOA

Antes do início do exercício subsequente, a SEPLAG encaminha à SUGESC os arquivos referentes à antecipação da LOA, com o objetivo de viabilizar a importação e validação no ambiente de Homologação SEPLAG.
Para essa validação, é solicitado que a SUGESC realize a extração das contas que compõem o roteiro da antecipação, garantindo que a carga tenha sido corretamente processada no sistema.
Procedimento para Geração dos Arquivos:
1.	Acessar o menu:
Administração > Configuração > Exportação de Arquivo
2.	Filtrar pelo módulo SEPLAG;
3.	Selecionar as extrações desejadas, conforme orientação da área técnica da SEPLAG;
4.	Gerar e encaminhar os arquivos extraídos para conferência e validação da carga.

Segue abaixo as contas que são solicitadas:
    EXTRACAO_522110201_ANTECIPACAO_LDO
    EXTRACAO_622110101_CRÉDITO_DISPONIVEL
    EXTRACAO_622120101_CRÉDITO_CONTIDO
    EXTRACAO_723130199_CONTROLE_DE_COTAS_DE_LME
    EXTRACAO_823130101_COTAS_DE_LME_A_LIBERAR
