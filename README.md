Installation
===================

Install the package:

``` bash
$ pip install pyramid_webassets
```

EITHER add it to your Pyramid `production.ini` and `development.ini`:

```
pyramid.includes =
    pyramid_debugtoolbar
    pyramid_tm
    pyramid_webassets
```

OR include it when configuring your application, usually in `__init__.py`:

``` python
def main(global_config, **settings):
    ...
    config.include('pyramid_webassets')
```

Configuration
====================
You are required to set ``base_dir`` and ``base_url``, the rest are optional,
but we currently support:

 * ``base_dir``: The directory to output and search for assets
 * ``base_url``: The url static assets will be located
 * ``debug``: If webassets should be in debug mode (i.e no compression)
 * ``updater``: Different update configurations (i.e always, timestamp)
 * ``cache``: If we should use webassets cache (if boolean), or override default path to cache directory
 * ``jst_compiler``: A custom jst compiler, by default it uses underscore
 * ``url_expire``: If a cache-busting query string should be added to URLs
 * ``static_view``: If assets should be registered as a static view using Pyramid config.add_static_view()
 * ``cache_max_age``: If static_view is true, this is passed as the static view's cache_max_age argument (allowing control of expires and cache-control headers)
 * ``paths``: A JSON dictionary of PATH=URL mappings to add paths to alternative asset locations (`URL` can be null to only add the path)
 * ``bundles``: filename or [asset-spec] (or a list of either) (http://docs.pylonsproject.org/projects/pyramid/en/latest/glossary.html#term-asset-specification) of a YAML [bundle spec](http://webassets.readthedocs.org/en/latest/loaders.html?highlight=loader#webassets.loaders.YAMLLoader) whose bundles will be auto-registered

``` ini
webassets.base_dir              = %(here)s/app/static
webassets.base_url              = static
webassets.debug                 = True
webassets.updater               = timestamp
webassets.cache                 = False
webassets.jst_compiler          = Handlebars.compile
webassets.url_expire            = False
webassets.static_view           = True
webassets.cache_max_age         = 3600
webassets.bundles               = mypackage:webassets.yaml
```

Then you can just use config.add_webasset to add bundles to your environment

``` python
from webassets import Bundle

jst = Bundle('templates/*.html',
        filters='jst',
        output='js/jst.js', debug=False)

config.add_webasset('jst', jst)
```

All other configurations are passed through to webassets, including
filter settings. These are adjusted as follows: if a value is exactly
``true`` or ``false``, then it is converted to a boolean; if a value
is prefixed with the string ``json:``, then it is JSON-parsed. This
allows pyramid-webassets to handle basic extensible filter
configurations without needing any python code, for example:

``` ini
webassets.less_run_in_debug     = true
webassets.less_extra_args       = json:["--line-numbers=mediaquery", "-O2"]
```

Use asset specs instead of files and urls
----------------------------------------------
It's possible to use an asset specifications (package:file) instead of simple file names.

- If the asset specifications declares a path outside the base_dir, the file will be copied.
- Otherwise, it will work like a normal bundle file.

If files are bundled from other packages and those packages act like pyramid
plugins adding their own ``add_static_view``, webassets will use those static
view urls to show the individual files if needed (for example, in development mode).

If you have defined your own static route and you want to use it with webassets,
for example:

``` python
config.add_static_view('static-stuff', 'my.super.app:static')
```

Setting the base url configuration option to an asset specification:

```
base_url = my.super.app:static
```

Will make webassets use the ``/static-stuff`` route for your assets. Note:
the absolute or relative path depends on where is your application is deployed.

Use with templates
========================
Included are helpers that you can use with your templates. Additional helpers
are documented below in the section labeled "Extras".

Mako
-----

You can use the global webassets tag:
``` python
% for url in webassets(request, 'css/bootstrap.css', 'css/bootstrap-responsive.css', output='css/generated.css', filters='cssmin'):
    <link href="${url}" rel="stylesheet">
% endfor
```

or you can grab the environment from the request.

Jinja2
-------
If you are using Jinja2, you can just do the following configuration (this assumes use of pyramid_jinja2):

``` python
config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
assets_env = config.get_webassets_env()
jinja2_env = config.get_jinja2_environment()
jinja2_env.assets_environment = assets_env
```
and then:

``` python
{% assets "jst" %}
<script type="text/javascript" src="{{ ASSET_URL }}"></script>
{% endassets %}
```

Generic
--------
It's always possible to access the environment from the request.

```python
jst_urls = request.webassets_env['jst'].urls()
```

Extras
====================

There are a few more utility methods you can use to make working with webassets
within your Pyramid application easier.

Configuration
---------------
These methods can be called on the `Configurator` instance during startup:

``add_webasset(name, bundle)``: Registers a bundle with webassets

``add_webassets_setting(key, value)``: Update the environment configuration

``add_webassets_path(path, url)``: Append a URL mapping to the environment

``get_webassets_env_from_settings(settings, prefix='static_assets')``: Pass a
dictionary of your settings and an optional keyword argument of the prefix in
your configuration and it will return a webassets environment.

``get_webassets_env()``: This will pull the environment out of the registry.

Request handling
------------------
These properties and helpers are attached to the `Request` object:

``request.webassets_env``: Access the webassets environment

``request.webassets(*bundle_names, **kwargs)``: Build the named bundles.
Keyword arguments will be passed to webassets to influence bundling.

Building assets from a script
=======================================
The `webassets` module includes a command line script, also called `webassets`,
which can be used to build bundles offline. When integrating with Pyramid, it
can be helpful to bootstrap the environment using paster instead, like so:

``` python
import pyramid.paster
import webassets.script

app_env = pyramid.paster.bootstrap('config.ini')
assets_env = app_env['request'].webasset_env
webassets.script.main(['build'], assets_env)
```
