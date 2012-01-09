Configuration
====================
You are required to set base_dir and base_url, the rest are optional,
but we currently support:

``` python
webassets.base_dir=%(here)s/eventq/static
webassets.base_url=/static
webassets.debug=True
webassets.base_url=/static
webassets.updater=timestamp
webassets.cache=False
webassets.jst_compiler=Handlebars.compile
 ```

Then you can just use config.add_webasset to add bundles to your environment

``` python
    jst = Bundle('templates/*.html',
            filters='jst',
            output='js/jst.js', debug=False)

    config.add_webasset('jst', jst)
 ```

Jinja2
====================
If you are using Jinja2, you can just do the following configuration (this assumes use of pyramid_jinja2):

``` python
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    assets_env = config.get_webassets_env()
    jinja2_env.assets_environment = assets_env
 ```

Extras
====================
There are a few utility methods you can use:

get_webassets_env_from_settings(settings, prefix='webassets'): Pass it a dictionary of your settings and an
option keyword argument of the prefix in your configuration and it will return you a webassets environment.

get_webassets_env(request or config): This will pull the environment out of the registry, you can use either
a configurator object or a request.
