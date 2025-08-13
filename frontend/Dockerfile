FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ENV HOST=0.0.0.0
ENV WATCHPACK_POLLING=true
ENV WDS_SOCKET_HOST=localhost

EXPOSE 3000

CMD ["npm", "start"]
