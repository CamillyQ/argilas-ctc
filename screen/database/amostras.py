from db import conectar

#arquivo de manipulação do banco
def inserir_amostra(
    codigo,
    origem="",
    observacoes=""
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO amostras
        (
            codigo,
            origem,
            observacoes
        )
        VALUES (?, ?, ?)
    """, (
        codigo,
        origem,
        observacoes
    ))

    conn.commit()

    amostra_id = cursor.lastrowid

    conn.close()

    return amostra_id