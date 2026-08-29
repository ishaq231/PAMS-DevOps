# ---- Stage 1: build ----------------------------------------------------
# Compiles the React app into static HTML/CSS/JS. Nothing from this stage
# ships except the build output, so node_modules never reaches production.
FROM node:22-slim AS build

WORKDIR /app

# Copy manifests first so this layer (and the install) is cached whenever
# only application code changes — same trick as requirements.txt in the API.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite substitutes import.meta.env.* into the bundle AT BUILD TIME, so the API
# URL has to arrive here as a build arg. Passing it at `docker run` would be
# too late — the value is already compiled into the JavaScript.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=https://pams-devops.onrender.com

RUN npm run build

# ---- Stage 2: serve ----------------------------------------------------
# nginx serving static files. No Node, no npm, no source code — just the
# compiled output, which keeps the image small and the attack surface tiny.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
