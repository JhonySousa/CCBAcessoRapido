#!/bin/bash
# Populate the database with sample casas de oração

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PATH="$SCRIPT_DIR/../database.db"

# Remove existing database if it exists
rm -f "$DB_PATH"

# Create tables and insert data
sqlite3 "$DB_PATH" <<EOF
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS casadeoracao (
  id INTEGER PRIMARY KEY,
  localidade TEXT
);

CREATE TABLE IF NOT EXISTS categoria (
  id INTEGER PRIMARY KEY,
  nome TEXT,
  descricao TEXT
);

CREATE TABLE IF NOT EXISTS funcao (
  id INTEGER PRIMARY KEY,
  id_categoria INTEGER NOT NULL,
  nome TEXT,
  descricao TEXT,
  FOREIGN KEY (id_categoria) REFERENCES categoria(id)
);

CREATE TABLE IF NOT EXISTS pessoa (
  id INTEGER PRIMARY KEY,
  nome TEXT,
  comum INTEGER,
  telefone1 TEXT,
  telefone2 TEXT,
  FOREIGN KEY (comum) REFERENCES casadeoracao(id)
);

CREATE TABLE IF NOT EXISTS pessoa_funcao_casadeoracao (
  id INTEGER PRIMARY KEY,
  id_pessoa INTEGER NOT NULL,
  id_funcao INTEGER NOT NULL,
  id_casadeoracao INTEGER NOT NULL,
  FOREIGN KEY (id_pessoa) REFERENCES pessoa(id),
  FOREIGN KEY (id_funcao) REFERENCES funcao(id),
  FOREIGN KEY (id_casadeoracao) REFERENCES casadeoracao(id)
);

INSERT INTO casadeoracao (localidade) VALUES
  ('Perocão'),
  ('Setiba'),
  ('Bela Vista'),
  ('Alfredo Chaves'),
  ('São Gabriel'),
  ('Ipiranga');
EOF

echo "Database populated successfully!"
