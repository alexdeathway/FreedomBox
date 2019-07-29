#
# This file is part of FreedomBox.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Decorators for the backup views.
"""

import functools
import os

from . import SESSION_PATH_VARIABLE


def delete_tmp_backup_file(function):
    """Decorator to delete uploaded backup files.

    XXX: Implement a better way to delete uploaded files.

    """

    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        path = request.session.get(SESSION_PATH_VARIABLE, None)
        if path:
            if os.path.isfile(path):
                os.remove(path)
            del request.session[SESSION_PATH_VARIABLE]
        return function(request, *args, **kwargs)

    return wrapper
