import sqlite3
import unicodedata

DB_PATH = "database.db"


def slugify(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().replace(" ", "-")


def init_db(conn: sqlite3.Connection):
    schema = """
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
    """
    conn.executescript(schema)
    conn.commit()


def build_index(conn: sqlite3.Connection):
    cursor = conn.execute("SELECT id, localidade FROM casadeoracao ORDER BY localidade")
    casas = cursor.fetchall()

    cards_html = ""
    for cid, localidade in casas:
        slug = slugify(localidade)
        cards_html += f'      <a href="{slug}.html" class="card">{localidade}</a>\n'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Casas de Oração</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <main>
    <h1>Casas de Oração</h1>
    <div class="grid">
{cards_html}    </div>
  </main>
</body>
</html>"""

    with open("generated/index.html", "w") as f:
        f.write(html)


def build_church_pages(conn: sqlite3.Connection):
    casas = conn.execute(
        "SELECT id, localidade FROM casadeoracao ORDER BY localidade"
    ).fetchall()
    categorias = conn.execute(
        "SELECT id, nome, descricao FROM categoria ORDER BY nome"
    ).fetchall()

    for cid, localidade in casas:
        church_slug = slugify(localidade)
        cards_html = ""
        for kid, nome, descricao in categorias:
            cat_slug = slugify(nome)
            link = f"{church_slug}_{cat_slug}.html"
            cards_html += f'      <a href="{link}" class="card"><span class="card-title">{nome}</span><span class="card-desc">{descricao}</span></a>\n'

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{localidade} — Casas de Oração</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <main>
    <a href="index.html" class="back">← Voltar</a>
    <h1>{localidade}</h1>
    <div class="grid">
{cards_html}    </div>
  </main>
</body>
</html>"""

        with open(f"generated/{church_slug}.html", "w") as f:
            f.write(html)


def build_category_pages(conn: sqlite3.Connection):
    casas = conn.execute(
        "SELECT id, localidade FROM casadeoracao ORDER BY localidade"
    ).fetchall()
    categorias = conn.execute(
        "SELECT id, nome, descricao FROM categoria ORDER BY nome"
    ).fetchall()

    for cid, localidade in casas:
        church_slug = slugify(localidade)
        for kid, nome, descricao in categorias:
            cat_slug = slugify(nome)
            church_link = f"{church_slug}.html"

            pessoas = conn.execute(
                """
                SELECT p.nome, p.telefone1, p.telefone2
                FROM pessoa p
                JOIN pessoa_funcao_casadeoracao pfc ON p.id = pfc.id_pessoa
                WHERE pfc.id_casadeoracao = ? AND pfc.id_funcao IN (
                    SELECT f.id FROM funcao f WHERE f.id_categoria = ?
                )
                ORDER BY p.nome
                """,
                (cid, kid),
            ).fetchall()

            if pessoas:
                rows_html = ""
                for nome, tel1, tel2 in pessoas:
                    telefone = tel1 or tel2 or ""
                    rows_html += f"      <tr><td>{nome}</td><td>{telefone}</td></tr>\n"
                people_html = f"""      <table>
        <thead><tr><th>Nome</th><th>Telefone</th></tr></thead>
        <tbody>
{rows_html}        </tbody>
      </table>"""
            else:
                people_html = '      <p class="empty">Nenhuma pessoa cadastrada nesta categoria.</p>'

            html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nome} — {localidade}</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <main>
    <a href="{church_link}" class="back">← Voltar</a>
    <h1>{localidade} — {nome}</h1>
{people_html}
  </main>
</body>
</html>"""

            with open(f"generated/{church_slug}_{cat_slug}.html", "w") as f:
                f.write(html)


def main():
    import os
    import shutil

    os.makedirs('generated', exist_ok=True)

    if os.path.isdir('static'):
        dest = os.path.join('generated', 'static')
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree('static', dest)

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        build_index(conn)
        build_church_pages(conn)
        build_category_pages(conn)


if __name__ == "__main__":
    main()
