# Manual de Cadastro e Conformidade de Usuários

---

## 1. Introdução

[cite_start]A nova sistemática do cadastramento de usuários de forma descentralizada visa, não apenas substituir os formulários de solicitações de acesso ao sistema em papel, mas principalmente que o cadastro, alterações e a conformidade de usuários fiquem sob a responsabilidade do respectivo gestor do Órgão ou Unidade Gestora[cite: 62].

[cite_start]Com isso, todo o processo será realizado de forma eletrônica no próprio sistema e com os respectivos registros gravados nos históricos das transações[cite: 63]. [cite_start]Cabendo agora ao Órgão Central, tendo em vista o objetivo de garantir a segurança e os procedimentos do sistema, apenas as aprovações finais[cite: 64].

[cite_start]O objetivo é oferecer aos Gestores de Usuários um suporte documental, por meio do qual serão disponibilizadas informações sobre a execução dos procedimentos no Sistema Integrado de Administração Financeira do Estado do Rio de Janeiro - SIAFE-Rio 2[cite: 40].

[cite_start]Este Manual trata dos principais procedimentos relacionados ao cadastramento e a conformidade de usuários no SIAFE-Rio 2, não esgotando o assunto, sendo que outras informações encontram-se na PORTARIA CGE Nº 204 DE 12 DE ABRIL DE 2017[cite: 41].

---

## 2. Conceitos

Para a correta operação do sistema, é fundamental compreender os seguintes conceitos:

### Gestor Responsável
[cite_start]Usuário que estará na hierarquia superior, responsável por incluir, alterar e excluir os usuários das suas respectivas unidades, determinando os perfis e níveis de acesso em que os usuários poderão ser habilitados[cite: 67]. [cite_start]Além disso, será o responsável pela realização da conformidade de usuários no sistema[cite: 68].

### UG Limbo - UG 299999
[cite_start]Unidade Gestora utilizada somente para alocar os usuários que estão inativos por desligamento, exceto por falecimento[cite: 70]. [cite_start]Somente será possível fazer uma solicitação de transferência se o usuário estiver na UG limbo[cite: 71].

### Chave Eletrônica
[cite_start]Funcionalidade que tem por finalidade a geração de um token, após informar o Nome, E-mail e CPF de um novo usuário do sistema[cite: 73]. [cite_start]O token será utilizado pelo novo usuário para completar o seu cadastro[cite: 74]. [cite_start]Deverá ser gerado pelo seu Gestor Responsável no sistema Security e tem validade de sete dias corridos[cite: 75].

### Órgão Central
São os usuários da SEFAZ (SUGESC). Têm o poder de aprovar/recusar as solicitações de inclusão/alteração de acordo com as suas avaliações. [cite_start]Também possuem a atribuição de alterar o gestor responsável de uma solicitação, se necessário[cite: 77, 78].

---

## 3. Cadastro de Novos Usuários

### 3.1 Geração do Token pelo Gestor

O Gestor de Usuários deverá acessar o Banco Security pelo endereço:
[cite_start]`https://siafe2-security.fazenda.rj.gov.br/Security/faces/login.jsp`[cite: 87, 90].

1.  [cite_start]No sistema Security, deverá selecionar a Transação "Chave Eletrônica" e clicar em "Gerar Token"[cite: 91].
2.  O sistema abrirá a tela para inserção dos dados gerais.
3.  [cite_start]Terá que preencher os dados solicitados (**Nome**, **E-mail** e **CPF** do novo usuário) e clicar em "Salvar"[cite: 98].

[Tela de Inserir Chave Eletrônica - Token](../imagens/cadastro_token_security.png)

> [cite_start]**OBS:** só serão permitidos e-mails institucionais[cite: 99].

### 3.2 Continuação do cadastro pelo novo usuário

[cite_start]O sistema automaticamente irá gerar o Token, com o envio automático deste número para o e-mail do novo usuário[cite: 101].

**Exemplo de e-mail recebido:**
> [cite_start]"Prezado(a), Foi gerado o seguinte Token (...) no ambiente de produção do sistema SiafeRio. Favor proceder com a Solicitação de Cadastro de Usuário."[cite: 107, 108].

**Procedimentos do Novo Usuário:**

1.  [cite_start]O novo usuário deverá entrar no SIAFE-Rio 2 (`https://siafe2.fazenda.rj.gov.br/Siafe/faces/login.jsp`), digitar o CPF e clicar no botão "**Solicitar Acesso**"[cite: 119].
2.  De posse do e-mail recebido, copiar o Token e colar no campo "Token". [cite_start]Depois, clicar no botão "**validar**"[cite: 127].
3.  [cite_start]Após a validação do Token, o novo usuário deverá preencher os demais campos relativos ao seu cadastro e clicar no botão "**Confirmar**"[cite: 148].

[Tela de Solicitação de Cadastro de Usuário - Validação Token](../imagens/cadastro_usuario_validacao.png)

> [cite_start]**OBS:** todos os campos com asterisco são obrigatórios, sendo que para contadores, apesar do campo "CRC" não ser obrigatório, o Órgão Central só irá validar perfis de contadores com o respectivo preenchimento do CRC[cite: 149].

### 3.3 Finalização do Cadastro por parte do Gestor

[cite_start]Após o preenchimento do cadastro pelo novo usuário, o Gestor receberá um e-mail informando sobre a solicitação de acesso ("Favor realizar a análise e submeter a solicitação para Aprovação")[cite: 184, 192].

De posse da informação do e-mail, o Gestor de Usuários deverá acessar o SIAFE-Rio 2 no seguinte caminho:
[cite_start]**Administração > Segurança > Solicitação de Cadastro de Usuário**[cite: 194].

> [cite_start]**OBS:** Neste momento, o Status da Solicitação estará como "em análise"[cite: 195].

[cite_start]O Gestor deverá selecionar o usuário e clicar no botão "**Alterar**" para navegar pelas abas de configuração[cite: 196].

[Tela de Listagem de Solicitações](../imagens/lista_solicitacoes_analise.png)

#### 3.3.1 Aba Dados do Solicitante (1ª Aba)
São os dados que já foram preenchidos pelo usuário no momento do cadastro. [cite_start]Ao Gestor, cabe apenas preencher a questão da permissão de acesso a exercícios anteriores (**Deseja conceder acesso a exercícios anteriores? Sim/Não**)[cite: 255, 293].

#### 3.3.2 Aba Grupos (2ª Aba)
[cite_start]O Gestor de Usuários deverá atribuir as funcionalidades do perfil dele (estarão no quadro da esquerda - "Disponíveis") para o novo usuário (ficarão no quadro da direita - "Selecionados")[cite: 295].

[Tela da Aba Grupos](../imagens/aba_grupos.png)

> **OBS:** O ideal é que o Gestor de Usuários possua um perfil amplo para poder delegar. [cite_start]Consulte a Tabela de Grupos de Funcionalidades na seção 6 deste manual[cite: 342, 343].

#### 3.3.3 Aba Hierarquias (3ª Aba)
[cite_start]O Gestor de Usuários irá informar em qual hierarquia o novo usuário será alocado[cite: 345]. [cite_start]Na maioria dos casos, o Gestor terá apenas uma UG na qual ele é o superior hierárquico, porém, nada impede que ele seja o Gestor de mais de uma UG[cite: 346, 347].

#### 3.3.4 Aba Perfil de Execução (4ª Aba)
[cite_start]Nesta aba, são disponibilizadas as UGs que o usuário terá visibilidade para execução e consultas no SIAFE-RIO 2. O Gestor deve selecionar as UGs e informar obrigatoriamente o campo **Unidade Gestora Principal**[cite: 384, 385].

[Tela da Aba Perfil de Execução](../imagens/aba_perfil_execucao.png)

#### 3.3.5, 3.3.6 e 3.3.7 (Abas de Planejamento e Programas)
* [cite_start]**Perfil de Planejamento:** Não aplicável no momento[cite: 425].
* [cite_start]**Coordenação de Ação:** Não aplicável no momento[cite: 440].
* [cite_start]**Gerente de Programa:** Não aplicável no momento[cite: 463].

#### 3.3.8 Aba Situação Cadastral (8ª Aba)
[cite_start]É a última aba, onde o Gestor de Usuários deverá **Validar** ou **Excluir** a solicitação deste novo usuário[cite: 484].

1.  Selecione a opção **Validar Solicitação**.
2.  Clique em **Confirmar**.

[Tela da Aba Situação Cadastral](../imagens/aba_situacao_cadastral.png)

### 3.4 e 3.5 Validação pelo Órgão Central

**3.4 Validação Positiva:**
Após a confirmação do cadastro pelo Gestor, o Órgão Central (SUGESC/SEFAZ) deverá validar o cadastro. [cite_start]Com a validação positiva, o novo usuário receberá uma **Senha de Acesso ao SIAFE-Rio 2 por e-mail**[cite: 523, 525].

**3.5 Validação Negativa:**
[cite_start]Se a solicitação for rejeitada pelo Órgão Central, o Gestor de Usuários receberá um e-mail com o motivo da rejeição (Ex: "Motivo: ALTERAR UG PARA 120100")[cite: 527, 529].
* [cite_start]O Gestor deverá realizar a alteração apontada na solicitação, clicar em "Pendência Resolvida" e confirmar[cite: 530, 736].
* [cite_start]Feita a alteração, o Órgão Central validará novamente[cite: 553].

---

## 4. Alteração de Usuários

O Gestor de Usuários irá realizar a solicitação de alteração no caminho:
[cite_start]**Administração > Segurança > Solicitação de Cadastro de Usuário**[cite: 556].

Ao incluir uma nova solicitação (botão "Inserir"), é possível escolher os seguintes Tipos:
* Solicitação de Alteração
* Solicitação de Reativação
* Solicitação de Desligamento
* [cite_start]Solicitação de Transferência[cite: 640].

[Tela de Tipos de Solicitação](../imagens/tipos_solicitacao.png)

### 4.1 Solicitação de Alteração

[cite_start]Neste tipo de solicitação, o Gestor de Usuários poderá alterar os dados de todas as abas do perfil do usuário (com exceção do nome)[cite: 673].

1.  O Gestor aperta o botão **Inserir**.
2.  [cite_start]Escolhe o Tipo **Solicitação de Alteração** e digita o CPF do usuário[cite: 674].
3.  [cite_start]Após realizar as alterações necessárias (em grupos, UGs, hierarquias, etc.), aperta o botão **Confirmar**[cite: 675].
4.  [cite_start]O Cadastrador-Geral (Órgão Central) irá aprovar ou rejeitar a solicitação[cite: 710].

### 4.2 Solicitação de Reativação

[cite_start]Somente podem ser reativados os usuários que estiverem **inativos por desuso** ou **inativos por inconformidade** (não é possível alterar nenhum dado do usuário neste processo)[cite: 787].

1.  [cite_start]O Gestor escolhe o Tipo de Solicitação **Reativação**[cite: 788].
2.  Digita o CPF do usuário e confirma.
3.  [cite_start]Se tentar reativar um usuário que esteja com status diferente (ex: apenas "Inativo"), o sistema apresentará erro[cite: 866].
4.  [cite_start]Após aprovação do Cadastrador-Geral, o status será alterado para **Ativo**[cite: 814].

### 4.3 Solicitação de Desligamento

Utilizado para encerrar o acesso de um usuário. [cite_start]O campo **Motivo do Desligamento** apresentará opções como: Aposentadoria, Encerramento da Tarefa, Exoneração, Falecimento, Movimentação entre UGs, etc.[cite: 891].

1.  O Gestor escolhe o Tipo **Solicitação de Desligamento**.
2.  [cite_start]Seleciona o Motivo e confirma[cite: 936].

**Consequências:**
* [cite_start]**Exceção Falecimento:** Usuário continua com grupos e perfil, status muda para "Inativo por Desligamento"[cite: 935].
* [cite_start]**Demais casos:** O usuário terá o perfil institucional e todos os grupos removidos e será incluído na **UG Limbo 299999** (saindo da hierarquia da antiga UG)[cite: 933]. Status muda para "Inativo por Desligamento".

[Tela de Solicitação de Desligamento](../imagens/solicitacao_desligamento.png)

### 4.4 Solicitação de Transferência

[cite_start]Utilizada para transferir um usuário que esteja desligado do sistema (na UG Limbo), por exemplo, um servidor transferido entre UGs[cite: 976, 977].

**Fluxo:**
1.  [cite_start]O **antigo gestor** faz a Solicitação de Desligamento (Motivo: Movimentação entre UGs)[cite: 978].
2.  [cite_start]O **novo gestor** faz a Solicitação de Transferência[cite: 979].

**Procedimento:**
1.  O novo gestor insere solicitação do tipo **Transferência**.
2.  [cite_start]O campo "Ativar" deve ser obrigatoriamente preenchido[cite: 982].
3.  [cite_start]Como o perfil foi removido no desligamento, o novo Gestor deve atribuir o novo perfil (Grupos, Hierarquias, etc.)[cite: 981].
4.  **Atenção:** Na aba Perfil de Execução, a UG Principal virá como 299999. O Gestor deve **remover a 299999 e incluir a nova UG Principal correta**. [cite_start]Se esquecer, o Órgão Central rejeitará a solicitação[cite: 1049, 1052].

---

## 5. Conformidade de Usuários

### 5.1 Realização da Conformidade

A Conformidade de usuários é um procedimento periódico obrigatório.
[cite_start]Caminho: **Administração > Segurança > Conformidade de Usuários**[cite: 1056].

1.  [cite_start]O Gestor deve clicar no botão "**Inserir**"[cite: 1057].
2.  [cite_start]Selecionar a Unidade Gestora pela qual é responsável[cite: 1080].
3.  [cite_start]Aparecerá a relação dos usuários sob sua hierarquia[cite: 1097].
4.  O Gestor marca os usuários para dar conformidade e clica em **Confirmar**.
5.  A conformidade pode ser parcial. [cite_start]Caso seja feita apenas de parte, o sistema informará a quantidade de usuários pendentes[cite: 1121].

[Tela de Realização de Conformidade](../imagens/tela_conformidade.png)

### 5.2 Inativação por falta de Conformidade

[cite_start]Conforme a Portaria CGE Nº 204/2017, o prazo para realização é de **07 dias corridos** após as datas trimestrais (01 de Janeiro, 01 de Abril, 01 de Julho e 01 de Outubro)[cite: 1165].

[cite_start]Após a expiração deste prazo, se a Conformidade não for realizada pelo Gestor, os seus respectivos usuários serão **Inativados no sistema** (Status: Inativo por Inconformidade)[cite: 1166].

**Como resolver (Reativação):**
O Gestor deverá ir em "Solicitação de Cadastro de Usuário", clicar em Inserir, escolher a opção "**Solicitação de Reativação**" e digitar o CPF do usuário. [cite_start]Após aprovação do Órgão Central, o usuário volta a ser Ativo[cite: 1208, 1227].

---

## 6. Outras Orientações

### 6.1 Tabela de Informações da Senha

| Parâmetro | Valor |
| :--- | :--- |
| Tamanho mínimo da senha | 5 |
| Tamanho máximo da senha | 20 |
| Quantidade de dias para expiração da senha | 120 |
| Quantidade de dias para desativação do usuário por desuso | 45 |
| Número de tentativas consecutivas de login incorreto para bloqueio | 3 |

[cite_start][cite: 1230]

### 6.2 Tabela dos Grupos de Funcionalidades

[cite_start]Abaixo, a lista dos principais grupos de funcionalidades disponíveis para atribuição aos usuários[cite: 1240, 1249]:

| Grupos | Funcionalidades |
| :--- | :--- |
| **ALERJ** | Perfil próprio dos Usuários da ALERJ (com diversas funcionalidades) |
| **ASCONTABIL / COORDSECCIONAL** | Diversas funcionalidades próprias dos assessores e coordenadores da Contabilidade do Órgão |
| **AUDITORIA** | Perfil próprio dos Usuários da AGE (com diversas funcionalidades) |
| **COD-BARRAS** | Cadastrar Código de Barras |
| **Compartilhamento Global de Consultas do Flexvision** | Executar consultas / Forçar a execução de consultas online |
| **CONCILIAÇÃO BANCÁRIA** | Cadastrar Conciliação Bancária Mensal |
| **CONFORMIDADE CONTABIL / CONFORMIDADE DIARIA** | Cadastrar e Visualizar Conformidade Contábil / Realizar Análise Boletim de RP e Verificar Procedimentos para Inscrição de RP / Cadastrar e Visualizar Conformidade Diária |
| **CONSULTA BOLETIM DE RP** | Verificar Procedimentos para Inscrição de RP |
| **CONSULTAS** | Visualização a diversas transações no SIAFERIO / Enviar, Excluir e Consultar mensagem pelo Comunica / Emitir Balancete, Razão, Diário e Detalhamento Conta Contábil |
| **CONTDRTC** | Cadastrar Conciliação Bancária Mensal / Cadastrar Nota de Empenho / Cadastrar Nota Patrimonial |
| **CONTRATOS** | Cadastrar e Visualizar Contrato / Permite realizar a alteração dos dados da tipificação do contrato |
| **CONTSECCIO** | Cadastrar Detalhamento da Dotação / Incluir Pessoa Física e Pessoa Jurídica / Executar Regra de Validação Contábil |
| **CONVÊNIOS** | Cadastrar e Registrar Convênio / Cadastrar Detalhamento da Dotação / Reativar Convênios Excluídos |
| **CREDOR** | Incluir Pessoa Física e Procedimento de Pagamento / Incluir Pessoa Jurídica e Procedimento de Pagamento |
| **DETAFONTE** | Cadastrar Detalhamento da Dotação |
| **DL/NL** | Cadastrar e Anular Nota de Liquidação - Cadastrar Guia de Recolhimento - Cadastrar Nota de Aplicação e Resgate - Cadastrar e Anular Nota Patrimonial |
| **EMPENHO1** | Cadastrar e Anular Nota de Empenho - Cadastrar e Anular Nota Patrimonial |
| **EXEPD** | Executar Programação de Desembolso - Cadastrar Guia de Devolução - Anular e Imprimir Registro de Envio - Imprimir a Relação de Envio |
| **FLEXVISION CRIAÇÃO DE CONSULTAS** | Cadastrar e Executar consultas |
| **FORÇAR EXECUÇÃO ONLINE** | Forçar a execução de consultas online |
| **GESTOR DE CONTRATOS / GESTORPROJ** | Editar Contrato / Cadastrar e Manter Projetos |
| **IMPORTAREL / IMPORTSPED** | Executar consultas / Cadastrar Empresa MANAD |
| **ÍNDICES CONSTITUCIONAIS (SAÚDE, EDUCAÇÃO, FAPERJ, FECAM, FECP, FEHIS, FUNDEB)** | Executar relatórios gerenciais específicos no âmbito de todas as Unidades Gestoras |
| **LISTAOB / LISTAPD** | Visualizar PDs e OBs (de todos os tipos) / Visualizar Acompanhamento de Execução de PDs |
| **MODULO DEA** | Cadastrar Despesa Exercício Anterior |
| **NL/NP** | Cadastrar Guia de Recolhimento / Nota de Aplicação e Resgate / Nota Patrimonial / Cadastrar e Contabilizar DEA |
| **NOTA DE DESCENTRALIZAÇÃO DE CRÉDITO** | Cadastrar Nota de Descentralização de Crédito / Cadastrar Nota Patrimonial |
| **OBINTRA / OBLISTA** | Cadastrar Ordem Bancária de Transferência / Cadastrar lista favorecido OB |
| **ORCAMENTO** | Perfil próprio dos Usuários da SEPLAG |
| **PAGA-IND / PD** | Executar e Filtrar Programação de Desembolso / Anular OB / Cadastrar PD e Guia de Devolução |
| **TCE / TESOURO** | Perfis próprios dos Usuários do TCE e TESOURO |
| **TIPO CONCILIAÇÃO BANCÁRIA** | Cadastrar Tipo Conciliação Bancária / Conciliar Ordem Bancária |

> [cite_start]**Dúvidas?** Devem ser encaminhadas preferencialmente através de Mensagem COMUNICA (UG 200299-SUGESC) ou telefones de contato (2334-4606 / 2334-4323)[cite: 42, 1251, 1260].