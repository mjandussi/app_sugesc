# 🗄️ Versionamento de Regras LME com PostgreSQL

## 📋 Resumo

O sistema agora permite salvar e versionar as regras de LME (Limite de Movimentação e Empenho) em um banco de dados PostgreSQL. Isso traz:

✅ **Histórico completo** de alterações nas regras
✅ **Comparações rápidas** entre versões (ANTES vs DEPOIS)
✅ **Auditoria** e rastreabilidade
✅ **Reprodutibilidade** de análises passadas
✅ **Backup automático** dos dados

## 🚀 Início Rápido

### 1. Criar banco PostgreSQL gratuito

Recomendamos **Neon** (https://neon.tech):
- Plano Free: 500 MB (suficiente para milhares de snapshots)
- Setup em 2 minutos
- Serverless e rápido

### 2. Configurar credenciais

Crie `.streamlit/secrets.toml`:

```toml
db_url = "postgresql+psycopg2://usuario:senha@host:porta/banco"
```

**Exemplo real:**
```toml
db_url = "postgresql+psycopg2://neondb_owner:abc123@ep-name.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

⚠️ **IMPORTANTE**: Este arquivo já está no `.gitignore` e **nunca** deve ser commitado!

### 3. Usar o sistema

Acesse **Análise de LME** → **ABA 2: TXT Antes x Depois**

Você verá 2 tabs:
- **📁 Comparar Arquivos**: Modo tradicional + botão para salvar no banco
- **🗄️ Usar Banco de Dados**: Gerenciar snapshots e comparar via banco

## 💡 Como Funciona

### Fluxo Típico:

1. **Salvar snapshot ANTES:**
   - Carregue os TXTs na tab "📁 Comparar Arquivos"
   - Clique em "💾 Salvar ANTES no Banco"
   - Copie o ID gerado (UUID)

2. **Quando chegar nova regra (DEPOIS):**
   - Vá em "🗄️ Usar Banco de Dados"
   - Sub-tab "📤 Salvar Novo"
   - Marque como "DEPOIS", faça upload
   - Clique em "💾 Salvar Snapshot"

3. **Comparar:**
   - Sub-tab "🔍 Comparar Snapshots"
   - Cole ID do ANTES e ID do DEPOIS
   - Clique em "🧮 Comparar"
   - Download do Excel com diferenças

### Recursos Adicionais:

- **Listar snapshots**: Veja todos os salvos, filtre por tipo/rótulo
- **Deletar snapshots**: Remova versões antigas (cuidado!)
- **Metadados**: Salve informações como ente, UO, observações
- **Hash SHA256**: Detecta arquivos duplicados automaticamente

## 📊 Estrutura de Dados

### Snapshots
Cada upload gera um snapshot com:
- ID único (UUID)
- Rótulo (ANTES/DEPOIS/BASE)
- Tipo (LME 1/2/6/misto)
- Nome do arquivo
- Data/hora
- Observações

### Regras
Cada regra tem:
- Texto completo
- Hash SHA256 (para comparação)
- Campos: GD, FONTE, UO
- Referência ao snapshot

## 🔒 Segurança

✅ Arquivo `secrets.toml` protegido no `.gitignore`
✅ Conexão SSL/TLS obrigatória
✅ Senhas nunca no código
✅ Banco isolado por projeto

❌ **NUNCA** commite credenciais no Git!

## 📚 Documentação Completa

Veja [docs/CONFIGURACAO_BD.md](docs/CONFIGURACAO_BD.md) para:
- Setup detalhado de cada provider
- Troubleshooting
- Boas práticas
- Limites dos planos gratuitos
- Estrutura completa do banco

## 🆘 Problemas Comuns

### "⚠️ Conexão com banco não configurada"
→ Crie o arquivo `.streamlit/secrets.toml` com a URL de conexão

### "connection refused"
→ Verifique se a URL está correta (host, porta, usuário, senha)

### "authentication failed"
→ Senha incorreta ou usuário inexistente

### Performance lenta
→ Considere upgrade do plano ou delete snapshots antigos

## 🎯 Vantagens do Banco vs Arquivos

| Aspecto | Arquivos TXT | Banco PostgreSQL |
|---------|--------------|------------------|
| Histórico | ❌ Manual | ✅ Automático |
| Comparação | 🔶 2 arquivos por vez | ✅ Qualquer par |
| Auditoria | ❌ Difícil | ✅ Completa |
| Busca | ❌ Manual | ✅ SQL rápido |
| Backup | 🔶 Manual | ✅ Provedor gerencia |
| Reprodução | ❌ Depende de arquivos | ✅ Snapshot versionado |

## 🚀 Próximos Passos

1. Configure seu banco PostgreSQL
2. Salve seu primeiro snapshot ANTES
3. Quando chegar nova regra, salve como DEPOIS
4. Compare e baixe o Excel com diferenças!

---

**Desenvolvido por**: SUGESC/SUBCONT
**Suporte**: Entre em contato com a equipe técnica
