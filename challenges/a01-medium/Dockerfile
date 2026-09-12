FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN addgroup -S lab && adduser -S lab -G lab && chown -R lab:lab /app
USER lab
ENV NODE_ENV=production PORT=6002
EXPOSE 6002
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O - http://127.0.0.1:6002/healthz || exit 1
CMD ["npm", "start"]
