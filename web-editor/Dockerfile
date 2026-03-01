# ── Stage 1: dependency installer ────────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

COPY package*.json ./
# install, si no encuentra el package-lock.json lo genera
RUN npm install


# ── Stage 2: development runtime ─────────────────────────────────────────────
FROM node:20-alpine AS runtime

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Config files needed at startup (source overridden by bind-mount in dev)
COPY vite.config.js index.html ./
COPY src/ ./src/

# Expose Vite dev server port
EXPOSE 3000

# --host exposes the server to the Docker network
CMD ["npm", "run", "dev"]
