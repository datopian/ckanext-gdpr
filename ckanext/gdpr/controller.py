import logging

from ckan.controllers.user import UserController

import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
UsernamePasswordError = logic.UsernamePasswordError


class GdprUserController(UserController):


    def request_reset(self):
        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': request.params.get('user')}
        try:
            check_access('request_reset', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to request reset password.'))

        if request.method == 'POST':
            id = request.params.get('user')

            context = {'model': model,
                       'user': c.user}

            data_dict = {'id': id}
            user_obj = None
            try:
                user_dict = get_action('user_show_gdpr')(context, data_dict)
                user_obj = context['user_obj']
            except NotFound:
                # Try searching the user
                del data_dict['id']
                data_dict['q'] = id

                if id and len(id) > 2:
                    user_list = get_action('user_list_gdpr')(context, data_dict)
                    if len(user_list) == 1:
                        # This is ugly, but we need the user object for the
                        # mailer,
                        # and user_list does not return them
                        del data_dict['q']
                        data_dict['id'] = user_list[0]['id']
                        user_dict = get_action('user_show_gdpr')(context, data_dict)
                        user_obj = context['user_obj']
                    elif len(user_list) > 1:
                        h.flash_error(_('"%s" matched several users') % (id))
                    else:
                        h.flash_error(_('No such user: %s') % id)
                else:
                    h.flash_error(_('No such user: %s') % id)

            if user_obj:
                try:
                    mailer.send_reset_link(user_obj)
                    h.flash_success(_('Please check your inbox for '
                                    'a reset code.'))
                    h.redirect_to('/')
                except mailer.MailerException as e:
                    h.flash_error(_('Could not send reset link: %s') %
                                  text_type(e))
			
			return render('user/request_reset.html')


    def index(self):
        '''We are overwriting the default index action in
        order to make the users list available only
        for system administrators
        '''

        context = {'return_query': True, 'user': c.user,
                   'auth_user_obj': c.userobj}

        data_dict = {'q': c.q,
                     'order_by': c.order_by}

        try:
            check_access('sysadmin', context, data_dict)
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        return super(GdprUserController, self).index()

    
    def activity(self, id, offset=0):
        '''Render this user's public activity stream page.'''

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': id, 'user_obj': c.userobj,
                     'include_num_followers': True}
        try:
            toolkit.check_access('sysadmin', context, data_dict)
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        self._setup_template_variables(context, data_dict)

        try:
            c.user_activity_stream = get_action('user_activity_list_html')(
                context, {'id': c.user_dict['id'], 'offset': offset})
        except ValidationError:
            base.abort(400)

		return render('user/activity_stream.html')