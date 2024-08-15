# Base devcontainer image with Python 3.12 installed
FROM mcr.microsoft.com/devcontainers/python:3.12

# Preserve command history
RUN SNIPPET="export HISTFILE=/commandhistory/.bash_history && mkdir -p /commandhistory && touch /commandhistory/.bash_history" \
    && echo $SNIPPET >> /root/.bashrc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"