FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=development
ENV PORT=3000

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

EXPOSE 3000

CMD ["npm", "run", "dev"]
