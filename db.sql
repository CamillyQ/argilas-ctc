CREATE TABLE leituras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amostra_id INTEGER NOT NULL,
    concentracao_sds REAL NOT NULL,
    condutividade REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(amostra_id)
        REFERENCES amostras(id)
);
CREATE TABLE amostras (
    id INTEGER PRIMARY KEY,
    codigo TEXT,
    origem TEXT,
    classe_argila TEXT,
    tipo_registro TEXT
);
CREATE TABLE propriedades (
    id INTEGER PRIMARY KEY,
    amostra_id INTEGER,
    cmc REAL,
    ctc REAL,
    FOREIGN KEY(amostra_id)
        REFERENCES amostras(id)
);
CREATE TABLE resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amostra_id INTEGER NOT NULL,
    cmc REAL,
    ctc REAL,
    metodo_calculo TEXT,
    data_processamento DATETIME,
    FOREIGN KEY(amostra_id)
        REFERENCES amostras(id)
);