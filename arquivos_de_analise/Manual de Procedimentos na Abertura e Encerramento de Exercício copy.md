# Manual de Abertura e Encerramento de Exercício

---

## Sumário

1. [Introdução](#introdução)
2. [Visão Geral do Processo](#visão-geral-do-processo)
3. [Fase 1: Início dos Testes](#fase-1-início-dos-testes)
4. [Fase 2: Pré-Fechamento](#fase-2-pré-fechamento)
5. [Fase 3: Pré-Virada](#fase-3-pré-virada)
6. [Fase 4: Pós-Virada](#fase-4-pós-virada)
7. [Glossário](#glossário)
8. [Anexos](#anexos)
9. [Cronograma de Encerramento com a SATI](#cronograma-de-encerramento-com-a-sati)

---

## Introdução

### Sobre este Manual

Este manual detalha os procedimentos para o encerramento do exercício financeiro e a abertura do subsequente no **Sistema Integrado de Administração Financeira do Estado do Rio de Janeiro (SIAFE-Rio)**.

O processo é conduzido pela Superintendência de Gerenciamento dos Sistemas Contábeis (SUGESC) da Subsecretaria de Contabilidade Geral do Estado (SUBCONT), órgão da Secretaria de Estado de Fazenda (SEFAZ).

Por ser uma etapa crítica da gestão financeira e orçamentária do Estado, sua execução exige rigor técnico, coordenação e o envolvimento de diversas equipes.

### A Complexidade do Processo: Trabalhando com Dois Exercícios Simultâneos

O processo de encerramento e abertura de exercício no SIAFE-Rio apresenta uma característica que o torna particularmente desafiador: **a operação simultânea de dois esquemas de banco de dados**, correspondentes a dois exercícios financeiros distintos operando em paralelo por algumas semanas.

Esta sistemática, estabelecida pela legislação vigente e necessária para não paralisar as operações do Estado, cria um cenário onde:

**No Banco de Encerramento:**
- Processa-se o fechamento contábil do exercício que se encerra
- Realizam-se ajustes e cancelamentos contábeis e de execução orçamentária
- Efetua-se a inscrição de Restos a Pagar (RP)
- Apura-se o resultado do exercício
- Executam-se os processos de encerramento de saldos contábeis

**No Banco de Abertura:**
- O "mundo financeiro" não para - opera com a "data corrente"
- Execuções financeiras (pagamentos) já ocorrem a partir do dia 2 de janeiro
- Arrecadações e receitas orçamentárias já são registradas desde o dia 2
- Liberações de antecipações do orçamento da despesa (antecipações da LOA) já são processadas
- Lançamentos de reclassificação e inicialização de saldos são realizados

### Os "Momentos" do Processo

O processo se desenrola em diferentes "momentos", cada um com suas características e níveis de criticidade:

**1. Etapas Preparatórias (Outubro/Novembro/Início de Dezembro)**
- Criação do banco do ano seguinte
- Início dos bloqueios no banco de encerramento
- Início dos testes 

**2. Pré-Virada (Meados de Dezembro até 30/12)**
- Início da carga de tabelas e saldos através da "Transferência Diária"
- **Momento que começa a ser crítico**: inicia-se o trabalho simultâneo com os dois bancos
- Ajustes e configurações no banco de abertura
- Intensificação dos bloqueios e controles
- Cancelamentos de Restos a Pagar prescritos

**3. A Virada (31/12 → 01/01)**
- Transferência Diária programada para as 22h do dia 30/12
- Operação simultânea dos dois bancos se intensifica
- Monitoramento dos dados migrados e dos bloqueios realizados

**4. Pós-Virada - O Período Mais Crítico (02/01 até conclusão da inscrição de RP)**

Este é o **período mais crítico** do processo, onde a complexidade atinge seu ápice:

- **No Banco de Abertura:** 
  - Pagamentos das Exceções do RP
  - Receitas sendo arrecadadas
  - Antecipações orçamentárias sendo liberadas e Despesas sendo empenhadas e executadas

- **No Banco de Encerramento:** 
  - Ajustes contábeis finais
  - Cancelamentos orçamentários
  - Inscrição de Restos a Pagar
  - Validações e conferências

**5. Após a Inscrição de RP (Final de Janeiro/Fevereiro)**
- O banco de encerramento fica praticamente fechado
- Não são mais permitidos ajustes de natureza orçamentária
- Apuração final do resultado do exercício
- Processos de encerramentos de saldos contábeis pelo órgão central de contabilidade
- Finalização de lançamentos de reclassificação no banco de abertura

### O Desafio da Gestão Simultânea

A grande complexidade reside em **gerenciar dois exercícios simultaneamente**, garantindo que:
- Os dados migrem corretamente entre os bancos
- Os bloqueios e controles estejam ativados
- As operações do novo exercício não sejam prejudicadas
- O fechamento do exercício anterior seja íntegro e tempestivo
- A equipe consiga dar suporte a ambos os processos em paralelo

### Responsáveis

**Setores Envolvidos:**
- **TI / LOGUS**: Infraestrutura técnica, configurações de banco de dados, agendamentos
- **SUGESC**: Gestão do sistema, coordenação geral do processo, execução operacional
- **SUNOT**: Configuração contábil, normatização contábil, definições técnicas contábeis
- **SEPLAG**: Orçamento, planejamento, LOA, contingenciamento
- **SUDEC**: Controle do fechamento, operações intra-orçamentárias, acompanhamento de pendências contábeis

---

## Visão Geral do Processo

### As 4 Fases do Processo

O processo de encerramento e abertura de exercício é dividido em **4 fases principais**, que representam os diferentes "momentos" pelos quais passamos neste período crítico de fim de ano e início do exercício seguinte:

**Fase 1 - Início dos Testes (Outubro/Novembro/Início de Dezembro)**
- **Característica**: Preparação e validação
- **Criticidade**: Baixa (ambiente controlado)
- **Foco**: Criar e testar todos os procedimentos em ambiente de homologação

**Fase 2 - Pré-Fechamento (Meados de Dezembro)**
- **Característica**: Implementação dos bloqueios e criação do banco de produção
- **Criticidade**: Média (início das restrições operacionais)
- **Foco**: Estabelecer os controles do Decreto de Encerramento e preparar o banco de produção

**Fase 3 - Pré-Virada (20 a 30 de Dezembro)**
- **Característica**: Carga de tabelas, saldos e início da operação simultânea
- **Criticidade**: Alta (trabalho com 2 bancos começa)
- **Foco**: Transferência Diária, cancelamentos de RP, conferências intensivas
- **Marco**: 30/12 às 22h - Transferência Diária programada

**Fase 4 - Pós-Virada (02 de Janeiro em diante)**
- **Característica**: Operação simultânea em plena intensidade
- **Criticidade**: Crítica (pico de complexidade)
- **Foco**: Gestão paralela dos dois exercícios
- **Duração**: Até a conclusão da inscrição definitiva de Restos a Pagar

### Fluxo de Trabalho e Progressão da Criticidade

```
CRITICIDADE:  Baixa ────────▶ Média ────────▶ Alta ────────▶ CRÍTICA

┌─────────────────────────┐
│   Início dos Testes     │ Criação banco teste
│   (Novembro)            │ Testes de migração
│   AMBIENTE CONTROLADO   │ Validações
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Pré-Fechamento       │ Bloqueios do Decreto
│   (Meados Dez)          │ Criação banco PRODUÇÃO
│   INÍCIO RESTRIÇÕES     │ Configurações finais
└───────────┬─────────────┘
            │
            ▼ ┌─────────────────────────────────────┐
┌─────────────────────────┐ │ INÍCIO DA COMPLEXIDADE:         │
│     Pré-Virada          │◄┤ Trabalho SIMULTÂNEO com         │
│   (20-30 Dez)           │ │ 2 BANCOS (2 exercícios)         │
│   TRABALHO DUPLO INICIA │ └─────────────────────────────────┘
└───────────┬─────────────┘
            │ Transferência Diária (30/12 - 22h)
            │
            ▼
┌─────────────────────────┐
│ VIRADA (31/12 → 01/01)  │ Feriado - Sistema operando
└───────────┬─────────────┘
            │
            ▼ ┌─────────────────────────────────────┐
┌─────────────────────────┐ │ PERÍODO MAIS CRÍTICO:           │
│     Pós-Virada          │◄┤                                 │
│   (02 Jan em diante)    │ │ • Banco Abertura: operações     │
│   PICO DE COMPLEXIDADE  │ │   financeiras plenas (dia 2)    │
└─────────────────────────┘ │ • Banco Encerramento: inscrição │
            │               │   de RP e fechamento contábil   │
            │               └─────────────────────────────────┘
            ▼
┌─────────────────────────┐
│ Após Inscrição de RP    │ Banco Encerramento fechado
│ (Final Jan/Fev)         │ Apuração final
│   FINALIZAÇÃO           │ Reclassificações finais
└─────────────────────────┘
```

### A Natureza Dual do Processo

Durante o período crítico (do dia 2 de janeiro até a conclusão da inscrição de RP), a equipe trabalha em **duas frentes simultâneas**:

| **BANCO DE ENCERRAMENTO** | **BANCO DE ABERTURA** |
|---------------------------|----------------------|
| 🔒 **Modo**: Fechamento | ▶️ **Modo**: Operação plena |
| 📊 Ajustes contábeis finais | 💰 Pagamentos de despesas |
| ❌ Cancelamentos orçamentários | 💵 Arrecadação de receitas |
| 📝 Inscrição de Restos a Pagar | 📈 Empenhos do novo exercício |
| ✅ Validações e conferências | 🚀 Antecipações da LOA |
| 🔢 Apuração de resultados | 🔄 Reclassificações de saldos |
| **Objetivo**: Fechar com integridade | **Objetivo**: Operar sem interrupções |

### Princípios Fundamentais do Processo

1. **Integridade dos Dados**: Garantir que nenhum dado seja perdido ou corrompido na migração entre exercícios

2. **Continuidade Operacional**: Assegurar que as operações do Estado não sejam interrompidas durante a transição

3. **Conformidade Legal**: Cumprir todos os prazos e requisitos da legislação de encerramento

4. **Rastreabilidade**: Manter registro detalhado de todas as operações para auditoria e prestação de contas

5. **Coordenação**: Sincronizar as ações de múltiplas equipes operando em ambos os bancos

### Desafios Específicos do Processo

**Desafio Técnico:**
- Gerenciar dois ambientes de banco de dados simultaneamente
- Garantir a sincronização através da Transferência Diária
- Evitar "saldos virados" e contaminação entre exercícios

**Desafio Operacional:**
- Suporte a usuários operando em dois exercícios diferentes
- Esclarecimento sobre qual banco utilizar para cada operação
- Gestão de erros e inconsistências em tempo real

**Desafio Temporal:**
- Prazos legais rígidos (Decreto de Encerramento, LRF)
- Necessidade de operação ininterrupta do Estado
- Pressão por fechamento contábil tempestivo

**Desafio de Comunicação:**
- Coordenação entre múltiplos setores (TI, SUGESC, SUNOT, SEPLAG, SUDEC)
- Comunicação clara com centenas de Unidades Gestoras
- Alinhamento com órgãos de controle externo

---

## Fase 1: Início dos Testes

### Objetivo
O objetivo desta fase é a preparação de ambientes de teste para a validação dos procedimentos de encerramento e abertura, precedendo a execução em produção. A quantidade de ambientes a serem criados pode variar a cada ano, a depender da implementação de novas rotinas financeiras, contábeis ou orçamentárias.

Geralmente, a arquitetura de testes é segmentada em duas frentes. O primeiro banco de dados é dedicado à validação de rotinas sistêmicas, como transferências diárias, migração de saldos, mapeamentos de dados (de-para) e migração de tabelas.

Paralelamente, um segundo banco de dados é configurado para atender às necessidades da equipe da SEPLAG, sendo utilizado para realizar testes de carga do orçamento e homologar melhorias no processo orçamentário para o exercício subsequente.

---

### 1.1 Criar Banco de Testes para Abertura e Encerramento

**Responsável:** TI / LOGUS / SUGESC / SUNOT

#### 1.1.1 Criar o Banco de Teste com o Ano Seguinte
**Responsável:** TI / LOGUS

**Procedimento:**
- Criar novo banco de dados com o código (esquema) do exercício seguinte
- Configurar a data do sistema para **01/01 do ano seguinte**

**Observações:**
- Esta ação é fundamental para simular o ambiente de produção para a migração entre exercícios

---

#### 1.1.2 Inicializar as Tabelas de Apoio
**Responsável:** TI / LOGUS

**Procedimento:**
1. Acessar a funcionalidade **"Migração de Tabelas"**
2. Executar o processo de inicialização do banco
3. Validar a carga das tabelas básicas (tabelas de apoio)

**Observações:**
- Este processo cria a estrutura básica do banco para o novo exercício

---

#### 1.1.3 Configurar o DEPARA Contábil
**Responsável:** SUGESC / SUNOT

**Procedimento:**
1. Copiar o parâmetro de DEPARA da Produção
2. Verificar com a SUNOT se há necessidade de inclusões ou mudanças no DEPARA contábil
3. Aplicar as alterações necessárias

**Observações:**
- O DEPARA Contábil é essencial para o correto lançamento dos saldos no novo exercício

---

#### 1.1.4 Verificar Preenchimento da Aba "Tipo de Encerramento" no Plano de Contas
**Responsável:** SUNOT

**Procedimento:**
1. Acessar o Plano de Contas
2. Verificar que **todas as contas analíticas** possuem o campo "Tipo de Encerramento" preenchido corretamente
3. Corrigir eventuais inconsistências

**Observações:**
- Este campo determina o comportamento da conta no processo de encerramento

---

#### 1.1.5 Ativar o Agendamento Genérico de Migração das Tabelas
**Responsável:** SUGESC

**Procedimento:**
1. Acessar: **PROCESSO "Atualizar Dados Cadastrais"**
2. Configurar: `logus.siplag.agendamento.job.ExecutarMigracaoTabelaJob`
3. Parâmetros exemplo: `SIAFE_RIO2_2024 / 2024 / 00001 >> SIAFE_RIO2_2025 / 2025 / 00001`

**Observações:**
- Este agendamento evita inconsistências que geram erros na Transferência Diária, impactando por consequência as migrações de Saldos Contábeis e de Documentos. O problema surge quando a rotina busca em tabelas dados que ainda não existem no banco de dados do novo exercício.

---

#### 1.1.6 Ativar a Transferência Diária
**Responsável:** SUGESC

**Procedimento:**
1. Ativar o agendamento da Transferência Diária
2. Executar testes manuais
3. Analisar e corrigir os erros identificados

**Observações:**
- A Transferência Diária é um agendamento, mas podem ser feitos testes manuais
- Realizar análises pontuais de UGs específicas que apresentem erros

---

#### 1.1.7 Analisar a Migração de Saldos e Documentos
**Responsável:** SUGESC

**Procedimento:**
1. Realizar batimento de saldos entre banco de encerramento e abertura
2. Verificar a migração correta dos documentos
3. Utilizar preferencialmente o **FlexVision** para análise dos saldos

**Observações:**
- Esta análise é crítica para garantir a consistência dos dados e integridade dos saldos contábeis

---

#### 1.1.8 Verificar Bloqueios e Travas de PDs nos Dois Exercícios
Durante o encerramento e a abertura de exercícios, é fundamental garantir que **os controles de PDs (Programações de Desembolso)** não apresentem **saldos invertidos** — ou seja, valores pagos ou anulados em exercícios diferentes, comprometendo a integridade do controle contábil.
Essas situações ocorrem, por exemplo, quando uma **PD do exercício anterior é paga no banco do novo exercício** e, posteriormente, **anulada no banco do exercício anterior**, resultando em **saldo negativo (“virado”)** no banco de abertura.

**Responsável:** SUGESC

**Objetivo:**
Assegurar que todas as regras e travas sistêmicas estejam corretamente parametrizadas e ativas para impedir a geração de PDs ou OBs que causem inversão de saldos entre exercícios.

**Procedimento:**

1. Verificar quais regras funcionam “por dentro do sistema” (que exigem data **01/JAN**).
2. Identificar regras parametrizadas no sistema que afetam o controle de PDs.
3. Criar, revisar ou ativar **regras de compatibilidade** necessárias para o novo exercício.
4. Testar o comportamento das travas a partir da virada do ano para garantir que **nenhuma operação de PD** gere saldo invertido.

**Observações:**

* É essencial evitar que PDs **anuladas ou pagas fora do exercício correto** resultem em **saldos invertidos no banco de abertura**.

---

### 1.2 Criar Banco de Testes para a Carga da LOA

**Responsável:** SUGESC / SEPLAG / TI / LOGUS

**Observação Inicial:**
- Pode ser utilizado o mesmo banco criado para os testes de Abertura e Encerramento (Ex: HML2 SEPLAG)

---

#### 1.2.1 Carregar as Tabelas de Apoio (TXT)
**Responsável:** SUGESC

**Procedimento:**
1. Receber os arquivos TXT da SEPLAG (OBS: para testes podem ser utilizados os arquivos do último ano)
2. Executar a carga das tabelas através da funcionalidade específica
3. Validar a carga

---

#### 1.2.2 Carregar os Arquivos de LME (XLS)
**Responsável:** SUGESC

**Procedimento:**
1. Receber os arquivos XLS da SEPLAG
2. Executar a carga através da funcionalidade específica
3. Validar a carga

---

#### 1.2.3 Carregar a LOA (Metas Financeiras)
**Responsável:** SUGESC

**Procedimento:**
1. Receber o arquivo da LOA da SEPLAG
2. Executar a carga das metas financeiras
3. Validar a carga

---

#### 1.2.4 Contabilizar as NDs (Importar LOA)
**Responsável:** SUGESC

**Procedimento:**
1. Executar a funcionalidade de contabilização das Notas de Dotação
2. Validar os lançamentos contábeis

---

#### 1.2.5 Exportar Arquivos para Conferência da SEPLAG
**Responsável:** SUGESC

**Procedimento:**
1. Acessar a funcionalidade: **"Exportação de Arquivos"**
2. Gerar os arquivos de conferência
3. Enviar para a SEPLAG validar a carga realizada

**Observações:**
- Podem ocorrer testes de:
  - Antecipação
  - Cancelamento da Antecipação
  - Carga Definitiva da LOA

---

## Fase 2: Pré-Fechamento

### Objetivo
Implementar os bloqueios do Decreto de Encerramento e criar o banco de produção do exercício seguinte.

---

### 2.1 Realizar os Bloqueios do Decreto de Encerramento

**Responsável:** SUGESC / SEPLAG / SUDEC

---

#### 2.1.1 Bloqueio de EMPENHAMENTO
**Responsável:** SUGESC / SEPLAG

**Procedimento:**
1. Ativar a regra: **Bloqueio Funcionalidade UG - Empenho**
2. Permitir que a SUBPLO realize o Contingenciamento no SIPLAG
3. Após a realização do contingenciamento, liberar o bloqueio

**Observações:**
- Impedir empenhamento após a data limite, ressalvadas as exceções previstas no Decreto
- **NÃO bloquear:**
  - PODERES (Códigos: 01, 02 e 03)
  - MP (10)
  - PGE (09)
  - DPGE (11)
- **Atenção:** Na ABA DISPONÍVEIS, as UG 030400, 030401, 030402, 030403, 030404 e 030410 pertencem aos Poderes, por isso não devem ser bloqueadas

---

#### 2.1.2 Bloqueio de ADIANTAMENTO
**Responsável:** SUGESC

**Procedimento:**
1. **Ativar a Regra de Compatibilidade 381**
2. Esta regra impede pagamento de adiantamentos após a data limite
3. Cancelar PDS não pagas de adiantamentos

**Objetivo:**
- Impedir pagamento após a data limite e cancelar PDS não pagas

---

#### 2.1.3 Bloqueio de OBs INTRA
**Responsável:** SUDEC

**Procedimento:**
1. **Ativar a Regra de Compatibilidade 375**
2. Esta regra deve ser ativada no **início do dia seguinte** para permitir a execução das PDs até o prazo máximo do dia do decreto.

**Objetivo:**
- Impedir pagamento após a data limite

**Observações:**
- Esta regra é de responsabilidade da SUDEC

---

### 2.2 Criar o Banco do Exercício Seguinte (PRODUÇÃO)

**Responsável:** TI / LOGUS / SUGESC

---

#### 2.2.1 Criar o Banco de Produção
**Responsável:** TI / LOGUS / SUNOT

**Procedimento:**
1. Criar o banco de dados de produção com o ano seguinte
2. Verificar com a SUNOT a melhor data de criação (pode necessitar antecedência para configurações contábeis de Plano de Contas, Regras de Mapeamentos, e Tipo, Itens e Operações Patrimoniais)

---

#### 2.2.2 Inicializar as Tabelas de Apoio
**Responsável:** TI / LOGUS

**Procedimento:**
1. Executar a funcionalidade **"Migração de Tabelas"**
2. Inicializar o banco com as tabelas básicas

---

#### 2.2.3 Configurar o DEPARA Contábil
**Responsável:** SUGESC

**Procedimento:**
1. Copiar o parâmetro que foi testado e validado no ambiente de testes
2. Aplicar no banco de produção

---

#### 2.2.4 Verificar o Tipo de Encerramento no Plano de Contas
**Responsável:** SUGESC / SUNOT

**Procedimento:**
1. Fazer a última conferência da Aba "Tipo de Encerramento" no Plano de Contas
2. Garantir que todas as contas estão corretamente preenchidas

---

#### 2.2.5 Verificar Tabelas de Ação e Programa
**Responsável:** TI / LOGUS / SUGESC

**Procedimento:**
1. Acessar: **Planejamento >> Plano Plurianual**
2. Verificar a existência das Tabelas de Ação e Programa
3. Provisoriamente, carregar a Tabela do Ano anterior (será sobrescrita pela carga do TXT da LOA)

**Observações:**
- Informação anual fornecida pela SEPLAG
- Não fica no pacote de inicialização do banco

---

#### 2.2.6 Possibilitar Execução de PDS de RPP antes da Inscrição Definitiva
**Responsável:** SUGESC

**Procedimento:**
1. **Ativar a Regra de Compatibilidade 361**

**Objetivo:**
- Permitir a execução de PDs de RPP no Banco de Abertura antes da inscrição definitiva de Restos a Pagar
- Vale tanto para o Tesouro como para os órgãos que tenham recursos próprios
- Importante que a Regra esteja atualizada com os possíveis novos dados (como fonte, etc) do Decreto de Encerramento

**Observações:**
- Exemplo de exceção: Quando o Governador libera pagamentos específicos
- Acrescentar na regra: `OU ([UNIDADE GESTORA FINANCEIRA].[CÓDIGO] = 296100 e EXTRAI([NÚMERO DA PD].[CÓDIGO], 7, 11) pertence ('2018PD00028', '2018PD01019'))`

---

#### 2.2.7 Realizar Bloqueio Geral de TODAS as Contabilizações
**Responsável:** SUGESC

**Procedimento:**
1. Executar o **Bloqueio Funcionalidades UG**
2. Este bloqueio impede qualquer contabilização no banco de abertura

**Objetivo:**
- Garantir que não haja lançamentos indevidos no banco do novo exercício antes da liberação oficial

---

#### 2.2.8 Bloquear as Funcionalidades de Execução no Banco de Abertura
**Responsável:** SUGESC

**Contexto:**
Neste momento (antes da virada), o Banco de Abertura ainda não está operacional. Toda a execução financeira e orçamentária continua ocorrendo no Banco de Encerramento. Portanto, é necessário bloquear praticamente todas as funcionalidades de execução no Banco de Abertura.

**Procedimento:**
1. Executar o **Bloqueio Funcionalidade Usuário** no Banco de Abertura
2. Aplicar bloqueio geral para **aproximadamente 366 funcionalidades de execução**
3. Manter liberadas APENAS:
   - Funcionalidades de **Visualização** (consultas e relatórios)
   - Funcionalidades de **Configuração** necessárias para o Órgão Central de Contabilidade (SUNOT)

**Funcionalidades que devem permanecer LIBERADAS no Banco de Abertura:**


**Usuários NÃO Bloqueados no Banco de Abertura (antes da virada):**
- `admin` 
- `CECIERJ` 
- `CONTROLE - CGE` 
- `converj` 
- `quartz` 
- `ARR` 
- `SISGRE` 
- `siga` 
- `SIPLAG` 
- `seeduc` 

**Observações CRÍTICAS:**

⚠️ **IMPORTANTE - Sincronização de Configurações:** 
Após a criação do banco de dados de produção do exercício seguinte, **qualquer alteração de configuração que a SUNOT realize no Banco de Encerramento deve ser OBRIGATORIAMENTE replicada no Banco de Abertura**. Esta ação é crucial para garantir a consistência e a integridade entre os dois ambientes.

**Exemplos de configurações que devem ser sincronizadas:**
- Alterações no Plano de Contas
- Ajustes em regras contábeis
- Modificações em parâmetros do sistema
- Atualizações de DEPARA Contábil

---

### 2.3 Atualizar Views Históricas do FlexVision

**Responsável:** TI / LOGUS / SUGESC

#### 2.3.1 Atualizar Cubo de Saldos Contábeis Histórico
**Procedimento:**
1. Fazer a junção do novo ano no Cubo de Saldos Contábeis Histórico
2. Atualizar as views históricas

**Objetivo:**
- Permitir a conferência de saldos

**Observações:**
- **Neste primeiro momento NÃO fazer o apontamento do Flex para o novo ano**
- O apontamento será feito apenas na Fase 4 (Pós-Virada)


---

## Fase 3: Pré-Virada

### Objetivo
Realizar os cancelamentos de Restos a Pagar, executar a Transferência Diária e preparar os bancos para a virada do exercício.

---

### 3.1 Cancelar o RP (RPP Prescrito e RPNP Poderes)

**Responsável:** SUGESC

---

#### 3.1.1 Cancelar Saldos das Contas de PDS (RPP Prescrito)
**Responsável:** SUGESC

**Procedimento:**
1. Executar o **Processo de Encerramento N° 9**
2. CANCELAR o saldo das contas:
   - **PDS A EMITIR**
   - **PDS EMITIDAS A PAGAR**
3. Referente ao RPP Prescrito de **5 anos**

**Observações:**
- Verificar se existe funcionalidade de Anular PDs em LOTE

---

#### 3.1.2 Cancelar PDS não Pagas (RPP Prescrito)
**Responsável:** SUGESC

**Procedimento:**
1. CANCELAR por SCRIPT as PDS (documento/capa) não pagas de RPP Prescrito de **5 anos**
2. **Ressalvar** as PDS de RPP REPACTUADO (não cancelar)
3. Confrontar o Saldo de PDs Emitidas com as PDs (capas documentais)

**Observações:**
- Verificar se existe funcionalidade de Anular PDs em LOTE

---

#### 3.1.3 Cancelar o RPP Prescrito de 5 Anos
**Responsável:** SUGESC

**Procedimento:**
1. Executar os **Processos de Encerramento N° 14, 15 e 16**
2. Cancelar definitivamente o RPP Prescrito

---

#### 3.1.4 Cancelar RPNP do Exercício Anterior (Outros Poderes)
**Responsável:** SUGESC

**Procedimento:**
1. Executar o **Processo de Encerramento N° 8**
2. CANCELAR o RPNP do Exercício Anterior remanescente:
   - **Outros Poderes**
   - **Índices Constitucionais**
3. Processar:
   - Conta **631110101** - por ANO+NE
   - Conta de controle - por ANO+FR
4. **IMPORTANTE:** Após o cancelamento, impedir que sejam feitos estornos

---

#### 3.1.5 Impedir Pagamento de RPP Cancelados por Prescrição
**Responsável:** SUGESC

**Procedimento:**
1. **Ativar a Regra de Compatibilidade 296 no Banco de Abertura**

**Objetivo:**
- Garantir que os RPP que estão sendo cancelados por prescrição não sejam pagos no banco de abertura

---

### 3.2 Transferência Diária

**Responsável:** SUGESC

---

#### 3.2.1 Ativar o Agendamento da Transferência Diária
**Responsável:** SUGESC

**Procedimento:**
1. Acessar: **Banco de Abertura >> Administração / Agendamento / Transferência Diária**
2. Ativar o agendamento para as **22:00h do dia 30/12** (ou antes)

**Observações:**
- O ideal é agendar o mais próximo possível da virada para carregar o mínimo possível de "PDs Lixo"
- Este é o momento crítico onde inicia-se a operação simultânea dos dois bancos

---

#### 3.2.2 Ativar Agendamento de Migração das Tabelas
**Responsável:** SUGESC

**Procedimento:**
1. Acessar: **Banco de Abertura >> Administração / Agendamento / Agendamento Genérico**
2. Ativar: **"Atualizar Dados Cadastrais - Migração de Tabelas (início do dia)"**

**Observações:**
- Este agendamento mantém as tabelas cadastrais atualizadas entre os bancos

---

#### 3.2.3 Conferir Saldos de Encerramento e Abertura
**Responsável:** SUGESC

**Procedimento:**
1. Realizar conferência detalhada dos saldos entre:
   - Banco de Encerramento
   - Banco de Abertura
2. Conferir a Migração das Tabelas (Ex: listas de favorecidos)
3. Conferir a Migração dos Documentos (Ex: PDs)

**IMPORTANTE:**
- O **Bloqueio Geral de Contabilizações** deve estar travando toda e qualquer contabilização (até a liberação - OK)

---

#### 3.2.4 Verificar Erros da Transferência Diária
**Responsável:** SUGESC

**Procedimento:**
1. Analisar o log da execução da Transferência Diária
2. Identificar e corrigir possíveis erros
3. Documentar as inconsistências para tratamento

---

### 3.3 Evitar “Saldo Virado” de PDs

**Responsável:** TI / LOGUS / SUGESC

Durante o encerramento e a abertura de exercícios, é fundamental garantir que **os controles de PDs (Programações de Desembolso)** não apresentem **saldos invertidos** — ou seja, valores pagos ou anulados em exercícios diferentes, comprometendo a integridade do controle contábil.
Essas situações ocorrem, por exemplo, quando uma **PD do exercício anterior é paga no banco do novo exercício** e, posteriormente, **anulada no banco do exercício anterior**, resultando em **saldo negativo (“virado”)** no banco de abertura.

---

#### 3.3.1 Impedir PDs que NÃO sejam do Tipo “REGULARIZAÇÃO” em 30/12

**Responsável:** TI / LOGUS / SUGESC

**Procedimento:**

1. Implementar **bloqueio sistêmico automático** a partir de **30/12**.
2. No Banco de encerramento do exercício, **impedir a emissão de PDs que não sejam do tipo “REGULARIZAÇÃO”**.

**Observações:**

* O bloqueio entra em vigor automaticamente após a virada de ano (**01/01**).
* Como os pagamentos financeiros estão ocorrendo no banco de abertura, no banco de encerramento as emissões de PDs devem ser obrigatoriamente de regularização.

---

#### 3.3.2 Impedir PDs e OBs de REGULARIZAÇÃO no Banco de Abertura

**Responsável:** SUGESC

**Procedimento:**

1. **Ativar a Regra de Compatibilidade 360.**
2. Impedir a confecção e execução de **PDs e OBs do tipo REGULARIZAÇÃO** no banco de abertura.

**Observações:**

* Atualmente configurada como **“AVISAR”**; deve ser alterada para **“IMPEDIR”**.
* Evita que ajustes indevidos de PDs impactem o saldo do exercício anterior.

---

#### 3.3.3 Impedir Anulação de PDs de Anos Anteriores no Banco de Abertura

**Responsável:** SUGESC

**Procedimento:**

1. Ativar o **Bloqueio de Funcionalidade UG** com expressão de exceção específica.
2. Impedir que PDs de exercícios anteriores sejam anuladas no banco de abertura.

### 🧩 Exemplo Prático

O caso abaixo demonstra a importância dos bloqueios descritos:

* Uma **PD de 2024** foi **paga em 2025** (no banco do novo exercício).
* Posteriormente, o usuário **anulou a PD no banco de 2024**, gerando um **saldo virado** negativo em 2025.

# Exemplo Real

![Exemplo de Saldo Invertido](imagens/Exemplo Saldo Invertido.png)

---

## Fase 4: Pós-Virada

### Objetivo
Realizar os ajustes finais, apontar o FlexVision para o novo exercício e implementar os bloqueios específicos pós-virada.

### ⚠️ ATENÇÃO: Período Mais Crítico

**A partir do dia 2 de janeiro inicia-se o PERÍODO MAIS CRÍTICO do processo**, caracterizado pela operação simultânea em plena intensidade dos dois bancos:

**🟢 BANCO DE ABERTURA - Operação Plena:**
- ✅ Execuções financeiras (pagamentos) já ocorrem a partir do dia 2
- ✅ Arrecadações e receitas orçamentárias sendo registradas
- ✅ Antecipações do orçamento da despesa (antecipações da LOA) sendo liberadas
- ✅ Empenhos sendo realizados
- ✅ Sistema operando com a "data corrente" - o mundo financeiro não para

**🔴 BANCO DE ENCERRAMENTO - Fechamento Contábil:**
- 🔄 Trabalho intenso de fechamento contábil do exercício
- 🔄 Ajustes e cancelamentos contábeis em andamento
- 🔄 Execução orçamentária sendo ajustada
- 🔄 Inscrição de Restos a Pagar em processamento
- 🔄 Validações e conferências contínuas

### Duração do Período Crítico

Este período crítico se estende **até a conclusão da inscrição definitiva de Restos a Pagar**, o que geralmente ocorre entre final de janeiro e fevereiro.

**Após a inscrição de RP:**
- ✅ O banco de encerramento não permite mais ajustes de natureza orçamentária
- ✅ O sistema fica praticamente fechado para apuração do resultado do exercício
- ✅ Iniciam-se os processos de encerramentos de saldos contábeis pelo órgão central de contabilidade
- ✅ No banco de abertura são finalizados os lançamentos de reclassificação e inicialização de saldos

---

### 4.1 Apontar o FlexVision para o Exercício Seguinte

**Responsável:** TI / LOGUS / SUGESC

**Procedimento:**
1. Alterar a configuração do FlexVision
2. Apontar o Flex para o novo ano corrente

**Observações:**
- Este é o momento em que o FlexVision passa a exibir prioritariamente os dados do novo exercício

---

### 4.2 Realizar o Bloqueio de Funcionalidades (Pós-Virada)

**Responsável:** SUGESC

**Contexto:**
Após a virada do exercício (a partir de 02 de janeiro), os bloqueios de funcionalidades precisam ser ajustados para refletir a nova realidade operacional: o **Banco de Abertura passa a ser o ambiente de execução financeira**, enquanto o **Banco de Encerramento** fica restrito aos ajustes contábeis e inscrição de RP.

---

#### 4.2.1 Bloquear Funcionalidades no Exercício de Encerramento

**Responsável:** SUGESC

**Objetivo:** Impedir funcionalidades relacionadas ao **processo financeiro de pagamentos e arrecadações**, pois estas devem ser realizadas exclusivamente no Banco de Abertura a partir do dia 2 de janeiro.

**Procedimento:**
1. Executar **Bloqueio Funcionalidade Usuário** no Banco de Encerramento
2. **IMPEDIR** as seguintes categorias de funcionalidades:

**💳 FUNCIONALIDADES FINANCEIRAS BLOQUEADAS:**
- **BLOQUETOS e FATURAS** (Código de Barras)
  - Cadastrar Código de Barras
  - Alterar Código de Barras
  - Todas as operações com código de barras

- **DOMBANS** (Domicílio Bancário)
  - Todas as funcionalidades relacionadas
  
- **LISTAS de Favorecidos**
  - Cadastrar Lista Favorecido OB
  - Demais operações com listas

**Total de Funcionalidades Bloqueadas:** Aproximadamente **12 funcionalidades** específicas do processo financeiro

**Justificativa:**
A partir do dia 2 de janeiro, **todas as operações financeiras** (pagamentos, arrecadações, movimentações bancárias) devem ocorrer no Banco de Abertura, que opera com a "data corrente".

**Usuários Especiais - NÃO Bloqueados:**
Durante este período, os seguintes usuários **NÃO são bloqueados** no Banco de Encerramento (necessitam realizar ajustes):
- `SIGA` 
- `ARR` 
- `SISGRE`

---

#### 4.2.2 Bloquear Funcionalidades no Exercício de Abertura

**Responsável:** SUGESC

**Objetivo:** Manter o bloqueio de **Cadastros de Apoio** no Banco de Abertura, pois estes devem continuar sendo gerenciados no Banco de Encerramento até a conclusão da inscrição de RP.

**Procedimento:**
1. Executar **Bloqueio Funcionalidade Usuário** no Banco de Abertura
2. **MANTER BLOQUEADAS** as seguintes categorias:

**📁 CADASTROS DE APOIO (continuam bloqueados):**
- **COMUNICAS** (inclusive os AUTOMÁTICOS)
- **INSCRIÇÕES GENÉRICAS**
- **CREDORES**
- **CONVÊNIOS**
- **CONTRATOS**
- **Outros cadastros auxiliares**

**Regra:** Estes cadastros **continuam a ser realizados APENAS no Banco de Encerramento**.

**Sincronização:** Os dados cadastrais são migrados diariamente para o Banco de Abertura por meio da rotina **"Atualizar Dados Cadastrais"**.

**Duração:** Até a conclusão da inscrição de Restos a Pagar (geralmente meados de janeiro).

**Usuários NÃO Bloqueados no Banco de Abertura (após a virada):**
- `admin` 
- `SISGRE` 
- `ARR` 
- `quartz` 
- `CONTROLE - CGE`
- `SIGA` (DEVE SER BLOQUEADO no Banco de Abertura enquanto não há orçamento carregado)

---

### 4.3 Bloqueios Após a Inscrição de RP (Fechamento Final)

**Responsável:** SUGESC

**Contexto:**
Após a conclusão da inscrição definitiva de Restos a Pagar (geralmente final de janeiro/início de fevereiro), o Banco de Encerramento entra em sua fase final de fechamento, onde **não são mais permitidos ajustes de natureza orçamentária**.

---

#### 4.3.1 Bloqueio MASSIVO no Banco de Encerramento

**Objetivo:** Fechar praticamente todo o sistema no Banco de Encerramento para:
- Apuração do resultado do exercício
- Processos de encerramentos de saldos contábeis pelo órgão central de contabilidade
- Preparação para auditoria e prestação de contas

**Procedimento:**
1. Executar **Bloqueio Funcionalidade Usuário** no Banco de Encerramento
2. **BLOQUEAR aproximadamente 313 funcionalidades**
3. Aplicar bloqueio para **TODOS os usuários** (sem exceções)

**📋 CATEGORIAS DE FUNCIONALIDADES BLOQUEADAS:**

**🚫 Documentos Orçamentários:**
- Anular Nota de Empenho
- Anular Nota de Empenho em Lote
- Anular Nota de Liquidação
- Anular Nota Patrimonial
- Cadastrar Ação (Despesa Orçamento)
- Qualquer operação com documentos orçamentários

**Justificativa Técnica:** O bloqueio funcionalidade UG **NÃO trava o botão anular** (trava apenas o botão contabilizar). Por isso, é necessário bloquear explicitamente estas funcionalidades através do Bloqueio Funcionalidade Usuário.

**🚫 Cadastros de Pessoas:**
- Alterar Pessoa Física
- Alterar Pessoa Jurídica
- Ativar/Desativar Pessoa Física
- Ativar/Desativar Pessoa Jurídica
- Bloquear/Desbloquear Pessoa Física
- Bloquear/Desbloquear Pessoa Jurídica

**🚫 Contratos e Convênios:**
- Todas as funcionalidades relacionadas a contratos
- Todas as funcionalidades relacionadas a convênios

**🚫 Importações e Cargas:**
- Cadastrar/Importar quaisquer dados
- Agendamentos de processos

**🔍 Método de Busca para Bloqueio:**
Utilizar as seguintes **palavras-chave** para identificar funcionalidades a serem bloqueadas:
- `pessoa`
- `contrato`
- `convênios`
- `comunica`
- `despesa exercí`
- `cadastrar`
- `importar`

**✅ Funcionalidades que PERMANECEM LIBERADAS:**
Apenas funcionalidades essenciais para o fechamento contábil:
- Alterar Regra de Compatibilidade
- Alterar Relatórios da LRF
- Alterar Relatórios do Balanço
- Alterar Relatórios Gerenciais
- Funcionalidades de consulta e visualização

**Total Bloqueado:** Aproximadamente **313 funcionalidades** de um total de 607.

---

#### 4.3.2 Liberação TOTAL no Banco de Abertura

**Objetivo:** O Banco de Abertura passa a operar em **plena capacidade**, sem restrições.

**Procedimento:**
1. **REMOVER todos os bloqueios** de funcionalidades do Banco de Abertura
2. **LIBERAR todos os usuários** no Banco de Abertura
3. Permitir:
   - Cadastros de Apoio (Credores, Convênios, Contratos)
   - Comunicas (todos os tipos)
   - Inscrições Genéricas
   - Todas as funcionalidades de execução orçamentária e financeira

**Observações:**
- A partir deste momento, **TODA a operação do Estado** ocorre exclusivamente no Banco de Abertura
- O Banco de Encerramento fica congelado para apurações contábeis finais

---

### 4.4 Quadro Resumo de Bloqueios por Fase

| Fase | Banco de Encerramento | Banco de Abertura | Duração |
|------|----------------------|-------------------|---------|
| **ANTES DA VIRADA**<br>(até 31/12) | ✅ **TUDO LIBERADO**<br>Operação normal | 🔒 **QUASE TUDO BLOQUEADO**<br>~366 funcionalidades bloqueadas<br>Liberadas: configurações e visualizações | Até 31/12 23:59 |
| **APÓS A VIRADA**<br>(02/01 até inscr. RP) | 🔒 **Bloqueio FINANCEIRO**<br>~12 funcionalidades bloqueadas<br>(Bloquetos, DOMBANS, Listas)<br>✅ Permite ajustes orçamentários | 🔶 **Bloqueio CADASTRAL**<br>Bloqueados: Cadastros de Apoio<br>✅ Execução financeira liberada | ~3 a 4 semanas |
| **APÓS INSCRIÇÃO RP**<br>(final Jan/Fev) | 🔒 **BLOQUEIO MASSIVO**<br>~313 funcionalidades bloqueadas<br>Bloqueados: TODOS usuários<br>Liberadas: apenas relatórios | ✅ **TUDO LIBERADO**<br>Operação plena | Permanente |

---

### 4.5 Impedir GDs no Banco de Abertura

**Responsável:** TI / LOGUS / SUGESC

**Procedimento:**
1. Tratar OBs pagas no exercício e devolvidas no exercício seguinte
2. Executar **Script para retirar a contabilização de GDs** (no Banco de Encerramento)
3. Utilizar a funcionalidade: **"Conciliação de OBs"**

**Observações:**
- Este procedimento evita inconsistências contábeis com GDs (Guias de Devolução) que atravessam a virada do exercício

---

## Glossário

### Siglas e Abreviações

- **DEPARA**: Tabela de correspondência contábil entre contas
- **DPGE**: Defensoria Pública Geral do Estado
- **FR**: Fonte de Recursos
- **GD**: Guia de Devolução
- **LOA**: Lei Orçamentária Anual
- **LME**: Limite de Movimentação e Empenho
- **MP**: Ministério Público
- **ND**: Nota de Dotação
- **NE**: Nota de Empenho
- **OB**: Ordem Bancária
- **PD**: Programação de Desembolso
- **PGE**: Procuradoria Geral do Estado
- **RP**: Restos a Pagar
- **RPNP**: Restos a Pagar Não Processados
- **RPP**: Restos a Pagar Processados
- **SEPLAG**: Secretaria de Estado de Planejamento e Gestão
- **SIAFE-Rio**: Sistema Integrado de Administração Financeira do Estado do Rio de Janeiro
- **SIPLAG**: Sistema de Planejamento
- **SUBPLO**: Subsecretaria de Planejamento Orçamentário
- **SUDEC**: Superintendência de Descentralização
- **SUGESC**: Superintendência de Gestão do Sistema Contábil
- **SUNOT**: Superintendência de Normas Técnicas
- **UG**: Unidade Gestora

### Termos Técnicos

**Agendamento Genérico**
Funcionalidade que permite agendar a execução automática de processos do sistema em horários específicos.

**Banco de Abertura**
Esquema de banco de dados correspondente ao exercício que está se iniciando, onde ocorrem as execuções financeiras do novo exercício.

**Banco de Encerramento**
Esquema de banco de dados correspondente ao exercício que está se encerrando, onde ocorrem os ajustes contábeis e a inscrição de Restos a Pagar.

**Bloqueio de Funcionalidade UG**
Restrição aplicada a uma ou mais Unidades Gestoras que impede a execução de determinadas funcionalidades do sistema.

**Bloqueio de Funcionalidade Usuário**
Restrição aplicada a usuários específicos ou grupos de usuários que impede a execução de determinadas funcionalidades do sistema.

**Contingenciamento**
Limitação de empenho e movimentação financeira estabelecida para garantir o cumprimento das metas fiscais.

**Decreto de Encerramento**
Ato normativo que estabelece os prazos e procedimentos para o encerramento do exercício financeiro.

**FlexVision**
Ferramenta de Business Intelligence utilizada para análise de dados contábeis e financeiros do SIAFE-Rio.

**Migração de Tabelas**
Processo de transferência das tabelas cadastrais básicas do banco de encerramento para o banco de abertura.

**PD Lixo**
Programações de Desembolso criadas no final do exercício que não deveriam ser migradas para o exercício seguinte.

**Prescrição de RP**
Perda da exigibilidade de Restos a Pagar após o prazo de 5 anos, conforme legislação vigente.

**Regra de Compatibilidade**
Validação parametrizável no sistema que pode AVISAR, IMPEDIR ou PERMITIR determinadas operações conforme regras de negócio.

**Regularização (PD)**
Tipo específico de Programação de Desembolso utilizada para ajustes e correções de lançamentos.

**Saldo Virado**
Situação indevida onde saldos ou documentos do exercício anterior contaminam o novo exercício.

**Transferência Diária**
Processo automatizado que migra saldos, documentos e informações do banco de encerramento para o banco de abertura.

**Tipo de Encerramento**
Atributo da conta contábil que determina como seus saldos devem ser tratados no processo de encerramento do exercício.

---

## Anexos

### Anexo A - Cronograma de Referência

| Período | Fase | Principais Atividades |
|---------|------|----------------------|
| **Novembro** | Início dos Testes | Criação do banco de testes, testes de migração e LOA |
| **Início de Dezembro** | Pré-Fechamento | Bloqueios do Decreto, criação do banco de produção |
| **20 a 29 de Dezembro** | Pré-Virada | Cancelamentos de RP, testes finais |
| **30 de Dezembro (22h)** | Pré-Virada | Transferência Diária programada |
| **31 de Dezembro → 01 de Janeiro** | Virada | Operação simultânea dos dois bancos |
| **02 de Janeiro em diante** | Pós-Virada | Ajustes finais, início das operações do novo exercício |

### Anexo B - Checklist de Conferência Pré-Virada

**Banco de Encerramento:**
- [ ] Todos os bloqueios do Decreto estão ativados
- [ ] RPP Prescrito de 5 anos está cancelado
- [ ] RPNP dos Poderes está cancelado
- [ ] PDs de RPP canceladas estão anuladas
- [ ] Bloqueio geral de contabilizações está ativo

**Banco de Abertura:**
- [ ] Tabelas de apoio inicializadas
- [ ] DEPARA Contábil configurado
- [ ] Tipo de Encerramento no Plano de Contas conferido
- [ ] Tabelas de Ação e Programa carregadas
- [ ] Agendamento da Transferência Diária ativado (22h do dia 30/12)
- [ ] Agendamento de Migração de Tabelas ativado
- [ ] Regras de compatibilidade ativadas:
  - [ ] RC 361 (Execução de PDs de RPP antes da inscrição)
  - [ ] RC 296 (Impedir pagamento de RPP cancelado por prescrição)
  - [ ] RC 360 (Impedir PDs e OBs de Regularização)
- [ ] Bloqueios de funcionalidade configurados
- [ ] FlexVision com views históricas atualizadas (ainda não apontado)

**Conferências:**
- [ ] Saldos contábeis conferidos (Encerramento x Abertura)
- [ ] Migração de tabelas validada
- [ ] Migração de documentos validada
- [ ] Erros da Transferência Diária analisados

### Anexo C - Checklist Pós-Virada

**Dia 02 de Janeiro:**
- [ ] FlexVision apontado para o novo exercício
- [ ] Bloqueios específicos do exercício de encerramento ativados:
  - [ ] Bloquetos e Faturas
  - [ ] DOMBANS
  - [ ] LISTAS
- [ ] Bloqueios específicos do exercício de abertura ativados:
  - [ ] COMUNICAS
  - [ ] Inscrições Genéricas
  - [ ] Credores
  - [ ] Convênios
  - [ ] Contratos
- [ ] Script de GDs executado
- [ ] Operações financeiras do novo exercício iniciadas

**Durante o Período de Inscrição de RP (até conclusão):**
- [ ] Acompanhamento diário das operações simultâneas
- [ ] Monitoramento de inconsistências
- [ ] Suporte aos órgãos para dúvidas e problemas

**Após Conclusão da Inscrição de RP:**
- [ ] Banco de encerramento praticamente fechado (sem ajustes orçamentários pendentes)

### Anexo D - Checklist Cronograma SATI 2025/2026

**26/12 – Preparação Inicial (TI/SATI & SUBCONT)**
- [ ] Criar o banco 2026 com todas as estruturas habilitadas.
- [ ] Remover a opção “gerar GD” na funcionalidade “Retorno de Ordem Bancária” logo após a inicialização das tabelas de 2025.

**29/12 – Transferências e Ajustes (TI/SATI & SUBCONT)**
- [ ] Ligar a Transferência Diária garantindo que os saldos das PDs não migrem até o dia 31.
- [ ] Solicitar a inclusão do novo ano nas consultas do Flexvision.
- [ ] Atualizar as views históricas para o exercício de 2025.
- [ ] Realizar o apontamento das views para 2025 após autorização da SUBCONT.

**31/12 (manhã) – Execução Crítica (Time SIAFE & SUBCONT)**
- [ ] Rodar o script para ativar os programas de trabalho antes dos processos de encerramento.
- [ ] Rodar o script para inativar os programas de trabalho após os processos.
- [ ] Ativar a migração de PDs no Depara Contábil e carregar os documentos necessários.
- [ ] SUBCONT confirmar o cancelamento dos Restos a Pagar conforme comunicado.

---

## Cronograma de Encerramento com a SATI

### Visão Geral

Referência operacional para a virada 2025→2026, com foco nas atividades que precisam ser executadas a partir de 26/12. Utilize este roteiro em conjunto com as demais seções do manual e com as orientações emitidas pela SUBCONT/SUGESC.

### 1. Criar o Banco 2026
**PASSO 1 – 26/12 – Criar o Banco 2026**

- Criar o banco do exercício de 2026 e garantir a disponibilização de todas as estruturas necessárias no ambiente de banco de dados.

### 2. Retorno de OBs
**PASSO 2 – 26/12 – Ajustar o “Retorno de Ordem Bancária”**

- Remover a opção **“gerar GD”** da funcionalidade **“Retorno de Ordem Bancária”** no exercício de 2025, logo após a inicialização das tabelas desse exercício.
- *Responsável indicado: Time SIAFE (execução via script no banco de dados).*

### 3. Transferência Diária
**PASSO 3 – 29/12 – Ligar a Transferência Diária**

- Ativar a Transferência Diária, garantindo que **os saldos das PDs não sejam migrados até o dia 31** (SUBCONT atualiza as contas afetadas).
- Solicitar, ainda no dia **29/12**, a inclusão do **“novo ano”** nas opções de consulta do **Flexvision**.

### 4. Apontamento e views históricas
**PASSO 4 – 29/12 – Views históricas e apontamento**

1. Atualizar as **views históricas** em 29/12/2025.
2. Realizar o **apontamento para o exercício de 2025**, aguardando a solicitação formal da SUBCONT antes da execução.

**Janela crítica de 31/12:** entre 7h e 8h da manhã a SUBCONT executa os processos de encerramento. Coordene qualquer intervenção junto ao time responsável antes desse período.

### 5. Scripts para programas de trabalho
**PASSO 5 – 31/12 (manhã) – Scripts para programas de trabalho**

1. Rodar o script (Time SIAFE) para **ativar os programas de trabalho** antes do processo (ambiente de banco de dados).
2. Rodar o script (Time SIAFE) para **inativar os programas de trabalho** após a conclusão do processo (ambiente de banco de dados).

### 6. Migração de PDs no Depara Contábil
**PASSO 6 – 31/12 (manhã) – Migração de PDs no Depara Contábil**

- Ativar a migração de PDs no **Depara Contábil**, assegurando o correto carregamento dos documentos (SUBCONT).

### 7. Cancelamento de RPs
**PASSO 7 – 31/12 (manhã) – Cancelamento de RPs**

- SUBCONT realiza o **cancelamento dos Restos a Pagar (RPs)** conforme orientações de encerramento.
