# 🔧 SETUP - Primeiros Passos

## 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/planner-nutricional-whatsapp.git
cd planner-nutricional-whatsapp
```

## 2. Criar ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

## 3. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

## 4. Configurar variáveis de ambiente

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com suas credenciais
nano .env (ou abra em VS Code)
```

### Valores para configurar:

```
DATABASE_URL=postgresql://user:password@localhost:5432/planner_db
SECRET_KEY=gere com: openssl rand -hex 32
WHATSAPP_ACCESS_TOKEN=seu_token_aqui
```

## 5. Criar banco de dados

Se usar PostgreSQL local:

```bash
createdb planner_db
```

Ou use Supabase (grátis): https://supabase.com

## 6. Rodar servidor

```bash
uvicorn main:app --reload
```

Acesse: http://localhost:8000/docs

## 7. Enviar para GitHub

```bash
git add .
git commit -m "Primeiro envio - Sistema Planner"
git push origin main
```

## 8. Deploy no Vercel (depois)

Quando o backend estiver pronto:

1. Push para GitHub
2. Conecte no Vercel
3. Configure variáveis de ambiente
4. Deploy!

---

Pronto! Seu servidor está rodando! 🚀
