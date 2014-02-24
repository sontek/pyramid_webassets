from os import path, makedirs
import json
import six

from pyramid.path           import AssetResolver
from pyramid.settings       import asbool, truthy
from pyramid.threadlocal    import get_current_request
from zope.interface         import Interface
from webassets              import Bundle
from webassets.env          import Environment
from webassets.env          import Resolver
from webassets.exceptions   import BundleError

falsy = frozenset(('f', 'false', 'n', 'no', 'off', '0'))
booly = frozenset(list(truthy) + list(falsy))
auto_booly = frozenset(('true', 'false'))

def maybebool(value):
    '''
    If `value` is a string type, attempts to convert it to a boolean
    if it looks like it might be one, otherwise returns the value
    unchanged. The difference between this and
    :func:`pyramid.settings.asbool` is how non-bools are handled: this
    returns the original value, whereas `asbool` returns False.
    '''
    if isinstance(value, six.string_types) and value.lower() in booly:
        return asbool(value)
    return value

class PyramidResolver(Resolver):
    def __init__(self, env):
        super(PyramidResolver, self).__init__(env)
        self.resolver = AssetResolver(None)

    def _split_asset_spec(self, item):
        if ':' in item:
            package, filepath = item.split(':', 1)
            try:
                package = self.resolver.resolve('%s:' % package).abspath()
            except ImportError as e:
                raise BundleError(e)
            return (package, filepath)
        else:
            return (None, item)

    def search_for_source(self, item):
        package, filepath = self._split_asset_spec(item)
        if package is None:
            return super(PyramidResolver, self).search_for_source(filepath)
        else:
            return self.consider_single_directory(package, filepath)

    def resolve_source_to_url(self, filepath, item):
        request = get_current_request()

        if request is not None:
            try:
                return request.static_url(filepath)
            except ValueError:
                pass
        return super(PyramidResolver, self).resolve_source_to_url(
            filepath,
            item
        )

    def resolve_output_to_path(self, target, bundle):
        package, filepath = self._split_asset_spec(target)
        if package is not None:
            target = path.join(package, filepath)
        return super(PyramidResolver, self).resolve_output_to_path(
            target,
            bundle
        )

    def resolve_output_to_url(self, item):
        request = get_current_request()

        package, filepath = self._split_asset_spec(item)
        if package is not None:
            item = path.join(package, filepath)
        else:
            if not path.isabs(filepath):
                item = path.join(self.env.directory, filepath)

        if request is not None:
            try:
                url = request.static_url(item)
                return url
            except ValueError:
                pass

        return super(PyramidResolver, self).resolve_output_to_url(item)

class Environment(Environment):
    resolver_class = PyramidResolver

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
            val = settings[k]
            if isinstance(val, six.string_types):
                if val.lower() in auto_booly:
                    val = asbool(val)
                elif val.lower().startswith('json:') and k[cut_prefix:] != 'manifest':
                    val = json.loads(val[5:])
            kwargs[k[cut_prefix:]] = val

    if 'base_dir' not in kwargs:
        raise Exception("You need to provide webassets.base_dir in your configuration")
    if 'base_url' not in kwargs:
        raise Exception("You need to provide webassets.base_url in your configuration")

    asset_dir = kwargs.pop('base_dir')
    asset_url = kwargs.pop('base_url')

    if 'debug' in kwargs:
        kwargs['debug'] = maybebool(kwargs['debug'])

    if 'cache' in kwargs:
        cache = kwargs['cache'] = maybebool(kwargs['cache'])

        if cache and isinstance(cache, six.string_types) and not path.isdir(cache):
            makedirs(cache)

    # 'updater' is just passed in...

    if 'auto_build' in kwargs:
        kwargs['auto_build'] = maybebool(kwargs['auto_build'])

    if 'jst_compiler' in kwargs:
        kwargs['JST_COMPILER'] = kwargs.pop('jst_compiler')

    if 'jst_namespace' in kwargs:
        kwargs['JST_NAMESPACE'] = kwargs.pop('jst_namespace')

    if 'manifest' in kwargs:
        kwargs['manifest'] = maybebool(kwargs['manifest'])

    if 'url_expire' in kwargs:
        kwargs['url_expire'] = maybebool(kwargs['url_expire'])

    if 'static_view' in kwargs:
        kwargs['static_view'] = asbool(kwargs['static_view'])
    else:
        kwargs['static_view'] = False

    if 'cache_max_age' in kwargs:
        kwargs['cache_max_age'] = int(kwargs.pop('cache_max_age'))
    else:
        kwargs['cache_max_age'] = None

    if 'load_path' in kwargs:
        # force load_path to be an array and split on whitespace
        if not isinstance(kwargs['load_path'], list):
            kwargs['load_path'] = kwargs['load_path'].split()

    assets_env = Environment(asset_dir, asset_url, **kwargs)

    return assets_env


def get_webassets_env_from_request(request):
    """ Get the webassets environment in the registry from the request. """
    return request.registry.queryUtility(IWebAssetsEnvironment)

def add_setting(config, key, value):
    env = config.registry.queryUtility(IWebAssetsEnvironment)
    env.config[key] = value

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
    config.add_directive('add_webassets_setting', add_setting)

    if assets_env.config['static_view']:
        config.add_static_view(
            assets_env.url,
            assets_env.directory,
            cache_max_age=assets_env.config['cache_max_age']
        )

    config.set_request_property(get_webassets_env_from_request,
        'webassets_env', reify=True)
    config.set_request_property(assets, 'webassets', reify=True)
