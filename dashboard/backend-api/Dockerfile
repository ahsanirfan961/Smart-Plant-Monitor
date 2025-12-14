FROM node:18-alpine

WORKDIR /app

COPY backend-api/package*.json ./
RUN npm install

COPY backend-api . 
COPY frontend ../frontend

EXPOSE 3000

CMD ["npm", "start"]
