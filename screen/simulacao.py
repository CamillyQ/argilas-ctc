from services.analises import (detectar_cmc_joao, calcular_interseccao_cmc)

dados = [
    {
        "volume_acumulado_mL": 0.5,
        "concentracao_molar": 2.14e-5,
        "condutividade": 320
    },
    {
        "volume_acumulado_mL": 1.0,
        "concentracao_molar": 4.28e-5,
        "condutividade": 510
    },
    {
        "volume_acumulado_mL": 1.5,
        "concentracao_molar": 6.42e-5,
        "condutividade": 690
    },
    {
        "volume_acumulado_mL": 2.0,
        "concentracao_molar": 8.56e-5,
        "condutividade": 860
    },

    # -------- início da região linear --------

    {
        "volume_acumulado_mL": 2.5,
        "concentracao_molar": 1.07e-4,
        "condutividade": 1068
    },
    {
        "volume_acumulado_mL": 3.0,
        "concentracao_molar": 1.28e-4,
        "condutividade": 1276
    },
    {
        "volume_acumulado_mL": 3.5,
        "concentracao_molar": 1.49e-4,
        "condutividade": 1484
    },
    {
        "volume_acumulado_mL": 4.0,
        "concentracao_molar": 1.71e-4,
        "condutividade": 1692
    },
    {
        "volume_acumulado_mL": 4.5,
        "concentracao_molar": 1.92e-4,
        "condutividade": 1900
    },
    {
        "volume_acumulado_mL": 5.0,
        "concentracao_molar": 2.14e-4,
        "condutividade": 2108
    }
]

resultado = detectar_cmc_joao(dados)
print(f"CMC pela detectar_cmc_joao: {resultado['cmc']}")

interseccao = calcular_interseccao_cmc(resultado['concentracoes'], resultado['omegas'], resultado['indice_joelho'])
print(f"CMC exata pela intersecção: {interseccao['x_cmc']} mol/L")

