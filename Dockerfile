#  Build Go
FROM golang:1.23-alpine AS go-builder

# Build final image
FROM python:3.12-slim-bookworm

# Copy Go binary from the Go builder stage
COPY --from=go-builder /usr/local/go/ /usr/local/go/

# Update the PATH to include Go binaries
ENV PATH="/usr/local/go/bin:${PATH}"

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the current directory contents into the container at /usr/src/app
WORKDIR /usr/src/app
COPY . .

# Install required dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    make zip curl git && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /usr/share/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install gh -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.8.3

# Install python dependencies
RUN poetry install && rm -rf $POETRY_CACHE_DIR   
