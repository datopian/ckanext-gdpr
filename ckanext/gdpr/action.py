import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.logic.action

_check_access = logic.check_access


@toolkit.side_effect_free
def user_list(context, data_dict):
    '''We are overwriting the default user_list api action in
    order to make the users list available only
    for system administrators
    '''
    _check_access('sysadmin', context, data_dict)
    return logic.action.get.user_list(context, data_dict)


@toolkit.side_effect_free
def user_show(context, data_dict):
    '''Forbid anonymous access to user info.
    API call works with POST request with authorization header and id
    of desired user supplied.
    '''
    if context.get('user'):
        return logic.action.get.user_show(context, data_dict)
    else:
        raise toolkit.NotAuthorized(
              'You must be logged in to perform this action.')


@toolkit.side_effect_free
def user_list_gdpr(context, data_dict):
    '''
    Return user list for reset password
    '''
    print 'INNN'
    return logic.action.get.user_list(context, data_dict)


@toolkit.side_effect_free
def user_show_gdpr(context, data_dict):
    '''
    User show for reset password
    '''
    return logic.action.get.user_show(context, data_dict)
