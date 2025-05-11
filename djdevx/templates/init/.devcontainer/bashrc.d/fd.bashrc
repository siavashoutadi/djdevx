mkdir -p ~/.local/bin/
[ ! -L ~/.local/bin/fd ] && ln -s $(which fdfind) ~/.local/bin/fd
