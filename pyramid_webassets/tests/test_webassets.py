import unittest2
from mock import Mock

class TestWebAssets(unittest2.TestCase):
    def test_asset_interface(self):
        from pyramid_webassets import IWebAssetsEnvironment

        def make_env():
            IWebAssetsEnvironment('1')

        self.assertRaises(TypeError, make_env)

    def test_add_web_asset(self):
        from pyramid_webassets import add_webasset

        config = Mock()
        config.registry = Mock()
        queryUtility = Mock()
        env = Mock()
        register = Mock()
        env.register = register
        queryUtility.return_value = env

        config.registry.queryUtility = queryUtility

        add_webasset(config, 'foo', 'bar')
        register.assert_called_with('foo', 'bar')

    def test_get_webassets_env(self):
        from pyramid_webassets import get_webassets_env
        from pyramid_webassets import IWebAssetsEnvironment

        config = Mock()
        config.registry = Mock()
        queryUtility = Mock()

        config.registry.queryUtility = queryUtility

        env = get_webassets_env(config)
        queryUtility.assert_called_with(IWebAssetsEnvironment)

        assert env != None

    def test_get_webassets_env_from_settings_no_config(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {}

        with self.assertRaises(Exception) as cm:
            get_webassets_env_from_settings(settings)

        assert cm.exception.message == "You need to provide webassets.base_dir in your configuration"

    def test_get_webassets_env_from_settings_no_base_dir(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {'webassets.base_url': '/static'}

        with self.assertRaises(Exception) as cm:
            get_webassets_env_from_settings(settings)

        assert cm.exception.message == "You need to provide webassets.base_dir in your configuration"

    def test_get_webassets_env_from_settings_no_base_url(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {'webassets.base_dir': '/home'}

        with self.assertRaises(Exception) as cm:
            get_webassets_env_from_settings(settings)

        assert cm.exception.message == "You need to provide webassets.base_url in your configuration"

    def test_get_webassets_env_from_settings_minimal(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': '/home/sontek'
        }

        env = get_webassets_env_from_settings(settings)

        assert env.directory == settings['webassets.base_dir']
        assert env.url == settings['webassets.base_url']

    def test_get_webassets_env_from_settings_complete(self):
        from pyramid_webassets import get_webassets_env_from_settings
        import webassets

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': '/home/sontek',
            'webassets.debug': 'true',
            'webassets.cache': 'false',
            'webassets.updater': 'always',
            'webassets.jst_compiler': 'Handlebars.compile'
        }

        env = get_webassets_env_from_settings(settings)

        assert env.directory == settings['webassets.base_dir']
        assert env.url == settings['webassets.base_url']
        assert env.debug == True
        assert isinstance(env.updater, webassets.updater.AlwaysUpdater)
        assert env.config['JST_COMPILER'] == settings['webassets.jst_compiler']
        assert env.cache == None

    def test_get_webassets_env_from_settings_with_cache(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': '/home/sontek',
            'webassets.cache': 'true',
        }

        env = get_webassets_env_from_settings(settings)

        assert env.cache != None

    def test_get_webassets_env_from_settings_prefix_change(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'foo.base_url': '/static',
            'foo.base_dir': '/home/sontek',
        }

        env = get_webassets_env_from_settings(settings, prefix='foo')

        assert env != None
        assert env.directory == settings['foo.base_dir']
        assert env.url == settings['foo.base_url']

    def test_get_webassets_env_from_settings_prefix_bad_change(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'foo.base_url': '/static',
            'foo.base_dir': '/home/sontek',
        }

        with self.assertRaises(Exception) as cm:
            get_webassets_env_from_settings(settings, prefix='webassets')

        assert cm.exception.message == "You need to provide webassets.base_dir in your configuration"

    def test_includeme(self):
        from pyramid_webassets import includeme
        from pyramid_webassets import add_webasset
        from pyramid_webassets import get_webassets_env

        config = Mock()
        add_directive = Mock()
        registerUtility = Mock()

        config.registry = Mock()
        config.registry.registerUtility = registerUtility
        config.add_directive = add_directive

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': '/home/sontek',
        }

        config.registry.settings = settings

        includeme(config)

        expected1 = ('add_webasset', add_webasset)
        expected2 = ('get_webassets_env', get_webassets_env)
        assert add_directive.call_args_list[0][0] == expected1
        assert add_directive.call_args_list[1][0] == expected2
