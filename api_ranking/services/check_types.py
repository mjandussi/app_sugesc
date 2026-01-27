#############################################################################
# FUNÇÃO: VERIFICAR TIPO DE RELATÓRIO (Simplificado ou Completo)
#############################################################################

def detectar_tipo_relatorio(df_extrato):
    """
    Detecta se o município usa relatório Simplificado ou Completo
    com base no Extrato de Entregas.

    Regra: Se qualquer entregável contém "Simplificado", usa Simplificado.
    Caso contrário, usa Completo.

    Estados sempre usam Completo (esta função só é chamada para Municípios).
    """
    if df_extrato is None or df_extrato.empty:
        return None  # Não foi possível detectar

    if 'entregavel' not in df_extrato.columns:
        return None

    entregaveis = df_extrato['entregavel'].dropna().unique()
    for entregavel in entregaveis:
        if 'Simplificado' in str(entregavel):
            return 'Simplificado'
    return 'Completo'


#############################################################################
# FUNÇÃO: VERIFICAR A DISPONIBILIDADE DE CADA DEMONSTRATIVO
#############################################################################

def verificar_disponibilidade_demonstrativos(df_extrato, tipo_ente, tipo_relatorio):
    """
    Analisa o extrato e retorna um dicionário com a disponibilidade de cada demonstrativo.

    Args:
        df_extrato: DataFrame com os extratos de entregas
        tipo_ente: "E" (Estado) ou "M" (Município)
        tipo_relatorio: "Completo" ou "Simplificado"

    Returns:
        dict com chaves: 'msc', 'msc_encerramento', 'dca', 'rreo', 'rgf'
        Cada valor é um dict com:
        - 'disponivel': bool (tem pelo menos 1 período)
        - 'completo': bool (tem todos os períodos esperados)
        - 'periodos': list de períodos encontrados
        - 'mensagem': str descritiva para exibição
    """
    resultado = {
        'msc': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviada'},
        'msc_encerramento': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviada'},
        'dca': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviada'},
        'rreo': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviado'},
        'rgf': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviado'},
        'rgf_exec': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviado'},
        'rgf_leg': {'disponivel': False, 'completo': False, 'periodos': [], 'mensagem': 'Não enviado'},
    }

    if df_extrato is None or df_extrato.empty:
        return resultado

    if 'entregavel' not in df_extrato.columns or 'periodo' not in df_extrato.columns:
        return resultado

    msc_df = df_extrato[df_extrato['entregavel'].str.contains('MSC Agregada', case=False, na=False)]
    if not msc_df.empty:
        periodos_msc = sorted(msc_df['periodo'].dropna().unique().tolist())
        resultado['msc']['periodos'] = periodos_msc
        resultado['msc']['disponivel'] = len(periodos_msc) > 0
        resultado['msc']['completo'] = set(range(1, 13)).issubset(set(periodos_msc))
        if resultado['msc']['completo']:
            resultado['msc']['mensagem'] = 'Completa (meses 1-12)'
        elif resultado['msc']['disponivel']:
            meses_str = ', '.join(map(str, periodos_msc))
            faltam = [m for m in range(1, 13) if m not in periodos_msc]
            faltam_str = ', '.join(map(str, faltam))
            resultado['msc']['mensagem'] = f'Parcial: meses {meses_str} (falta: {faltam_str})'

    msce_df = df_extrato[df_extrato['entregavel'].str.contains('MSC Encerramento', case=False, na=False)]
    if not msce_df.empty:
        resultado['msc_encerramento']['disponivel'] = True
        resultado['msc_encerramento']['completo'] = True
        resultado['msc_encerramento']['periodos'] = [1]
        resultado['msc_encerramento']['mensagem'] = 'Enviada'

    dca_df = df_extrato[df_extrato['entregavel'].str.contains('Balanço Anual|DCA', case=False, na=False)]
    if not dca_df.empty:
        resultado['dca']['disponivel'] = True
        resultado['dca']['completo'] = True
        resultado['dca']['periodos'] = [1]
        resultado['dca']['mensagem'] = 'Enviada'

    rreo_df = df_extrato[df_extrato['entregavel'].str.contains('RREO|Resumido de Execução Orçamentária', case=False, na=False)]
    if not rreo_df.empty:
        periodos_rreo = sorted(rreo_df['periodo'].dropna().unique().tolist())
        resultado['rreo']['periodos'] = periodos_rreo
        resultado['rreo']['disponivel'] = len(periodos_rreo) > 0
        resultado['rreo']['completo'] = 6 in periodos_rreo
        if resultado['rreo']['completo']:
            resultado['rreo']['mensagem'] = 'Completo (bimestres 1-6)'
        elif resultado['rreo']['disponivel']:
            bim_str = ', '.join(map(str, periodos_rreo))
            faltam = [b for b in range(1, 7) if b not in periodos_rreo]
            faltam_str = ', '.join(map(str, faltam))
            resultado['rreo']['mensagem'] = f'Parcial: bimestres {bim_str} (falta: {faltam_str})'

    rgf_df = df_extrato[df_extrato['entregavel'].str.contains('RGF|Gestão Fiscal', case=False, na=False)]
    if not rgf_df.empty:
        if 'periodicidade' in rgf_df.columns:
            periodicidade = rgf_df['periodicidade'].mode().iloc[0] if not rgf_df['periodicidade'].mode().empty else 'Q'
        else:
            periodicidade = 'S' if tipo_relatorio == 'Simplificado' else 'Q'

        periodos_rgf = sorted(rgf_df['periodo'].dropna().unique().tolist())
        resultado['rgf']['periodos'] = periodos_rgf
        resultado['rgf']['disponivel'] = len(periodos_rgf) > 0

        ultimo_periodo_esperado = 2 if periodicidade == 'S' else 3
        resultado['rgf']['completo'] = ultimo_periodo_esperado in periodos_rgf

        if resultado['rgf']['completo']:
            tipo_per = 'semestres' if periodicidade == 'S' else 'quadrimestres'
            resultado['rgf']['mensagem'] = f'Completo ({tipo_per} 1-{ultimo_periodo_esperado})'
        elif resultado['rgf']['disponivel']:
            tipo_per = 'semestres' if periodicidade == 'S' else 'quadrimestres'
            per_str = ', '.join(map(str, periodos_rgf))
            faltam = [p for p in range(1, ultimo_periodo_esperado + 1) if p not in periodos_rgf]
            faltam_str = ', '.join(map(str, faltam))
            resultado['rgf']['mensagem'] = f'Parcial: {tipo_per} {per_str} (falta: {faltam_str})'

        if 'instituicao' in rgf_df.columns:
            rgf_exec = rgf_df[rgf_df['instituicao'].str.contains('Executivo|Prefeitura|Governo', case=False, na=False)]
            if not rgf_exec.empty:
                periodos_exec = sorted(rgf_exec['periodo'].dropna().unique().tolist())
                resultado['rgf_exec']['periodos'] = periodos_exec
                resultado['rgf_exec']['disponivel'] = len(periodos_exec) > 0
                resultado['rgf_exec']['completo'] = ultimo_periodo_esperado in periodos_exec
                if resultado['rgf_exec']['completo']:
                    resultado['rgf_exec']['mensagem'] = 'Completo'
                elif resultado['rgf_exec']['disponivel']:
                    resultado['rgf_exec']['mensagem'] = f'Parcial: períodos {", ".join(map(str, periodos_exec))}'

            rgf_leg = rgf_df[rgf_df['instituicao'].str.contains('Legislativ|Câmara|Assembl', case=False, na=False)]
            if not rgf_leg.empty:
                periodos_leg = sorted(rgf_leg['periodo'].dropna().unique().tolist())
                resultado['rgf_leg']['periodos'] = periodos_leg
                resultado['rgf_leg']['disponivel'] = len(periodos_leg) > 0
                resultado['rgf_leg']['completo'] = ultimo_periodo_esperado in periodos_leg
                if resultado['rgf_leg']['completo']:
                    resultado['rgf_leg']['mensagem'] = 'Completo'
                elif resultado['rgf_leg']['disponivel']:
                    resultado['rgf_leg']['mensagem'] = f'Parcial: períodos {", ".join(map(str, periodos_leg))}'

    return resultado


#############################################################################
# FUNÇÃO: VERIFICAR SE UMA VERIFICAÇÃO PODE SER EXECUTADA
#############################################################################

# Tradução dos tipos de relatório do arquivo metodologia para chaves internas
TRADUCAO_RELATORIO = {
    'MSC': ['msc'],
    'DCA': ['dca'],
    'RREO': ['rreo'],
    'RGF': ['rgf'],
    'MSC x DCA': ['msc', 'dca'],
    'MSC x RREO': ['msc', 'rreo'],
    'DCA x RREO': ['dca', 'rreo'],
    'DCA x RGF': ['dca', 'rgf'],
    'RREO x RGF': ['rreo', 'rgf'],
    'RGF x RREO': ['rreo', 'rgf'],
    'MSC de Dezembro': ['msc_encerramento'],
    'MSC de dezembro x RREO': ['msc_encerramento', 'rreo'],
    'DCA x MSC de dezembro': ['dca', 'msc_encerramento'],
    'MSC \nRGF': ['msc', 'rgf'],
    'RGF\nMSC Dezembro': ['rgf', 'msc_encerramento'],
}

def verificacao_disponivel(codigo, disponibilidade, tipo_relatorio_verif=None):
    """
    Verifica se uma verificação específica pode ser executada.

    Regras:
    - D1: SEMPRE executa com dados parciais (exceto D1_00036 que precisa msc_encerramento)
    - D2/D3/D4: Verifica se TODOS os demonstrativos necessários estão disponíveis

    Args:
        codigo: código da verificação (ex: 'D1_00020')
        disponibilidade: dict retornado por verificar_disponibilidade_demonstrativos
        tipo_relatorio_verif: tipo de relatório da verificação (coluna 'Relatório' da metodologia)

    Returns:
        (bool, str): (pode_executar, mensagem_motivo)
    """
    dimensao = codigo[:2]  # 'D1', 'D2', etc.

    if dimensao == 'D1':
        # D1 sempre executa com dados parciais
        if codigo == 'D1_00036':
            # Exceção: precisa MSC Encerramento
            if not disponibilidade.get('msc_encerramento', {}).get('disponivel', False):
                return False, "Requer MSC de Encerramento"
        # Verificar se tem pelo menos MSC disponível para as outras verificações D1
        if not disponibilidade.get('msc', {}).get('disponivel', False):
            return False, "Requer MSC"
        return True, "OK"

    # D2, D3, D4: verificar requisitos baseado no tipo de relatório
    if tipo_relatorio_verif:
        requisitos = TRADUCAO_RELATORIO.get(tipo_relatorio_verif, [])
        for req in requisitos:
            if not disponibilidade.get(req, {}).get('disponivel', False):
                nome_req = req.upper().replace('_', ' ')
                return False, f"Requer {nome_req}"

    return True, "OK"