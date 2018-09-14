import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.routing import SubMapper
import ckanext.gdpr.action


class GdprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'gdpr')


    def get_actions(self):
        action_functions = {
            'user_list':
                ckanext.gdpr.action.user_list,
            'user_show':
                ckanext.gdpr.action.user_show,
            'user_list_gdpr':
                ckanext.gdpr.action.user_list_gdpr,
            'user_show_gdpr':
                ckanext.gdpr.action.user_show_gdpr                
            }
        return action_functions            


    def before_map(self, map):
        user_ctrl = 'ckanext.gdpr.controller:GdprUserController'        

        with SubMapper(map, controller=user_ctrl) as m:
            m.connect('user_index', '/user',
                        controller=user_ctrl, action='index')
            m.connect('/user/reset', action='request_reset')           
            m.connect('/user/activity/{id}/{offset}', action='activity')
            m.connect('user_activity_stream', '/user/activity/{id}',
                      action='activity', ckan_icon='time')
        return map        
