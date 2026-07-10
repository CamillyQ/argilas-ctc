import numpy as np


CT_G_L = 0.01       # concentração da solução titulante (g/L)
MM_G_MOL = 319.85  
VA_L = 0.300          # volume da amostra/solução no béquer (L)


def calcular_concentracao_molar(volume_acumulado_mL, ct_g_l=CT_G_L, mm_g_mol=MM_G_MOL, va_l=VA_L):
    """
    Calcula a concentração molar do tensoativo já adicionado à solução.

    Estou seguindo as equações 4, 5 e 6 da dissertação:
    """
    if volume_acumulado_mL <= 0:
        return 0.0
    massa_tensoativo_g = ct_g_l * volume_acumulado_mL / 1000.0
    mols = massa_tensoativo_g / mm_g_mol
    return mols / va_l


import numpy as np

def calcular_r2(x, y):
    """Função auxiliar para calcular o R² de uma regressão linear."""
    if len(x) < 2: return 0.0
    coef = np.polyfit(x, y, 1)
    y_pred = np.polyval(coef, x)
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return (1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def detectar_cmc_joao(
    pontos_titulacao,
    minimo_pontos_reta=4,
    janela_derivada=3
):
    """
    Detecta a CMC identificando o 'joelho' da curva (mudança abrupta 
    na inclinação/derivada) e calculando a intersecção exata entre a 
    Reta Inicial (Pré-micelização) e a Reta Final (Pós-micelização).
    """

    ##############################################################
    # 1. Preparação dos Dados
    ##############################################################
    pontos_validos = [p for p in pontos_titulacao if p["concentracao_molar"] > 0]
    
    if len(pontos_validos) < minimo_pontos_reta * 2 + 1:
        raise ValueError("Pontos insuficientes para calcular duas retas distintas.")

    concentracoes = np.array([p["concentracao_molar"] for p in pontos_validos])
    volumes = np.array([p["volume_acumulado_mL"] for p in pontos_validos])
    condutividades = np.array([p["condutividade"] for p in pontos_validos])
    
    # Condutividade Molar (Ω)
    omegas = condutividades / concentracoes
    n = len(omegas)

    ##############################################################
    # 2. Encontrar o Ponto de Virada (O "Joelho") via Derivada
    # Usamos uma diferença finita local para achar onde a 
    # inclinação da curva sofre a maior alteração.
    ##############################################################
    
    derivadas = np.zeros(n - 1)
    for i in range(n - 1):
        derivadas[i] = (omegas[i+1] - omegas[i]) / (concentracoes[i+1] - concentracoes[i])
    
    # A mudança de inclinação (segunda derivada aproximada)
    mudanca_inclinacao = np.zeros(n - 2)
    for i in range(n - 2):
        mudanca_inclinacao[i] = abs(derivadas[i+1] - derivadas[i])
    
    # O índice do "joelho" é onde ocorre a maior quebra de inclinação
    # O +1 ajusta o índice para o array original de 'omegas'
    indice_joelho = np.argmax(mudanca_inclinacao) + 1 

    # Validação de segurança para o joelho não ficar nas pontas
    if indice_joelho < minimo_pontos_reta:
        indice_joelho = minimo_pontos_reta
    elif indice_joelho > n - minimo_pontos_reta:
        indice_joelho = n - minimo_pontos_reta

    ##############################################################
    # 3. Definir as Zonas de Pré e Pós Micelização 
    # Ignoramos intencionalmente o ponto exato do joelho (transição)
    # para garantir que as retas se ajustem apenas aos trechos lineares.
    ##############################################################
    
    # Pontos ANTES da transição (Reta Inicial)
    # Pega do início até um pouco antes do joelho
    idx_fim_pre = max(minimo_pontos_reta, indice_joelho)
    x_pre = concentracoes[:idx_fim_pre]
    y_pre = omegas[:idx_fim_pre]
    
    # Pontos DEPOIS da transição (Reta Final)
    # Pega de um pouco depois do joelho até o fim
    idx_inicio_pos = min(indice_joelho + 1, n - minimo_pontos_reta)
    x_pos = concentracoes[idx_inicio_pos:]
    y_pos = omegas[idx_inicio_pos:]

    ##############################################################
    # 4. Regressões Lineares e Intersecção
    ##############################################################
    
    a1, b1 = np.polyfit(x_pre, y_pre, 1)
    r2_pre = calcular_r2(x_pre, y_pre)
    
    a2, b2 = np.polyfit(x_pos, y_pos, 1)
    r2_pos = calcular_r2(x_pos, y_pos)

    # Resolve o sistema: a1*x + b1 = a2*x + b2 -> x = (b2 - b1) / (a1 - a2)
    # Proteção contra retas paralelas (muito raro em titulação)
    if abs(a1 - a2) < 1e-12:
        x_cmc = concentracoes[indice_joelho]
        y_cmc = omegas[indice_joelho]
    else:
        x_cmc = (b2 - b1) / (a1 - a2)
        y_cmc = a1 * x_cmc + b1

    ##############################################################
    # 5. Formatação do Resultado
    ##############################################################
    
    resultado = {
        "cmc": float(x_cmc),
        "omega_cmc": float(y_cmc),
        "indice_joelho": int(indice_joelho),
        
        # Qualidade do Ajuste
        "r2_pre": float(r2_pre),
        "r2_pos": float(r2_pos),
        
        # Dados das Retas (Para o Gráfico do Relatório)
        "reta_pre": (float(a1), float(b1)),
        "reta_pos": (float(a2), float(b2)),
        
        # Dados Brutos
        "concentracoes": concentracoes,
        "volumes_mL": volumes,
        "omegas": omegas
    }
    
    return resultado

def calcular_interseccao_cmc(concentracoes, omegas, indice_joelho):
    """
    Calcula o ponto de intersecção entre a reta de pré-micelização
    e a reta de pós-micelização.
    """
    if indice_joelho < 2 or indice_joelho >= len(concentracoes) - 2:
        raise ValueError("Ponto de corte muito próximo às extremidades.")

    # 1. Regressão da Reta Inicial (Pré-micelização)
    # Pontos antes do corte
    x_pre = concentracoes[:indice_joelho]
    y_pre = omegas[:indice_joelho]
    a1, b1 = np.polyfit(x_pre, y_pre, 1)

    # 2. Regressão da Reta Final (Pós-micelização - usando a que você já detectou)
    x_pos = concentracoes[indice_joelho:]
    y_pos = omegas[indice_joelho:]
    a2, b2 = np.polyfit(x_pos, y_pos, 1)

    # 3. Resolução do sistema: a1*x + b1 = a2*x + b2
    # x = (b2 - b1) / (a1 - a2)
    x_cmc = (b2 - b1) / (a1 - a2)
    y_cmc = a1 * x_cmc + b1

    return {
        "x_cmc": float(x_cmc),
        "y_cmc": float(y_cmc),
        "reta_pre": (float(a1), float(b1)),
        "reta_pos": (float(a2), float(b2))
    }

"""def detectar_cmc_joao(pontos_titulacao, limiar_percentual=10.0):
    
    Detecta o CMC pelo método de Silva Neto (2023): condutividade molar
    (Ω = condutividade / concentração) versus concentração molar, identificando
    onde começa o trecho linear (achatado) da curva através da diferença
    percentual entre pontos consecutivos de Ω.

    pontos_titulacao: lista de dicts, um por adição de titulante, em ordem
                       crescente de concentração, cada um com as chaves:
                       'volume_acumulado_mL', 'concentracao_molar' (mol/L)
                       e 'condutividade' (µS/cm)

    Retorna um dicionário com concentrações, volumes, Ω, o índice de corte,
    o CMC (mol/L), o volume (mL) no ponto de corte, a reta ajustada e as
    diferenças percentuais usadas no critério.

    Lança ValueError se faltarem pontos ou não for possível achar um trecho
    linear estável com o limiar dado.
    
    pontos_validos = [p for p in pontos_titulacao if p["concentracao_molar"] > 0]

    if len(pontos_validos) < 5:
        raise ValueError(
            "Pontos de titulação insuficientes para detectar o CMC "
            "(mínimo recomendado: 5 adições registradas)."
        )

    concentracoes = np.array([p["concentracao_molar"] for p in pontos_validos])
    volumes_mL = np.array([p["volume_acumulado_mL"] for p in pontos_validos])
    condutividades = np.array([p["condutividade"] for p in pontos_validos])
    omegas = condutividades / concentracoes

    diferencas_percentuais = np.zeros(len(omegas))
    for i in range(1, len(omegas)):
        diferencas_percentuais[i] = abs(omegas[i - 1] - omegas[i]) / omegas[i - 1] * 100.0

    indice_joelho = None
    for j in range(1, len(omegas) - 2):
        if np.all(diferencas_percentuais[j:] < limiar_percentual):
            indice_joelho = j
            break

    if indice_joelho is None:
        raise ValueError(
            "Não foi possível identificar um trecho linear estável com o limiar de "
            f"{limiar_percentual:.0f}%. Colete mais pontos ou ajuste o limiar."
        )

    a, b = np.polyfit(concentracoes[indice_joelho:], omegas[indice_joelho:], 1)

    return {
        "concentracoes": concentracoes,
        "volumes_mL": volumes_mL,
        "omegas": omegas,
        "indice_joelho": indice_joelho,
        "cmc": float(concentracoes[indice_joelho]),
        "volume_no_corte_mL": float(volumes_mL[indice_joelho]),
        "reta": (float(a), float(b)),
        "diferencas_percentuais": diferencas_percentuais,
    }
"""
def concentracao_para_volume(concentracao_molar, ct_g_l=CT_G_L, mm_g_mol=MM_G_MOL, va_l=VA_L):
    """
    Faz o caminho inverso das equações IV, V e VI da dissertação.
    Recebe a concentração molar exata da intersecção (x_cmc) e retorna 
    o volume exato correspondente (mL) de titulante adicionado.
    """
    if concentracao_molar <= 0:
        return 0.0
        
    volume_mL = (concentracao_molar * 1000.0 * mm_g_mol * va_l) / ct_g_l
    return volume_mL

def cmc_para_ctc(volume_no_corte_mL, massa_amostra_g, normalidade_titulante=0.01):
    """
    Calcula a CTC (mEq/100g) usando a normalidade fixa de 0.01 N
    para garantir a consistência com os resultados da dissertação.
    """
    if massa_amostra_g <= 0:
        raise ValueError("A massa da amostra deve ser maior que zero.")

    # CTC = (V_titulante * N_titulante * 100) / massa_amostra
    return (volume_no_corte_mL * normalidade_titulante * 100) / massa_amostra_g

def calcular_ctc_final(interseccao_cmc, massa_amostra):
    volume_exato = concentracao_para_volume(interseccao_cmc['x_cmc'])
  
    resultado = cmc_para_ctc(
        volume_no_corte_mL=volume_exato, 
        massa_amostra_g=massa_amostra, 
        normalidade_titulante=0.01
    )
    
    return resultado

def classificar_tipo_argila(ctc_meq_100g):
    """
    Classifica o tipo de argila com base em faixas de CTC da literatura
    (Menezes et al., 2008, citado na dissertação, p.26).

    PLACEHOLDER -- substitua por seu classificador treinado assim que tiver
    amostras de referência suficientes.
    """
    if ctc_meq_100g < 15:
        return "Caulinita (estimado)"
    elif ctc_meq_100g < 40:
        return "Ilita (estimado)"
    else:
        return "Esmectita/Bentonita (estimado)"