# 📘 Configuração do Banco de Dados PostgreSQL

Este guia explica como configurar o banco de dados PostgreSQL para versionamento de regras LME.

## 🎯 O que é versionado?

O sistema permite salvar "snapshots" das regras de LME (Limite de Movimentação e Empenho) para:
- ✅ Manter histórico de alterações
- ✅ Comparar versões diferentes (ANTES vs DEPOIS)
- ✅ Auditoria e rastreabilidade
- ✅ Reproduzir análises passadas

## 🗄️ Providers de PostgreSQL Gratuitos

Recomendamos usar um serviço gerenciado gratuito:

### 1. **Neon** (Recomendado) 🌟
- Site: https://neon.tech
- Plano Free: 500 MB
- Vantagens: Serverless, rápido, fácil setup
- Exemplo de URL:
```
postgresql+psycopg2://usuario:senha@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 2. **Supabase**
- Site: https://supabase.com
- Plano Free: 500 MB
- Vantagens: Interface web completa, backups automáticos
- Exemplo de URL:
```
postgresql+psycopg2://postgres:senha@db.abc123xyz.supabase.co:5432/postgres
```

### 3. **Railway**
- Site: https://railway.app
- Plano Free: $5 de crédito/mês
- Vantagens: Deploy integrado, fácil de usar

### 4. **ElephantSQL**
- Site: https://www.elephantsql.com
- Plano Free: 20 MB
- Vantagens: Simples e estável

## ⚙️ Configuração Passo a Passo

### 1. Criar conta no provider escolhido

Exemplo usando **Neon**:
1. Acesse https://neon.tech
2. Faça login com GitHub
3. Clique em "Create Project"
4. Escolha região (us-east-2 é mais rápido para Brasil)
5. Copie a Connection String

### 2. Configurar secrets no Streamlit

#### Desenvolvimento Local:

Crie o arquivo `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
db_url = "postgresql+psycopg2://seu_usuario:sua_senha@host:5432/banco"
```

**Exemplo real (Neon):**
```toml
db_url = "postgresql+psycopg2://neondb_owner:senha123@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

#### Deploy no Render:

1. Acesse o painel do Render
2. Vá em **Environment** → **Secret Files**
3. Adicione o arquivo `.streamlit/secrets.toml` com o conteúdo acima

OU

1. Vá em **Environment Variables**
2. Adicione:
   - Key: `db_url`
   - Value: `postgresql+psycopg2://...`

### 3. Testar conexão

Ao abrir a página **Análise de LME**, se a conexão estiver OK, você verá:
- ✅ Sem mensagens de erro
- ✅ Aba "🗄️ Usar Banco de Dados" funcionando

Se houver erro:
- ❌ Mensagem: "⚠️ Conexão com banco não configurada"
- Solução: Verifique o `secrets.toml` e a URL de conexão

## 📊 Estrutura do Banco

O sistema cria automaticamente 2 tabelas:

### `lme_snapshots`
Armazena informações sobre cada upload:
- `id` (UUID): Identificador único
- `ente`: Código do ente/IBGE (opcional)
- `uo`: Unidade Orçamentária (opcional)
- `lme_tipo`: 'LME 1' | 'LME 2' | 'LME 6' | 'misto'
- `rotulo`: 'ANTES' | 'DEPOIS' | 'BASE'
- `filename`: Nome do arquivo TXT
- `file_sha256`: Hash SHA256 do arquivo
- `created_at`: Data/hora de criação
- `note`: Observações

### `lme_regras`
Armazena as regras de cada snapshot:
- `id`: ID sequencial
- `snapshot_id`: Referência ao snapshot
- `lme`: Tipo de LME ('LME 1', 'LME 2', 'LME 6')
- `regra_completa`: Texto completo da regra
- `gd`, `fonte`, `uo`: Informações adicionais
- `regra_hash`: Hash SHA256 da regra (para comparação)

## 🚀 Como Usar

### 1. Salvar um snapshot ANTES

**Método Rápido:**
1. Na ABA 2, tab "📁 Comparar Arquivos"
2. Carregue os arquivos TXT em "Arquivo ANTES"
3. Clique em "💾 Salvar ANTES no Banco"
4. Copie o ID gerado

**Método Completo:**
1. Na ABA 2, tab "🗄️ Usar Banco de Dados"
2. Sub-tab "📤 Salvar Novo"
3. Preencha rótulo, ente, UO, observações
4. Faça upload dos TXTs
5. Clique em "💾 Salvar Snapshot"

### 2. Comparar snapshots

1. Na tab "🗄️ Usar Banco de Dados"
2. Sub-tab "🔍 Comparar Snapshots"
3. Veja a lista de snapshots recentes
4. Cole o ID do snapshot ANTES
5. Cole o ID do snapshot DEPOIS
6. Clique em "🧮 Comparar"
7. Download do Excel com diferenças

### 3. Gerenciar snapshots

1. Sub-tab "📋 Listar/Gerenciar"
2. Filtre por tipo, rótulo, limite
3. Veja todos os snapshots salvos
4. Delete snapshots antigos (cuidado!)

## 🔒 Segurança

### Boas Práticas:
- ✅ **NUNCA** commite o arquivo `secrets.toml` no Git
- ✅ Adicione `.streamlit/secrets.toml` no `.gitignore`
- ✅ Use senhas fortes no banco
- ✅ Habilite SSL/TLS na conexão (`?sslmode=require`)
- ✅ Limite acesso por IP no provider (se disponível)

### O que NÃO fazer:
- ❌ Colocar senha no código
- ❌ Compartilhar URL de conexão publicamente
- ❌ Usar banco de produção para testes

## 📈 Limites dos Planos Gratuitos

| Provider | Armazenamento | Conexões | Observações |
|----------|--------------|----------|-------------|
| **Neon** | 500 MB | 100 | Serverless, sem downtime |
| **Supabase** | 500 MB | 60-100 | Interface completa, backups |
| **Railway** | $5/mês crédito | Ilimitadas | Pago após crédito |
| **ElephantSQL** | 20 MB | 5 | Muito limitado |

### Estimativas de uso:
- 1 snapshot (LME misto) ≈ **50-200 KB**
- 100 snapshots ≈ **5-20 MB**
- 1000 snapshots ≈ **50-200 MB**

**Conclusão**: 500 MB suporta facilmente **centenas a milhares** de snapshots!

## 🐛 Troubleshooting

### Erro: "connection refused"
- Verifique se a URL está correta
- Teste conexão usando `psql` ou DBeaver
- Confirme que o banco aceita conexões externas

### Erro: "authentication failed"
- Senha incorreta
- Usuário não existe
- Banco de dados não existe

### Erro: "table does not exist"
- Tabelas ainda não foram criadas
- Execute `ensure_schema()` manualmente
- Verifique permissões do usuário

### Performance lenta
- Índices são criados automaticamente
- Se muito lento: considere upgrade do plano
- Limite número de snapshots antigos (delete)

## 📞 Suporte

Para problemas:
1. Verifique logs do Streamlit
2. Teste conexão usando client PostgreSQL
3. Consulte documentação do provider
4. Entre em contato com a equipe SUGESC/SUBCONT
