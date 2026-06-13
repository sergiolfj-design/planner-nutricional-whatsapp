# 🍎 Planner Nutricional via WhatsApp

Sistema de acompanhamento nutricional integrado ao WhatsApp para nutricionistas e pacientes.

## 📋 Estrutura do Projeto

```
planner-nutricional-whatsapp/
├── backend/
│   ├── app/
│   │   ├── routes/          # Endpoints da API
│   │   ├── services/        # Lógica de negócio
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── schemas.py       # Schemas Pydantic
│   │   ├── config.py        # Configurações
│   │   ├── database.py      # Setup do BD
│   │   └── __init__.py
│   ├── main.py              # Aplicação principal
│   ├── requirements.txt     # Dependências
│   ├── .env.example         # Variáveis de exemplo
│   ├── .env                 # Variáveis locais
│   └── .gitignore
└── frontend/
    ├── src/
    └── public/
```

## 🚀 Começando

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar banco de dados

```bash
# Editar .env com suas credenciais do PostgreSQL
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/planner_db
```

### 3. Rodar servidor

```bash
uvicorn main:app --reload
```

Acesse: http://localhost:8000/docs

## 📚 Documentação

- [QUICK_START.md](../QUICK_START.md) - Guia rápido
- [README.md](../README.md) - Documentação completa

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub!
