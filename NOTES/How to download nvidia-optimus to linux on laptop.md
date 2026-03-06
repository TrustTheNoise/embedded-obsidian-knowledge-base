Tags: #linux
## Nvidia-optimus
1) sudo pacman -S nvidia
2) sudo pacman -S optimus-manager
3) sudo -E nvim /etc/gdm/custom.conf убрать # в "#WaylandEnable=false"
4) sudo -E nvim /etc/optimus-manager/optimus-manager.conf вставить текст из файла
