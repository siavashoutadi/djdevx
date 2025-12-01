export RIPGREP_CONFIG_PATH=~/.config/ripgreprc
function rg { command rg --json $@ | delta; }
