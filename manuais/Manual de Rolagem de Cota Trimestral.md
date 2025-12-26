# Manual de Rolagem de Cota (Trimestral)

---

## Introdução e Conceitos

### Por que realizar a rolagem?
A rolagem das cotas de LME (Limite de Movimentação e Empenho) entre trimestres é realizada para dois fins principais:

1.  [cite_start]**Controle da Execução Orçamentária:** Permite que os saldos não utilizados em um determinado trimestre sejam transferidos para o seguinte, assegurando a continuidade da execução e evitando a perda de limite disponível para empenho[cite: 336, 337].
2.  [cite_start]**Compatibilização Financeira:** Alinha os limites de empenho à disponibilidade financeira, garantindo conformidade com restrições legais e operacionais[cite: 338].

### Cronograma dos Trimestres

A rolagem deve ser observada nas seguintes datas de corte:

* [cite_start]**1° Trimestre:** 01 de Janeiro (Vem carregado na carga inicial do orçamento) [cite: 340]
* [cite_start]**2° Trimestre:** 01 de Abril [cite: 341]
* [cite_start]**3° Trimestre:** 01 de Julho [cite: 342]
* [cite_start]**4° Trimestre:** 01 de Outubro [cite: 342]

> [cite_start]**Quando Executar:** A rolagem só pode ser efetuada quando a SEPLAG solicitar OU, caso não peça, quando o mês de extração dos saldos estiver fechado[cite: 344].

> [cite_start]**Atenção:** Realizar teste no ambiente BETA no 1º dia do trimestre antes de executar em produção[cite: 346].

---

## Fase 1: Configuração e Execução (Conta 8)

### 1. Configuração dos Eventos (Conta 8)

O primeiro passo é configurar os eventos complementares do **Processo Contábil nº 06** para transferir os saldos da conta **8.2.3.1.2.01.01** (Cotas de LME Publicadas a Liberar).

[cite_start]**Caminho:** `Execução > Contabilidade > Evento` [cite: 351]

#### Ajuste do Evento 880771 (Baixa)
1.  [cite_start]Localize o evento **880771** e clique em alterar[cite: 352].
2.  **Aba Roteiro Contábil:**
    * Insira a conta `823120101` a **DÉBITO**.
    * [cite_start]Exclua a conta que estiver no crédito[cite: 353].
3.  **Aba Classificação da UG1:**
    * Selecione o **Trimestre ATUAL** (aquele que se pretende zerar o saldo).
    * [cite_start]*Exemplo:* Se estamos em Abril, selecione "1º Trimestre" [cite: 354-356].
4.  Confirme a alteração.

[Tela Configuração Evento 880771 - Conta 8](../imagens/Manual_Rolagem_Cota/evento_880771_conta8.png)

#### Ajuste do Evento 880772 (Acréscimo)
1.  [cite_start]Localize o evento **880772** e clique em alterar[cite: 359].
2.  **Aba Roteiro Contábil:**
    * Insira a conta `823120101` a **CRÉDITO**.
    * [cite_start]Exclua a conta que estiver no débito[cite: 360].
3.  **Aba Classificação da UG1:**
    * Selecione o **PRÓXIMO Trimestre** (aquele que receberá o saldo).
    * [cite_start]*Exemplo:* Se estamos em Abril, selecione "2º Trimestre" [cite: 361-363].
4.  Confirme a alteração.

[Tela Configuração Evento 880772 - Conta 8](../imagens/Manual_Rolagem_Cota/evento_880772_conta8.png)

---

### 2. Configuração do Processo Contábil (Conta 8)

Antes da execução, é necessário ajustar o **Processo Contábil 06**.

[cite_start]**Caminho:** `Execução > Contabilidade > Processo Contábil` [cite: 370]

1.  [cite_start]Localize o processo **06** e clique em alterar[cite: 371].
2.  **Alteração de Nome:** Atualize o nome para identificar os trimestres envolvidos.
    * [cite_start]*Exemplo:* "Rolagem de Cotas de LME publicadas - do 1º Trimestre para o 2º Trimestre – SUGESC"[cite: 372, 373].
3.  **Aba Conta de Extração:**
    * [cite_start]Insira a conta `823120101` (Cotas de LME Publicadas a Liberar)[cite: 378].
4.  **Aba Regra de Extração:**
    * Informe a regra para filtrar o trimestre que será zerado.
    * *Fórmula:* `[Trimestre].[Código] = X` (Onde X é o número do trimestre atual/anterior).
    * [cite_start]*Exemplo:* `[Trimestre].[Código] = 1`[cite: 379, 380].
5.  [cite_start]Confirme a alteração[cite: 381].

[Tela Configuração Processo 06 - Conta 8](../imagens/Manual_Rolagem_Cota/processo_06_conta8.png)

---

### 3. Execução e Validação (Conta 8)

[cite_start]**Caminho:** `Execução > Contabilidade > Execução de Processos Contábeis` [cite: 384]

1.  **Tipo de Processo:** Encerramento.
2.  **Processo Contábil:** 06.
3.  [cite_start]**Data Emissão:** 1º dia do novo trimestre (Ex: 01/04/2025)[cite: 387, 388].
4.  [cite_start]Selecione as Unidades Gestoras e clique em **Executar**[cite: 389, 390].
5.  [cite_start]Verifique o LOG de processamento[cite: 393].

**Validação no Balancete:**
1.  [cite_start]Acesse `Execução > Contabilidade > Emitir Balancete`[cite: 395].
2.  [cite_start]Filtre pela conta `823120101` e clique em **Detalhamento de Conta**[cite: 397].
3.  [cite_start]Verifique se o conta corrente final termina com o dígito do novo trimestre (Ex: ".2")[cite: 399].
4.  [cite_start]Marque "Trazer Saldos Zerados" para confirmar que o trimestre anterior ficou zerado[cite: 400, 401].

[Tela Validação Balancete - Conta 8](../imagens/Manual_Rolagem_Cota/validacao_balancete_conta8.png)

---

## Fase 2: Configuração e Execução (Conta 7)

### 1. Configuração dos Eventos (Conta 7)

[cite_start]Repita o procedimento para a conta **7.2.3.1.1.01.01** (Controle das Cotas Publicadas)[cite: 402, 403].

[cite_start]**Caminho:** `Execução > Contabilidade > Evento` [cite: 406]

#### Ajuste do Evento 880771 (Baixa)
1.  Localize o evento **880771** e altere.
2.  **Aba Roteiro Contábil:**
    * [cite_start]Insira a conta `723110101` a **CRÉDITO**[cite: 408].
    * Exclua a conta anterior de débito.
3.  **Aba Classificação da UG1:**
    * Selecione o **Trimestre ATUAL** (que será zerado). [cite_start]Ex: "1º Trimestre" [cite: 409-411].

#### Ajuste do Evento 880772 (Acréscimo)
1.  [cite_start]Localize o evento **880772** e altere[cite: 412].
2.  **Aba Roteiro Contábil:**
    * [cite_start]Insira a conta `723110101` a **DÉBITO**[cite: 413].
    * Exclua a conta anterior de crédito.
3.  **Aba Classificação da UG1:**
    * Selecione o **PRÓXIMO Trimestre** (destino). [cite_start]Ex: "2º Trimestre" [cite: 414-416].

---

### 2. Configuração do Processo Contábil (Conta 7)

[cite_start]Ajuste novamente o **Processo Contábil 06** para a nova conta[cite: 421].

1.  [cite_start]Acesse o processo 06 (não precisa mudar o nome)[cite: 423].
2.  **Aba Conta de Extração:**
    * [cite_start]Altere a conta para `723110101`[cite: 425].
3.  **Aba Regra de Extração:**
    * [cite_start]Mantenha a regra do trimestre anterior (Ex: `[Trimestre].[Código] = 1`)[cite: 426, 427].
4.  [cite_start]Confirme[cite: 428].

[Tela Configuração Processo 06 - Conta 7](../imagens/Manual_Rolagem_Cota/processo_06_conta7.png)

---

### 3. Execução e Validação (Conta 7)

Execute novamente o processo para processar a conta 7.

1.  **Caminho:** `Execução de Processos Contábeis`.
2.  [cite_start]**Dados:** Mesma data de emissão (Ex: 01/04/2025) e UGs [cite: 432-437].
3.  [cite_start]Clique em **Executar**[cite: 438].

**Validação no Balancete:**
1.  [cite_start]Acesse o Balancete e filtre pela conta `723110101`[cite: 440].
2.  [cite_start]Verifique no detalhamento se o saldo migrou para o conta corrente final ".2" (ou correspondente ao novo trimestre)[cite: 445].
3.  [cite_start]Confirme se o trimestre anterior foi zerado[cite: 447].

[Tela Validação Balancete - Conta 7](../imagens/Manual_Rolagem_Cota/validacao_balancete_conta7.png)

---

## Resumo dos Lançamentos Contábeis

Para entender o fluxo completo da rolagem, desde a publicação pela SEPLAG até a rolagem pela SUGESC, consulte o resumo abaixo.

[Baixar Resumo Contábil da Rolagem](DATA_RESUMO_CONTABIL_ROLAGEM)

### Visão Geral do Fluxo SEPLAG vs SUGESC

1.  **Publicação (SEPLAG):** Nota Patrimonial (Evento 780013).
2.  **Liberação (SEPLAG):** Liberação de Cotas (Evento 880013).
3.  **Empenhamento (UGs):** Emissão de Empenhos (Evento 522920101).
4.  **Rolagem (SUGESC):** Transferência de saldos entre trimestres (Processo 06).

Para detalhes das contas D/C de cada etapa, exporte o arquivo Excel acima.