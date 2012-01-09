from pyramid.settings import asbool
from zope.interface import Interface
from webassets import Environment

class IWebAssetsEnvironment(Interface):
    pass

def add_web_asset(config, name, bundle):
    asset_env = get_webassets_env(config)
    asset_env.register(name, bundle)

def get_webassets_env(config):
    return config.registry.queryUtility(IWebAssetsEnvironment)

def get_webassets_env_from_settings(settings, prefix='webassets'):
    def base_name(string):
        return '%s.%s' % (prefix, string)

    if not base_name('base_dir')  in settings:
        raise Exception("You need to provide webassets.base_dir in your configuration")
    if not base_name('base_url') in settings:
        raise Exception("You need to provide webassets.base_url in your configuration")

    asset_dir = settings.get(base_name('base_dir'))
    asset_url = settings.get(base_name('base_url'))
    kwargs = {}

    if base_name('debug') in settings:
        dbg = settings.get(base_name('debug')).lower()

        if dbg == 'false' or dbg == 'true':
            dbg = asbool(dbg)

        kwargs['debug']  = dbg

    if base_name('cache') in settings:
        kwargs['cache'] = asbool(settings.get(base_name('cache')))

    if base_name('updater') in settings:
        kwargs['updater'] = settings.get(base_name('updater'))

    if base_name('jst_compiler') in settings:
        kwargs['JST_COMPILER'] = settings.get(base_name('jst_compiler'))

    assets_env = Environment(asset_dir, asset_url, **kwargs)

    return assets_env

def includeme(config):
    assets_env = get_webassets_env_from_settings(config.registry.settings)

    config.registry.registerUtility(assets_env, IWebAssetsEnvironment)

    config.add_directive('add_webasset', add_web_asset)
    config.add_directive('get_webassets_env', get_webassets_env)
