# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import ugettext_lazy as _

clients = [{
    'name': _('MediaWiki'),
    'platforms': [{
        'type': 'web',
        'url': '/mediawiki'
    }]
}]

backup = {
    'config': {
        'files': ['/etc/mediawiki/FreedomBoxSettings.php']
    },
    'data': {
        'directories': ['/var/lib/mediawiki-db/']
    },
    'services': ['mediawiki-jobrunner']
}
