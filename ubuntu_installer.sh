#!/bin/bash

source requirements.sh

color
heading "Ubuntu" "Installer"

copy_repo() {
    repo=$(git config --get remote.origin.url)
    dir="${repo##*'/'}"
    dir="${1}/${dir%.git}"
    git clone "$repo" "${dir}"
}

if [ "$HOME" = "/data/data/com.termux/files/home" ]; then
    install "Proot-Distro" "Git" "proot-distro" "git"

    heading "Ubuntu" "Installer"
    proot-distro install ubuntu
    echo "proot-distro login ubuntu" >"${PREFIX}/bin/ubuntu"
    chmod +x "${PREFIX}/bin/ubuntu"

    [ -f "$HOME/.bashrc" ] && ! grep -q "ubuntu" "$HOME/.bashrc" &&
        sed -i "1i\[ \$(ps -e | grep -cwi proot) -le 2 ] && ubuntu" "$HOME/.bashrc"
    [ -f "$HOME/.zshrc" ] && ! grep -q "ubuntu" "$HOME/.zshrc" &&
        sed -i "1i\[ \$(ps -e | grep -cwi proot) -le 2 ] && ubuntu" "$HOME/.zshrc"

    grep -q "/data/data/com.termux/files/usr/bin" "$PREFIX/var/lib/proot-distro/installed-rootfs/ubuntu/etc/environment" &&
        sed -i "s|:/data/data/com.termux/files/usr/bin:|:|" "$PREFIX/var/lib/proot-distro/installed-rootfs/ubuntu/etc/environment"

    copy_repo "$PREFIX/var/lib/proot-distro/installed-rootfs/ubuntu/root"
elif [ "$HOME" = "/root" ]; then
    echo -ne "${c[33]}Enter your username: ${c[0]}" && read -r user
    echo -ne "${c[33]}Enter your password: ${c[0]}" && read -ers pass
    echo -ne "${c[33]}Enter password again: ${c[0]}" && read -ers pass_cnf
    [ "$pass" != "$pass_cnf" ] && echo -ne "${c[31]}Passwords don't match!${c[0]}" && exit 1

    install "Git" "nano" "Curl" "git" "nano" "curl"
    echo -e "5\n44" | apt install tzdata -y
    echo -e "32\n1" | apt install keyboard-configuration -y

    ! grep -q "${user}" "/etc/passwd" &&
        sudo useradd -m -u 2412 -U -s /bin/bash "${user}"
    echo -e "${pass}\n${pass}" | sudo passwd "${user}"

    ! grep -q "${user}" "/etc/sudoers" &&
        sed -i "/root.*ALL=(ALL:ALL) ALL/a ${user} ALL=(ALL:ALL) ALL" "/etc/sudoers" "/etc/sudoers"

    echo "proot-distro login --user ${user} ubuntu" >"/data/data/com.termux/files/usr/bin/ubuntu"

    cp ./Files/pip.conf "/etc/pip.conf"

    copy_repo "/home/${user}"
else
    echo "Ubuntu Desktop Installer"
fi
