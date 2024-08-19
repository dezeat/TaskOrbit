# Base devcontainer image with Python 3.12 installed
FROM mcr.microsoft.com/devcontainers/python:3.12

# Add mounted bash_history to bash_rc
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo "$SNIPPET" >> "/root/.bashrc" \
    # Add git auto complete option to bash_rc
    && echo 'if [ -f /etc/bash_completion ] && ! shopt -oq posix; then' >> "/root/.bashrc" \
    && echo '    . /etc/bash_completion' >> "/root/.bashrc" \
    && echo 'fi' >> "/root/.bashrc"
    
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"