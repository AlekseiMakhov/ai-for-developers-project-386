FROM mcr.microsoft.com/playwright:v1.59.1-jammy

WORKDIR /app

COPY package.json package-lock.json .npmrc ./
RUN npm install && npx playwright install chromium

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
