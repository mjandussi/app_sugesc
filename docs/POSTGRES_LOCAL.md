# 🐘 Configurar PostgreSQL Local

Guia rápido para configurar e usar PostgreSQL local para desenvolvimento.

## ✅ Pré-requisitos

Você já deve ter PostgreSQL instalado localmente. Se não tiver:

**Windows:**
- Download: https://www.postgresql.org/download/windows/
- Ou via Chocolatey: `choco install postgresql`

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
sudo yum install postgresql postgresql-server       # CentOS/RHEL
```

**Mac:**
```bash
brew install postgresql
```

## 🚀 Setup Rápido

### 1. Verificar se PostgreSQL está rodando

**Windows (PowerShell):**
```powershell
Get-Service postgresql*
```

Se não estiver rodando:
```powershell
Start-Service postgresql-x64-XX  # Substituir XX pela versão
```

**Linux/Mac:**
```bash
sudo systemctl status postgresql
```

Se não estiver rodando:
```bash
sudo systemctl start postgresql
```

### 2. Criar banco de dados para LME

**Conectar ao PostgreSQL:**
```bash
# Windows/Linux/Mac
psql -U postgres
```

**Criar o banco:**
```sql
CREATE DATABASE lme_db;
```

**Verificar:**
```sql
\l  -- Lista todos os bancos
\q  -- Sair
```

### 3. Configurar secrets.toml

Crie o arquivo `.streamlit/secrets.toml`:

```toml
# Para PostgreSQL Local
db_url = "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/lme_db"
```

**Importante:**
- Substitua `SUA_SENHA` pela senha do seu usuário `postgres`
- A porta padrão é `5432`
- No Linux/Mac você pode omitir `:5432` se for a porta padrão

### 4. Testar conexão

Abra o app Streamlit:
```bash
streamlit run Home.py
```

Vá em **Análise de LME** → **ABA 2**

Se conectou com sucesso:
- ✅ Sem mensagens de erro
- ✅ Tab "🗄️ Usar Banco de Dados" funciona

Se houver erro:
- ❌ Verifique senha
- ❌ Verifique se PostgreSQL está rodando
- ❌ Verifique se o banco `lme_db` foi criado

## 🗄️ Estrutura Criada Automaticamente

Ao abrir a página pela primeira vez, serão criadas automaticamente:

### Tabela `lme_snapshots`:
- `id` (UUID): Identificador único
- `uo`: Unidade Orçamentária padrão
- `lme_tipo`: Tipo ('LME 1' | 'LME 2' | 'LME 6' | 'misto')
- `rotulo`: Rótulo ('ANTES' | 'DEPOIS' | 'BASE')
- `filename`: Nome do arquivo TXT
- `file_sha256`: Hash SHA256 do arquivo
- `created_at`: Data/hora de criação
- `note`: Observações

### Tabela `lme_regras`:
- `id`: ID sequencial
- `snapshot_id`: Referência ao snapshot
- `lme`: Tipo de LME
- `regra_completa`: Texto completo da regra
- **`gd`**: Grupo de Despesa (ex: '1')
- **`uo`**: Unidade Orçamentária (ex: '40440')
- **`acao`**: Ação PPA (ex: '2019')
- `regra_hash`: Hash SHA256 da regra

## 🔍 Consultas Úteis (psql)

### Ver todos os snapshots:
```sql
SELECT id, rotulo, lme_tipo, filename, created_at
FROM lme_snapshots
ORDER BY created_at DESC;
```

### Ver regras de um snapshot:
```sql
SELECT lme, gd, uo, acao, regra_completa
FROM lme_regras
WHERE snapshot_id = 'COLE_UUID_AQUI'
LIMIT 10;
```

### Contar regras por snapshot:
```sql
SELECT
    s.id,
    s.rotulo,
    s.lme_tipo,
    COUNT(r.id) as qtd_regras
FROM lme_snapshots s
LEFT JOIN lme_regras r ON r.snapshot_id = s.id
GROUP BY s.id, s.rotulo, s.lme_tipo
ORDER BY s.created_at DESC;
```

### Deletar snapshot e suas regras:
```sql
DELETE FROM lme_snapshots WHERE id = 'COLE_UUID_AQUI';
-- As regras são deletadas automaticamente (CASCADE)
```

### Ver tamanho do banco:
```sql
SELECT pg_size_pretty(pg_database_size('lme_db'));
```

## 🔄 Migrar para Cloud (Neon/Supabase)

Quando quiser migrar do local para cloud:

### 1. Exportar dados:
```bash
pg_dump -U postgres -d lme_db -F c -f lme_backup.dump
```

### 2. Criar banco no Neon/Supabase

### 3. Importar dados:
```bash
pg_restore -U usuario -d nome_banco -h host lme_backup.dump
```

### 4. Atualizar secrets.toml:
```toml
# Mudar de:
db_url = "postgresql+psycopg2://postgres:senha@localhost:5432/lme_db"

# Para (Neon):
db_url = "postgresql+psycopg2://usuario:senha@ep-name.aws.neon.tech/neondb?sslmode=require"
```

## 🐛 Troubleshooting

### Erro: "connection refused"
→ PostgreSQL não está rodando. Inicie o serviço.

### Erro: "authentication failed"
→ Senha incorreta. Verifique a senha do usuário `postgres`.

### Erro: "database does not exist"
→ Crie o banco: `CREATE DATABASE lme_db;`

### Erro: "permission denied"
→ Usuário não tem permissão. Use o superuser `postgres` ou ajuste permissões.

### PostgreSQL lento
→ Configure `shared_buffers` e `work_mem` no `postgresql.conf`

## 💡 Dicas

✅ **Backup automático**:
```bash
# Cron job (Linux) para backup diário
0 2 * * * pg_dump -U postgres lme_db > /backups/lme_$(date +\%Y\%m\%d).sql
```

✅ **Interface gráfica**:
- pgAdmin: https://www.pgadmin.org/
- DBeaver: https://dbeaver.io/

✅ **Logs do PostgreSQL**:
- Windows: `C:\Program Files\PostgreSQL\XX\data\log\`
- Linux: `/var/log/postgresql/`

---

**Próximos passos:**
1. Teste salvando um snapshot ANTES
2. Simule nova regra e salve como DEPOIS
3. Compare os dois snapshots
4. Quando estiver satisfeito, migre para Neon/Supabase para produção!
