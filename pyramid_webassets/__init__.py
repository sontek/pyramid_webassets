from pyramid.path import AssetResolver
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_request
from zope.interface import Interface
from webassets import Environment
from webassets.exceptions import BundleError


class Environment(Environment):
    def _normalize_source_path(self, spath):
        # spath might be an asset spec
        try:
            spath = AssetResolver(None).resolve(spath).abspath()
        except ImportError, e:
            raise BundleError(e)
        except ValueError:
            pass # Not an absolute asset spec

        return super(Environment, self)._normalize_source_path(spath)

    def absurl(self, fragment):
        if ':' in fragment:
            request = get_current_request()
            try:
                return request.static_url(fragment)
            except ValueError, e:
                raise BundleError(e)

        return super(Environment, self).absurl(fragment)


class IWebAssetsEnvironment(Interface):
    pass


def add_webasset(config, name, bundle):
    asset_env = get_webassets_env(config)
    asset_env.register(name, bundle)


def get_webassets_env(config):
    return config.registry.queryUtility(IWebAssetsEnvironment)


def get_webassets_env_from_settings(settings, prefix='webassets'):
    """This function will take all webassets.* parameteres, and
    call the ``Environment()`` constructor with kwargs passed in.

    The only two parameters that are not passed as keywords are:

    * base_dir
    * base_url

    which are passed in positionally.

    Read the ``WebAssets`` docs for ``Environment`` for more details.
    """
    # Make a dictionary of the webassets.* elements...
    kwargs = {}   # assets settings
    cut_prefix = len(prefix) + 1
    for k in settings:
        if k.startswith(prefix):
            kwargs[k[cut_prefix:]] = settings[k]

    if 'base_dir' not in kwargs:
        raise Exception("You need to provide webassets.base_dir in your configuration")
    if 'base_url' not in kwargs:
        raise Exception("You need to provide webassets.base_url in your configuration")

    asset_dir = kwargs.pop('base_dir')
    asset_url = kwargs.pop('base_url')

    if 'debug' in kwargs:
        dbg = kwargs['debug'].lower()

        if dbg == 'false' or dbg == 'true':
            dbg = asbool(dbg)

        kwargs['debug'] = dbg

    if 'cache' in kwargs:
        kwargs['cache'] = asbool(kwargs['cache'])

    # 'updater' is just passed in...

    if 'jst_compiler' in kwargs:
        kwargs['JST_COMPILER'] = kwargs.pop('jst_compiler')

    assets_env = Environment(asset_dir, asset_url, **kwargs)

    return assets_env


def includeme(config):
    assets_env = get_webassets_env_from_settings(config.registry.settings)

    config.registry.registerUtility(assets_env, IWebAssetsEnvironment)

    config.add_directive('add_webasset', add_webasset)
    config.add_directive('get_webassets_env', get_webassets_env)
    config.add_static_view(assets_env.url, assets_env.directory)

