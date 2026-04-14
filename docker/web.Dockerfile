FROM mcr.microsoft.com/playwright:v1.49.0-jammy

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install && npx playwright install chromium

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
