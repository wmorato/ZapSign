# --- Fase de Build ---
FROM node:20-alpine AS build

WORKDIR /app

# Copia os arquivos de configuração do projeto
COPY package.json package-lock.json ./

# Adiciona uma etapa para garantir que node_modules e package-lock.json sejam limpos
# antes de cada npm install, evitando problemas de cache ou resquícios.
RUN rm -rf node_modules && \
    rm -f package-lock.json

# Instala as dependências do Node.js
RUN npm install

# Copia o restante do código da aplicação
COPY . .

# Constrói a aplicação Angular para produção
RUN npm run build -- --output-path=./dist/browser --configuration production

# --- Fase de Servir (Nginx) ---
FROM nginx:alpine

# Copia a configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os conteúdos da pasta de build do Angular para o diretório de serviço do Nginx
COPY --from=build /app/dist/browser/browser /usr/share/nginx/html

# Expõe a porta padrão do Nginx
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]