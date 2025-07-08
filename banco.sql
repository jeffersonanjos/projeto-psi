-- Usuário
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE,
    senha TEXT,
    foto_perfil TEXT,
    bio TEXT
);

-- Receita
CREATE TABLE receita (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    modo_preparo TEXT,
    imagem TEXT,
    data_postagem TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Ingrediente
CREATE TABLE ingrediente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

-- ReceitaIngrediente
CREATE TABLE receita_ingrediente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receita_id INTEGER,
    ingrediente_id INTEGER,
    quantidade TEXT,
    FOREIGN KEY (receita_id) REFERENCES receita(id),
    FOREIGN KEY (ingrediente_id) REFERENCES ingrediente(id)
);

-- Favorito
CREATE TABLE favorito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    receita_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (receita_id) REFERENCES receita(id)
);

-- Comentário
CREATE TABLE comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receita_id INTEGER,
    usuario_id INTEGER,
    conteudo TEXT,
    data_comentario TEXT,
    FOREIGN KEY (receita_id) REFERENCES receita(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Notificação
CREATE TABLE notificacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    comentario_id INTEGER,
    visualizado BOOLEAN,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (comentario_id) REFERENCES comentario(id)
);
