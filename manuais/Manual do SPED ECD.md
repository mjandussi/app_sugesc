# Manual SPED ECD – Passo a Passo para Atualização e Geração

---

## Introdução e Contexto

### Objetivo
Este manual orienta a SUBCONT/SUGESC na atualização dos dados cadastrais e contábeis no SIAFE-Rio, permitindo que as Empresas Públicas e Sociedades de Economia Mista gerem o arquivo para importação no programa SPED ECD.

**Pré-requisito de Testes:**
Para realização dos testes, é necessário que o **banco Beta** do Ano Calendário da Declaração continue sendo atualizado até o fim das validações.

---

## Passo 1: Atualização Cadastral (Parâmetros SPED)

### Solicitação de Dados aos Órgãos
A SUBCONT deve solicitar aos órgãos (Empresas Públicas e Sociedades de Economia Mista) o envio dos dados cadastrais atualizados via Processo SEI.

**Dados necessários:**
* Número do Livro Diário
* Dados do Contador Responsável
* Dados do Representante Legal

**Caminho no SIAFE-Rio:**
`Administração > Configuração > Parâmetros Arquivo SPED > Inserir`

[Tela Parâmetros Arquivo SPED](../imagens/Manual_SPED_ECD/parametros_sped_inserir.png)

> **Controle Administrativo:** Recomenda-se criar uma planilha para controlar o recebimento dos processos SEI enviados pelos órgãos.

---

## Passo 2: Migração do Plano de Contas Referencial

Deve-se migrar a tabela do Plano de Contas Referencial do exercício anterior para o corrente (ex: de 2021 para 2022).

**Procedimento:**
1.  Acesse: `Administração > Migração de Dados > Migração de Tabelas`.
2.  Execute a migração da tabela específica.

> **Nota Técnica:** Caso a tabela não migre automaticamente, solicitar abertura de ISSUE ao setor de TI.

---

## Passo 3: Regra de Mapeamento (Contas Referenciais)

Esta é a etapa mais crítica e envolve a correlação entre a Conta Contábil do SIAFE e a Conta Referencial da Receita Federal.

### 3.1. Criar/Atualizar a Regra
1.  **No Exercício Corrente:** Acesse `Administração > Estrutura Classificatória > Regras de Mapeamento`.
2.  Crie ou edite a regra **“Mapeamento de Conta Contábil e Conta Referencial”**.

[Tela Regras de Mapeamento](../imagens/Manual_SPED_ECD/regras_mapeamento_lista.png)

### 3.2. Exportar e Preparar o Layout (Template)
Para facilitar, exporte a regra do exercício anterior e use como base:
1.  Vá ao **Exercício Anterior**.
2.  Acesse a regra de mapeamento e clique em **Exportar**.
3.  Será gerado um arquivo Excel (Template).

**Validação de Novas Contas (PROCV):**
Antes de importar no exercício atual, faça um cruzamento (PROCV) entre:
* O Plano de Contas do Exercício Corrente (filtrado por Analíticas Ativas/Inativas).
* A planilha exportada do ano anterior.

**Objetivo:** Identificar contas novas que precisam ser incluídas na planilha com seus respectivos códigos de contas referenciais (disponíveis nas tabelas dinâmicas do SPED - Blocos L100A e L300A).

### 3.3. Importação e Tratamento de Erros (Contas Inativas)
Ao importar a planilha atualizada no exercício corrente (`Botão Importar`), o sistema pode apresentar erros de **"Conta não encontrada"**.

[Tela de Erro na Importação](../imagens/Manual_SPED_ECD/erro_importacao_contas.png)

**Causa:** O erro geralmente ocorre porque as contas contábeis estão com status **"Inativo"** no sistema.

**Procedimento de Correção (Checklist):**

1.  Copie a lista de contas com erro apresentada na tela.
2.  Cole em uma planilha Excel para controle (Use a ferramenta de exportação abaixo).
3.  Acesse `Execução > Contabilidade > Plano de Contas`.
4.  Filtre cada conta, clique em **Alterar** e mude o status para **ATIVA**.
5.  Repita a importação da planilha de mapeamento.
6.  Após o sucesso da importação e validação do arquivo TXT final, **INATIVE** as contas novamente.

[Planilha de Controle de Erros de Contas](DATA_CONTROLE_ERROS_SPED)

---

## Passo 4: Atualização de Software e Layout

1.  Baixe ou atualize o programa **SPED Contábil** (PVA) no site da Receita Federal (`sped.rfb.gov.br`).
2.  Solicite à TI a atualização do layout no SIAFE-Rio caso tenha havido mudanças legais.

---

## Passo 5: Geração e Validação do Arquivo TXT

### 5.1. Gerar Arquivo no SIAFE
**Caminho:** `Execução > Contabilidade > Geração SPED`

Preencha os filtros:
* Órgão
* Ano e Período (Anual)
* Clique em **Gerar** e depois **Download**.

[Tela Geração SPED](../imagens/Manual_SPED_ECD/geracao_sped_filtro.png)

### 5.2. Validar no PVA (Programa Validador)
1.  Abra o SPED Contábil.
2.  Vá em `Arquivo > Escrituração Contábil > Importar`.
3.  Selecione o TXT baixado do SIAFE.
4.  Execute a validação.

**Análise de Resultados:**
* **Advertências:** Geralmente aceitáveis (ex: "Não houve recuperação da ECD anterior"). Não impedem o envio.
* **Erros:** Impeditivos. Devem ser analisados pela SUGESC.

> **Dica de Validação:** Antes de liberar para o órgão, verifique se a **DRE** apresentada no arquivo coincide com a consulta de DRE no **FlexVision**.

### 5.3. Liberação para o Órgão
Após validar e garantir que não há erros impeditivos:
1.  Envie **Comunica** autorizando o órgão a gerar o arquivo definitivo.
2.  O órgão é responsável pelo envio à Receita Federal.

---

## Anexos

### Checklist de Fechamento SPED

- [ ] Dados cadastrais atualizados (Contador/Representante)
- [ ] Plano de Contas Referencial migrado
- [ ] Regra de Mapeamento atualizada e importada
- [ ] Contas inativas ativadas temporariamente para importação
- [ ] Arquivo TXT gerado e validado no PVA (sem erros)
- [ ] DRE do SPED batida com FlexVision
- [ ] Comunica de autorização enviado ao órgão