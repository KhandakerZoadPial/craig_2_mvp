# Start from a lightweight, official Node.js image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files and install dependencies first for layer caching
COPY package*.json ./
RUN npm install --omit=dev # Use --omit=dev to skip installing devDependencies like nodemon

# Copy the rest of the application code
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# The command to start the application
CMD ["node", "index.js"]