FROM node:18-alpine

WORKDIR /app
RUN npm install -g npm@10.7.0
COPY package.json package-lock.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
EXPOSE 3000
