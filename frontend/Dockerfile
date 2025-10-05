# build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# production stage
FROM node:18-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit dev
COPY --from=build /app/build ./build
EXPOSE 3000
ENV HOST=0.0.0.0
ENV PORT=3000
CMD ["node", "build"]
