# Chat API - Desafio Positivo S+ usando FastAPI 

Este projeto é uma API de chat baseada em FastAPI com autenticação JWT e integração com MongoDB para o desafio técnico para desenvolvedor Positivo S+.

## Tecnologias Utilizadas
- **FastAPI**
- **MongoDB** (via Mongo Atlas)
- **Docker e Docker Compose**
- **Autenticação JWT**

## Como Executar:

### Com Docker
1. Substitua `<usuario>` e `<senha>` no `docker-compose.yml` pela sua conexão Mongo Atlas.
2. Execute:
   ```sh
   docker-compose up --build
   ```
3. A API estará disponível em `http://localhost:8000`.

### Localmente (sem Docker)
1. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
2. Execute a aplicação:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Endpoints Principais

- **Autenticação**
  - `POST /token`: Gera token JWT.

- **Chat**
  - `POST /chat/start`: Inicia um chat.
  - `POST /chat/send`: Envia uma mensagem.
  - `POST /chat/end`: Encerra o chat.
  - `GET /reports`: Obtém relatórios.

## Observações
- O MongoDB precisa estar configurado corretamente.
- O JWT expira em 15 minutos.

## Licença
MIT
