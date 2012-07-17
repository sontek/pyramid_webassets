from pyramid.path           import AssetResolver
from pyramid.settings       import asbool
from pyramid.threadlocal    import get_current_request
from zope.interface         import Interface
from webassets              import Bundle
from webassets.env          import Environment
from webassets.exceptions   import BundleError


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
        query = None
        request = get_current_request()

        if self.url_expire != False and '?' in fragment:
          fragment, query = fragment.rsplit('?', 1)

        if not ':' in fragment:
          # Get the path to the file if it's not an asset spec
          fragment = super(Environment, self).abspath(fragment)

        try:
            fragment = request.static_url(fragment)
            return query and "%s?%s" % (fragment, query) or fragment
        except ValueError, e:
             raise BundleError(e)


class IWebAssetsEnvironment(Interface):
    pass


def add_webasset(config, name, bundle):
    asset_env = get_webassets_env(config)
    asset_env.register(name, bundle)


def get_webassets_env(config):
    return config.registry.queryUtility(IWebAssetsEnvironment)


def get_webassets_env_from_settings(settings, prefix='webassets'):
    """This function will take all webassets.* parameters, and
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

    if 'manifest' in kwargs:
        kwargs['manifest'] = asbool(kwargs.pop('manifest'))

    assets_env = Environment(asset_dir, asset_url, **kwargs)

    return assets_env


def get_webassets_env_from_request(request):
    """ Get the webassets environment in the registry from the request. """
    return request.registry.queryUtility(IWebAssetsEnvironment)


def assets(request, *args, **kwargs):
    env = get_webassets_env_from_request(request)

    result = []

    for f in args:
        try:
            result.append(env[f])
        except KeyError:
            result.append(f)

    bundle = Bundle(*result, **kwargs)
    urls = bundle.urls(env=env)

    return urls

def add_assets_global(event):
    event['webassets'] = assets


def includeme(config):
    config.add_subscriber(add_assets_global, 'pyramid.events.BeforeRender')

    assets_env = get_webassets_env_from_settings(config.registry.settings)

    config.registry.registerUtility(assets_env, IWebAssetsEnvironment)

    config.add_directive('add_webasset', add_webasset)
    config.add_directive('get_webassets_env', get_webassets_env)
    config.add_static_view(assets_env.url, assets_env.directory)
    config.set_request_property(get_webassets_env_from_request,
        'webassets_env', reify=True)
    config.set_request_property(assets, 'webassets', reify=True)
