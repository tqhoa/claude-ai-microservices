FROM node:22-alpine AS base
RUN corepack enable
WORKDIR /app

# Development target
FROM base AS development
COPY package.json ./
RUN npm install --ignore-scripts 2>/dev/null; npx -y serve --version || true
COPY . .
EXPOSE 3000
CMD ["npx", "serve", "-s", ".", "-l", "3000"]

# Build
FROM base AS builder
COPY package.json ./
RUN npm install 2>/dev/null || true
COPY . .
RUN mkdir -p dist && cp index.html dist/

# Production target (Nginx serve static)
FROM nginx:1.27-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
