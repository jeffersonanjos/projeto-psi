# 📅 Cronograma e Requisitos do Projeto

## ✅ Etapas do Projeto e Responsáveis

| Tarefa                                                                                   | Responsável              | Status        | Início       | Término      | Observações        |
|------------------------------------------------------------------------------------------|--------------------------|---------------|--------------|--------------|--------------------|
| Definir grupo e temática / Criação do projeto no GitHub                                  | Todos                    | Feita         | 05/05/2025   | 09/05/2025   |                    |
| Definir layout da aplicação                                                              | Integrante 1 e 2         | Feita         | 12/05/2025   | 12/06/2025   |                    |
| Modelagem do banco de dados                                                              | Integrante 1             | Feita         | 19/05/2025   | 09/06/2025   | SQLAlchemy         |
| Implementação de rotas (parte delas). Testar layout e operações com banco de dados       | Integrante 1 e 2         | Feita         | 12/06/2025   | 12/07/2025   | Blueprints / Fetch |
| Implementação de autenticação de usuário (registro/login)                                | Integrante 1             | Não iniciada  | 14/07/2025   | 11/08/2025   | Flask-Login / JWT  |
| Integração do sistema de login com a interface                                           | Integrante 2             | Não iniciada  | 14/07/2025   | 11/08/2025   | Formulários Jinja  |
| Implementação de regras de negócio da aplicação (autorização)                            | Integrante 1             | Não iniciada  | 09/09/2025   | 06/10/2025   |                    |
| Criação de páginas de erro e mensagens de acesso negado                                  | Integrante 2             | Não iniciada  | 09/09/2025   | 06/10/2025   | UX/Acessibilidade  |
| Implementação de operações da aplicação (requisitos funcionais)                          | Integrante 1             | Não iniciada  | 06/10/2025   | 07/11/2025   | Favoritar receitas |
| Implementação de páginas para essas operações no frontend                                | Integrante 2             | Não iniciada  | 06/10/2025   | 07/11/2025   | Consumo de dados   |
| Envio de e-mails (definir e implementar)                                                 | Integrante 3             | Não iniciada  | 07/11/2025   | 08/12/2025   | Flask-Mail         |
| Implementar notificações (e-mail e web)                                                  | Integrante 2 e 3         | Não iniciada  | 07/11/2025   | 08/12/2025   | SweetAlert2        |
| Gerar relatórios da aplicação                                                            | Integrante 3             | Não iniciada  | 24/11/2025   | 08/12/2025   | PDF (WeasyPrint)   |
| Criar página de download/visualização de relatórios                                      | Integrante 2             | Não iniciada  | 24/11/2025   | 08/12/2025   | Interface web      |
| Ajustes finais do projeto                                                                | Todos                    | Não iniciada  | 01/12/2025   | 15/12/2025   |                    |
| Apresentação final                                                                       | Todos                    | Não iniciada  | 17/12/2025   | 17/12/2025   | Slides e demo      |


---

## 📌 Observações Importantes

- O projeto está sendo desenvolvido em Python com Flask para o backend.
- Banco de dados será modelado com SQLAlchemy e migrations usando Flask-Migrate.
- Interface será feita com Jinja2 e Bootstrap ou Tailwind CSS.
- O sistema incluirá autenticação, autorização, notificações, envio de e-mails e geração de relatórios.

---

## 📎 Tecnologias Envolvidas

- **Backend:** Python, Flask, Flask-RESTful, Flask-Login/JWT, Flask-Mail
- **Banco de Dados:** SQLAlchemy, SQLite (dev), PostgreSQL/MariaDB (produção)
- **Frontend:** Jinja2, Bootstrap/Tailwind, JavaScript
- **Relatórios e E-mail:** WeasyPrint / ReportLab, Flask-Mail, SweetAlert2

---

## 🧑‍💻 Equipe e Papéis

- **Integrante 1 (Backend & Banco de Dados)**
- **Integrante 2 (Frontend & UI/UX)**
- **Integrante 3 (Funcionalidades Avançadas & Relatórios)**
