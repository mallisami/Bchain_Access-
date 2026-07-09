FROM nikolaik/python-nodejs:python3.11-nodejs18-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Set work directory
WORKDIR /app

# Copy package files first for caching
COPY smart_contracts/package*.json /app/smart_contracts/

# Install Node.js dependencies
RUN cd /app/smart_contracts && npm install

# Copy requirements file first for caching
COPY backend/requirements.txt /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the rest of the application
COPY . /app

# Compile Solidity smart contracts
RUN cd /app/smart_contracts && npx hardhat compile

# Make the start script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 5000

# Set entrypoint to the startup script
ENTRYPOINT ["/app/start.sh"]
