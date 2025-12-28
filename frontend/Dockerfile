# Multi-stage build for React + Vite frontend

# Stage 1: Build the application
FROM node:20-alpine as builder

WORKDIR /app

# Build arguments for environment variables
ARG VITE_API_URL=http://localhost:5000/api/v1
ARG VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_test_publishable_key
ARG VITE_APP_NAME=Cookie Shop
ARG VITE_APP_URL=http://localhost:3000

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_URL=$VITE_APP_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
