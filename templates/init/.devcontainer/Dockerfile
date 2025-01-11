FROM python:3.13.1-slim-bullseye

ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    gettext \
    jq \
    ripgrep \
    fd-find \
    tree \
    less \
    coreutils \
    bash-completion \
    vim \
    shellcheck \
    wget && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    wget https://github.com/dandavison/delta/releases/download/0.18.2/git-delta_0.18.2_amd64.deb && \
    dpkg -i git-delta_0.18.2_amd64.deb && \
    rm -rf git-delta_0.18.2_amd64.deb && \
    wget https://github.com/alexellis/arkade/releases/download/0.11.31/arkade -O /usr/local/bin/arkade && \
    chmod +x /usr/local/bin/arkade && \
    arkade get \
    yq \
    gh \
    viddy && \
    mv $HOME/.arkade/bin/* /usr/local/bin/ && \
    rm -rf $HOME/.arkade/ && \
    cd /tmp && wget https://github.com/owenthereal/ccat/releases/download/v1.1.0/linux-amd64-1.1.0.tar.gz && \
    tar -xvzf linux-amd64-1.1.0.tar.gz && \
    mv linux-amd64-1.1.0/ccat /usr/local/bin && \
    chmod +x /usr/local/bin/ccat && \
    rm -rf /tmp/linux-amd64-1.1.0 &&\
    cd /tmp && wget https://github.com/lsd-rs/lsd/releases/download/v1.1.5/lsd-v1.1.5-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xvzf lsd-v1.1.5-x86_64-unknown-linux-gnu.tar.gz && \
    mv lsd-v1.1.5-x86_64-unknown-linux-gnu/lsd /usr/local/bin && \
    chmod +x /usr/local/bin/lsd && \
    rm -rf lsd-v1.1.5-x86_64-unknown-linux-gnu && \
    cd /tmp && wget https://github.com/starship/starship/releases/download/v1.21.1/starship-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xvzf starship-x86_64-unknown-linux-gnu.tar.gz && \
    mv starship /usr/local/bin && \
    chmod +x /usr/local/bin/starship && \
    cd /tmp && wget https://github.com/astral-sh/uv/releases/download/0.5.6/uv-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xvzf uv-x86_64-unknown-linux-gnu.tar.gz && \
    chmod +x uv-x86_64-unknown-linux-gnu/* && \
    mv uv-x86_64-unknown-linux-gnu/* /usr/local/bin && \
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.16/tailwindcss-linux-x64 && \
    chmod +x tailwindcss-linux-x64 && \
    mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss && \
    cd /tmp && wget https://github.com/sirwart/ripsecrets/releases/download/v0.1.8/ripsecrets-0.1.8-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xvzf ripsecrets-*.tar.gz && \
    chmod +x ripsecrets-0.1.8-x86_64-unknown-linux-gnu/* && \
    mv ripsecrets-0.1.8-x86_64-unknown-linux-gnu/ripsecrets /usr/local/bin && \
    wget https://github.com/biomejs/biome/releases/download/cli%2Fv1.9.4/biome-linux-x64 && \
    chmod +x biome-linux-x64 && \
    mv biome-linux-x64 /usr/local/bin/biome && \
    cd /tmp && curl -sLO https://github.com/nushell/nushell/releases/download/0.101.0/nu-0.101.0-x86_64-unknown-linux-musl.tar.gz && \
    tar -xvzf nu-*.tar.gz && \
    cp nu*/n* /usr/local/bin && \
    cd /tmp && curl -sLO https://github.com/zellij-org/zellij/releases/download/v0.41.2/zellij-x86_64-unknown-linux-musl.tar.gz && \
    tar -xvzf zellij-*.tar.gz && mv zellij /usr/local/bin && \
    rm -rf /tmp/*




USER devuser

RUN mkdir -p /home/devuser/.bashrc.d/ /home/devuser/.config/git /home/devuser/.cache/pre-commit && \
    echo 'for f in ~/.bashrc.d/*; do source $f; done' >> /home/devuser/.bashrc

COPY bashrc.d/* /home/devuser/.bashrc.d/
COPY config/git/config /etc/gitconfig
COPY config/ripgrep/* /home/devuser/.config/
COPY config/starship/* /home/devuser/.config/

WORKDIR /home/devuser/workspace
