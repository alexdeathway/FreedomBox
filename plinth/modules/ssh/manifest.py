# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Application manifest for ssh.
"""

backup = {
    'secrets': {
        'files': [
            '/etc/ssh/ssh_host_ecdsa_key', '/etc/ssh/ssh_host_ecdsa_key.pub',
            '/etc/ssh/ssh_host_ed25519_key',
            '/etc/ssh/ssh_host_ed25519_key.pub', '/etc/ssh/ssh_host_rsa_key',
            '/etc/ssh/ssh_host_rsa_key.pub'
        ]
    }
}
