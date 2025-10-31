# 💾 Guia do Sistema de Banco de Dados LME

## Visão Geral

O novo sistema de banco de dados utiliza **SCD-Type 2** (Slowly Changing Dimension Type 2) para manter um histórico completo e automático de todas as alterações nas regras de LME.

### Principais características:

✅ **Uma única tabela** (`lme_regras_hist`) ao invés de snapshots
✅ **Histórico automático** de todas as mudanças
✅ **Rastreabilidade completa** com datas de vigência
✅ **Sincronização inteligente** que identifica regras novas, removidas e alteradas
✅ **Consultas rápidas** de regras vigentes ou histórico completo

---

## Como Funciona

### Estrutura da Tabela

A tabela `lme_regras_hist` possui os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | BIGSERIAL | Chave primária auto-incremento |
| `lme` | TEXT | Tipo de LME ('LME 1', 'LME 2', 'LME 6') |
| `gd` | TEXT | Grupo de Despesa |
| `uo` | TEXT | Unidade Orçamentária |
| `acao` | TEXT | Ação PPA (sufixo do código) |
| `regra_completa` | TEXT | Texto completo da regra |
| `regra_hash` | CHAR(64) | Hash SHA256 da regra (para detectar alterações) |
| `vigente_desde` | TIMESTAMPTZ | Data/hora em que a regra entrou em vigor |
| `vigente_ate` | TIMESTAMPTZ | Data/hora em que a regra saiu de vigor (NULL = ainda vigente) |

### Chave Natural

A combinação **(lme, gd, uo, acao)** identifica unicamente uma regra. Um índice único parcial garante que só pode existir **uma linha aberta** (com `vigente_ate = NULL`) por chave natural.

---

## Processo de Sincronização

Quando você carrega um arquivo TXT de regras, o sistema:

1. **Analisa o arquivo** e extrai todas as combinações (GD, UO, AÇÃO)
2. **Compara com o banco** (regras atualmente vigentes para aquele LME)
3. **Identifica movimentos:**
   - 🟢 **Novas**: combinações que estão no arquivo mas não no banco
   - 🔴 **Removidas**: combinações que estão no banco mas não no arquivo
   - 🟡 **Alteradas**: combinações que existem em ambos mas com `regra_completa` diferente
   - ⚪ **Mantidas**: combinações idênticas

4. **Executa operações:**
   - **Removidas** → fecha a vigência (`vigente_ate = NOW()`)
   - **Novas** → insere nova linha com `vigente_desde = NOW()`, `vigente_ate = NULL`
   - **Alteradas** → fecha a linha antiga e cria uma nova
   - **Mantidas** → não faz nada

---

## Exemplo Prático

### Situação Inicial

Banco vazio. Você carrega `LME_1.txt` com 270 regras:

```
Resultado:
- 🟢 Novas: 270
- 🔴 Removidas: 0
- 🟡 Alteradas: 0
- ⚪ Mantidas: 0

Banco agora tem 270 regras vigentes para LME 1
```

### Primeira Atualização

Você modifica `LME_1.txt`:
- Remove 2 combinações (GD=1, UO=25010, ACAO=4921) e (GD=1, UO=49650, ACAO=4540)
- Adiciona 11 novas combinações na UO=27410 e UO=27530

Carrega o novo arquivo:

```
Resultado:
- 🟢 Novas: 11
- 🔴 Removidas: 2
- 🟡 Alteradas: 0
- ⚪ Mantidas: 268

Banco agora tem 279 regras vigentes para LME 1 (270 - 2 + 11)
Histórico total: 281 registros (11 novas + 268 mantidas + 2 encerradas)
```

### Alteração de Regra

Você modifica uma regra existente (mesmo GD+UO+ACAO, mas muda o texto da `regra_completa`):

```
Resultado:
- 🟢 Novas: 0
- 🔴 Removidas: 0
- 🟡 Alteradas: 1
- ⚪ Mantidas: 278

Banco ainda tem 279 regras vigentes para LME 1
Histórico total: 282 registros (a regra antiga foi fechada, nova foi aberta)
```

---

## Como Usar

### 1. Configurar Banco de Dados

Certifique-se de que o arquivo `.streamlit/secrets.toml` está configurado:

```toml
# PostgreSQL Local
db_url = "postgresql+psycopg2://postgres:sua_senha@localhost:5432/lme_db"

# Ou PostgreSQL Cloud (Neon/Supabase)
# db_url = "postgresql+psycopg2://usuario:senha@host.cloud.com/lme_db?sslmode=require"
```

### 2. Acessar a Página de Banco de Dados

No Streamlit, acesse: **Outras Análises → Banco de Dados LME**

### 3. Sincronizar Regras

1. Vá para a aba **"📤 Sincronizar Regras"**
2. Faça upload do arquivo TXT (LME 1, LME 2 ou LME 6)
3. Clique em **"Sincronizar"**
4. Veja o resumo das mudanças

### 4. Consultar Regras Vigentes

1. Vá para a aba **"📊 Regras Vigentes"**
2. Escolha o filtro (Todos, LME 1, LME 2 ou LME 6)
3. Clique em **"Consultar"**
4. Baixe para Excel se necessário

### 5. Visualizar Histórico

1. Vá para a aba **"📜 Histórico Completo"**
2. Filtre por LME e/ou UO
3. Veja todas as regras (vigentes e encerradas) com suas datas
4. Regras com `vigente_ate = NULL` estão vigentes
5. Regras com `vigente_ate <> NULL` foram encerradas

### 6. Ver Estatísticas

1. Vá para a aba **"📈 Estatísticas"**
2. Veja totais de regras vigentes e registros históricos
3. Visualize distribuição por LME

---

## Consultas SQL Úteis

### Listar regras vigentes de um LME específico

```sql
SELECT lme, gd, uo, acao, regra_completa, vigente_desde
FROM lme_regras_hist
WHERE lme = 'LME 1'
  AND vigente_ate IS NULL
ORDER BY gd, uo, acao;
```

### Ver histórico completo de uma UO específica

```sql
SELECT lme, gd, uo, acao, vigente_desde, vigente_ate,
       CASE WHEN vigente_ate IS NULL THEN 'VIGENTE' ELSE 'ENCERRADA' END as status
FROM lme_regras_hist
WHERE uo = '27410'
ORDER BY lme, gd, acao, vigente_desde DESC;
```

### Contar quantas vezes uma combinação mudou

```sql
SELECT lme, gd, uo, acao, COUNT(*) as num_versoes
FROM lme_regras_hist
GROUP BY lme, gd, uo, acao
HAVING COUNT(*) > 1
ORDER BY num_versoes DESC;
```

### Ver regras que foram encerradas em um período

```sql
SELECT lme, gd, uo, acao, vigente_desde, vigente_ate
FROM lme_regras_hist
WHERE vigente_ate BETWEEN '2025-01-01' AND '2025-12-31'
ORDER BY vigente_ate DESC;
```

---

## Vantagens vs Sistema Anterior (Snapshots)

| Aspecto | Sistema Anterior | Novo Sistema |
|---------|-----------------|--------------|
| **Tabelas** | 2 tabelas (snapshots + regras) | 1 tabela única |
| **Consulta vigente** | Buscar snapshot mais recente | `WHERE vigente_ate IS NULL` |
| **Histórico** | Comparar snapshots manualmente | Automático na mesma tabela |
| **Duplicação** | Alta (mesmas regras em múltiplos snapshots) | Baixa (só registra mudanças) |
| **Rastreabilidade** | Limitada a snapshots salvos | Completa e automática |
| **Manutenção** | Precisa deletar snapshots antigos | Automática |

---

## Limpeza de Dados

### Deletar todas as regras de um LME (dados de teste)

⚠️ **CUIDADO:** Esta operação é irreversível!

1. Vá para a aba **"🗑️ Gerenciar Dados"**
2. Selecione o LME
3. Digite `DELETAR LME X` para confirmar
4. Clique em **"Deletar"**

Ou via SQL:

```sql
DELETE FROM lme_regras_hist WHERE lme = 'LME 1';
```

---

## Troubleshooting

### Erro: "Sem engine de banco de dados"

**Causa:** Não foi possível conectar ao PostgreSQL
**Solução:** Verifique o arquivo `.streamlit/secrets.toml` e certifique-se de que:
- O PostgreSQL está rodando
- As credenciais estão corretas
- O banco de dados `lme_db` existe

### Erro: "DF sem colunas obrigatórias"

**Causa:** O arquivo TXT não foi parseado corretamente
**Solução:** Verifique se o arquivo TXT está no formato esperado:
- Blocos separados por ` OU `
- Condições dentro de cada bloco separadas por ` E `
- Formato: `[GRUPO DE DESPESA].[Código] = 'X' E ...`

### Regras não aparecem após sincronização

**Causa:** Possível erro durante o upsert
**Solução:**
1. Verifique os logs de erro no Streamlit
2. Execute consulta SQL direta:
   ```sql
   SELECT COUNT(*) FROM lme_regras_hist WHERE lme = 'LME X';
   ```

---

## Próximos Passos

1. **Migração para Cloud**: Quando estiver satisfeito com os testes locais, migre para Neon ou Supabase
2. **Backups**: Configure backups automáticos do PostgreSQL
3. **Auditoria**: Use as consultas de histórico para auditar mudanças

---

## Suporte

Em caso de dúvidas ou problemas, consulte:
- Documentação PostgreSQL: https://www.postgresql.org/docs/
- Logs do Streamlit
- Código fonte em `core/db_simple.py`
