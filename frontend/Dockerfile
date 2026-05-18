FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ENV PORT=5173
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.d/10-runtime-env.sh /docker-entrypoint.d/10-runtime-env.sh
RUN chmod +x /docker-entrypoint.d/10-runtime-env.sh
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173
