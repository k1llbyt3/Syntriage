# Use Node.js 20 base image
FROM node:20-slim AS base

# 1. Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install

# 2. Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Disable telemetry for build
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# 3. Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy essential files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Important for Cloud Run: listen on all interfaces
ENV HOSTNAME "0.0.0.0"
ENV PORT 8080

USER nextjs

EXPOSE 8080

CMD ["npm", "start", "--", "-p", "8080"]
