# 📋 Divisão de Tarefas por Integrante para o Projeto

## 💻 **Integrante 1: Backend & Banco de Dados:**

### 🧠 Semana 19/05 a 09/06):
**Tecnologias:**
```sh
Python
Flask
```
1. Modelagem do Banco de Dados (Semana 19/05 a 09/06):
  - Usar SQLAlchemy para criar modelos: User, Recipe, Ingredient, Comment,
  Favorite.
  - Escolher SGBD (SQLite para desenvolvimento, PostgreSQL/MariaDB para
  produção).
  - Criar migrations com Flask-Migrate (ou Alembic).

### 2. **Implementar login/registro com Flask-Login ou JWT (para API)**
  - Implementar login/registro com Flask-Login ou JWT (para API).
  - Roles (usuário comum/admin) com decorators (ex: @admin_required)

### 3. **Regras de Negócio (Semana 09/09 a 06/10):**
  - Lógica para favoritar receitas (many-to-many entre User e Recipe).
  - Restrições (ex: só o autor pode editar receita).

### **4. API/Rotas Básicas (Semana 12/06 a 12/07):**
  - Criar endpoints com **Flask-RESTful ou Blueprints:**
    - GET /recipes?ingredient=tomate (busca).
    - POST /recipes (criar receita).


# 💻 Integrante 2: Frontend & UI/UX

### 🖌 Semana 12/05 a 12/06 - Layout
**Tecnologias:**
```sh
Jinja2 + Bootstrap/Tailwind CSS
```

### **1. Layout da Aplicação (Semana 12/05 a 12/06):**
  - Usar **Jinja2** para templates + **Bootstrap** ou **Tailwind CSS**.
  - Páginas essenciais:
  - index.html (lista de receitas).
    - recipe_detail.html (detalhes + comentários).
    - profile.html (perfil do usuário)
  - Criar páginas: Home, Perfil, Detalhes da Receita.
    
### **2. Integração Front-Back (Semana 12/06 a 12/07):**
  - Consumir dados das rotas do Flask nos templates Jinja2.
  - Busca por ingredientes (JavaScript fetch + endpoint /**recipes?ingredient=...**).
    
### **3. Notificações na UI (Semana 07/11 a 08/12):**
  - Alertas com SweetAlert2 ou Flask-Flash.
  - Integrar com sistema de e-mails (trabalho com Integrante 3).


# 💻 Integrante 3: Funcionalidades Avançadas & Relatórios

### **1. Envio de E-mails (Semana 07/11 a 08/12):**
```sh
  - Usar Flask-Mail ou SendGrid API para:
    - Notificar novos comentários.
    - Confirmação de registro.

```

### **2. Gerar PDFs (Semana 24/11 a 08/12):**

  - Usar ReportLab ou WeasyPrint para gerar lista de compras em PDF.

### 3. Deploy Básico (Semana 01/12 a 15/12):
- Subir aplicação no Render, Heroku ou PythonAnywhere.

*Apresentação (17/12):* *Preparar slides e demonstração*
