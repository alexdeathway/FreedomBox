# SPDX-License-Identifier: AGPL-3.0-or-later

import django.views.generic
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)

from plinth import actions
from plinth.errors import ActionError
from plinth.modules import first_boot
from plinth.utils import is_user_admin
from plinth.views import AppView

from . import get_last_admin_user
from .forms import (CreateUserForm, FirstBootForm, UserChangePasswordForm,
                    UserUpdateForm)


class ContextMixin(object):
    """Mixin to add 'title' to the template context."""

    def get_context_data(self, **kwargs):
        """Add self.title to template context."""
        context = super(ContextMixin, self).get_context_data(**kwargs)
        context['title'] = getattr(self, 'title', '')
        return context


class UserCreate(ContextMixin, SuccessMessageMixin, CreateView):
    """View to create a new user."""
    form_class = CreateUserForm
    template_name = 'users_create.html'
    model = User
    success_message = ugettext_lazy('User %(username)s created.')
    success_url = reverse_lazy('users:create')
    title = ugettext_lazy('Create User')

    def get_form_kwargs(self):
        """Make the request object available to the form."""
        kwargs = super(UserCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        """Return the URL to redirect to in case of successful updation."""
        return reverse('users:index')


class UserList(AppView, ContextMixin, django.views.generic.ListView):
    """View to list users."""
    model = User
    template_name = 'users_list.html'
    title = ugettext_lazy('Users')
    app_id = 'users'

    def get_context_data(self, *args, **kwargs):
        context = super(UserList, self).get_context_data(*args, **kwargs)
        context['last_admin_user'] = get_last_admin_user()
        return context


class UserUpdate(ContextMixin, SuccessMessageMixin, UpdateView):
    """View to update a user's details."""
    template_name = 'users_update.html'
    model = User
    form_class = UserUpdateForm
    slug_field = 'username'
    success_message = ugettext_lazy('User %(username)s updated.')
    title = ugettext_lazy('Edit User')

    def dispatch(self, request, *args, **kwargs):
        """Handle a request and return a HTTP response."""
        if self.request.user.get_username() != self.kwargs['slug'] \
                and not is_user_admin(self.request):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Make the request object available to the form."""
        kwargs = super(UserUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['username'] = self.object.username
        return kwargs

    def get_initial(self):
        """Return the data for initial form load."""
        initial = super(UserUpdate, self).get_initial()
        try:
            ssh_keys = actions.superuser_run(
                'ssh', ['get-keys', '--username', self.object.username])
            initial['ssh_keys'] = ssh_keys.strip()
            initial['language'] = self.object.userprofile.language
        except ActionError:
            pass

        return initial

    def get_success_url(self):
        """Return the URL to redirect to in case of successful updation."""
        return reverse('users:edit', kwargs={'slug': self.object.username})


class UserDelete(ContextMixin, DeleteView):
    """Handle deleting users, showing a confirmation dialog first.

    On GET, display a confirmation page.
    On POST, delete the user.
    """
    template_name = 'users_delete.html'
    model = User
    slug_field = 'username'
    success_url = reverse_lazy('users:index')
    title = ugettext_lazy('Delete User')

    def delete(self, *args, **kwargs):
        """Set the success message of deleting the user.

        The SuccessMessageMixin doesn't work with the DeleteView on Django1.7,
        so set the success message manually here.
        """
        output = super(UserDelete, self).delete(*args, **kwargs)

        message = _('User {user} deleted.').format(user=self.kwargs['slug'])
        messages.success(self.request, message)

        try:
            actions.superuser_run('users',
                                  ['remove-user', self.kwargs['slug']])
        except ActionError:
            messages.error(self.request, _('Deleting LDAP user failed.'))

        return output


class UserChangePassword(ContextMixin, SuccessMessageMixin, FormView):
    """View to change user password."""
    template_name = 'users_change_password.html'
    form_class = UserChangePasswordForm
    title = ugettext_lazy('Change Password')
    success_message = ugettext_lazy('Password changed successfully.')

    def dispatch(self, request, *args, **kwargs):
        """Handle a request and return a HTTP response."""
        if self.request.user.get_username() != self.kwargs['slug'] \
                and not is_user_admin(self.request):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Make the user object available to the form."""
        kwargs = super(UserChangePassword, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['user'] = User.objects.get(username=self.kwargs['slug'])
        return kwargs

    def get_success_url(self):
        """Return the URL to go to on successful sumbission."""
        return reverse('users:edit', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        """Save the form if the submission is valid.

        Django user session authentication hashes are based on password to have
        the ability to logout all sessions on password change.  Update the
        session authentications to ensure that the current sessions is not
        logged out.
        """
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(UserChangePassword, self).form_valid(form)


class FirstBootView(django.views.generic.CreateView):
    """Create user account and log the user in."""
    template_name = 'users_firstboot.html'

    form_class = FirstBootForm

    def get_form_kwargs(self):
        """Make request available to the form (to insert messages)"""
        kwargs = super(FirstBootView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        """Return the next first boot step after valid form submission."""
        return reverse(first_boot.next_step())
