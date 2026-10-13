# Jezker

Jezker is a small lab setup for a split VM privacy box.

What it has
- a gateway VM
- a workstation VM
- Tor on the gateway
- a basic firewall
- a safe place to test browser privacy ideas

What to use
- Vagrant
- VirtualBox
- Ansible

Quick start
1. Install Vagrant and VirtualBox.
2. Open a terminal in this folder.
3. Run: vagrant up
4. Run: vagrant ssh gateway
5. Run: vagrant ssh workstation

This is a starter. You need to harden it more before using it for real work.
