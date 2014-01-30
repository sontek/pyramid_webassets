import unittest
import os
from mock import Mock
from pyramid import testing
from webassets.test import TempDirHelper


class TestWebAssets(unittest.TestCase):
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

    def test_add_setting(self):
        from pyramid_webassets import add_setting

        config = Mock()
        config.registry = Mock()
        queryUtility = Mock()
        env = Mock()
        env.config = {}
        register = Mock()
        env.register = register
        queryUtility.return_value = env

        config.registry.queryUtility = queryUtility

        add_setting(config, 'foo', 'bar')
        assert env.config['foo'] == 'bar'

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
            'webassets.base_dir': os.getcwd(),
        }

        env = get_webassets_env_from_settings(settings)

        assert env.directory == settings['webassets.base_dir']
        assert env.url == settings['webassets.base_url']

    def test_get_webassets_env_from_settings_autobuild_disabled(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.auto_build': 'false'
        }

        env = get_webassets_env_from_settings(settings)

        assert env.directory == settings['webassets.base_dir']
        assert env.url == settings['webassets.base_url']
        assert env.auto_build == False

    def test_get_webassets_env_from_settings_complete(self):
        from pyramid_webassets import get_webassets_env_from_settings
        import webassets

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.debug': 'true',
            'webassets.cache': 'false',
            'webassets.updater': 'always',
            'webassets.jst_compiler': 'Handlebars.compile',
            'webassets.jst_namespace': 'window.Ember.TEMPLATES'
        }

        env = get_webassets_env_from_settings(settings)

        assert env.directory == settings['webassets.base_dir']
        assert env.url == settings['webassets.base_url']
        assert env.debug == True
        assert isinstance(env.updater, webassets.updater.AlwaysUpdater)
        assert env.config['JST_COMPILER'] == settings['webassets.jst_compiler']
        assert env.config['JST_NAMESPACE'] == settings['webassets.jst_namespace']
        assert env.cache == None
        assert env.auto_build == True

    def test_get_webassets_env_from_settings_with_cache(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.cache': 'true',
        }

        env = get_webassets_env_from_settings(settings)

        assert env.cache != None

    def test_get_webassets_env_from_settings_with_cache_directory(self):
        from pyramid_webassets import get_webassets_env_from_settings
        from uuid import uuid4
        import shutil

        tmpdir = os.path.join(os.getcwd(), 'test-cache-dir-' + str(uuid4()))

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.cache': tmpdir,
        }

        assert not os.path.isdir(tmpdir)

        env = get_webassets_env_from_settings(settings)

        assert env.cache != None
        assert env.cache == tmpdir
        assert os.path.isdir(tmpdir)

        shutil.rmtree(tmpdir)

    def test_get_webassets_env_from_settings_prefix_change(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'foo.base_url': '/static',
            'foo.base_dir': os.getcwd(),
        }

        env = get_webassets_env_from_settings(settings, prefix='foo')

        assert env != None
        assert env.directory == settings['foo.base_dir']
        assert env.url == settings['foo.base_url']

    def test_get_webassets_env_from_settings_prefix_bad_change(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'foo.base_url': '/static',
            'foo.base_dir': os.getcwd(),
        }

        with self.assertRaises(Exception) as cm:
            get_webassets_env_from_settings(settings, prefix='webassets')

        assert cm.exception.message == "You need to provide webassets.base_dir in your configuration"

    def test_includeme(self):
        from pyramid_webassets import includeme
        from pyramid_webassets import add_webasset
        from pyramid_webassets import get_webassets_env
        from pyramid_webassets import add_setting
        from pyramid_webassets import get_webassets_env_from_request

        config = Mock()
        add_directive = Mock()
        registerUtility = Mock()
        set_request_property = Mock()

        config.registry = Mock()
        config.registry.registerUtility = registerUtility
        config.add_directive = add_directive
        config.set_request_property = set_request_property

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
        }

        config.registry.settings = settings

        includeme(config)

        expected1 = ('add_webasset', add_webasset)
        expected2 = ('get_webassets_env', get_webassets_env)
        expected3 = ('add_webassets_setting', add_setting)

        assert add_directive.call_args_list[0][0] == expected1
        assert add_directive.call_args_list[1][0] == expected2
        assert add_directive.call_args_list[2][0] == expected3

        assert set_request_property.call_args_list[0][0] == \
            (get_webassets_env_from_request, 'webassets_env')

    def test_get_webassets_env_from_request(self):
        from pyramid_webassets import get_webassets_env_from_request
        from pyramid_webassets import IWebAssetsEnvironment

        request = Mock()
        request.registry = Mock()
        queryUtility = Mock()
        request.registry.queryUtility = queryUtility

        env = get_webassets_env_from_request(request)
        queryUtility.assert_called_with(IWebAssetsEnvironment)

        assert env != None

    def test_webassets_static_view_setting(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.static_view': True,
        }

        env = get_webassets_env_from_settings(settings)

        assert env != None
        assert env.config['static_view'] == settings['webassets.static_view']

    def test_webassets_static_view_cache_control_setting(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.static_view': True,
            'webassets.cache_max_age': 3600,
        }

        env = get_webassets_env_from_settings(settings)

        assert env != None
        assert env.config['static_view'] == settings['webassets.static_view']
        assert env.config['cache_max_age'] == settings['webassets.cache_max_age']

    def test_get_webassets_env_from_settings_load_path(self):
        from pyramid_webassets import get_webassets_env_from_settings

        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.load_path': '/foo bar/\nbaz'
        }

        env = get_webassets_env_from_settings(settings)

        assert env.load_path == ['/foo', 'bar/', 'baz']

    def test_auto_bool(self):
        from pyramid_webassets import get_webassets_env_from_settings
        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.less_run_in_debug': 'true',
        }
        env = get_webassets_env_from_settings(settings)
        assert env.config['less_run_in_debug'] == True

    def test_auto_json(self):
        from pyramid_webassets import get_webassets_env_from_settings
        settings = {
            'webassets.base_url': '/static',
            'webassets.base_dir': os.getcwd(),
            'webassets.less_extra_args': 'json:["--foo", "--bar"]',
        }
        env = get_webassets_env_from_settings(settings)
        assert env.config['less_extra_args'] == ['--foo', '--bar']


class TestAssetSpecs(TempDirHelper, unittest.TestCase):
    # Mask the methods from TempDirHelper, pytest will try to call them without
    # instantiating the class...
    setup = None
    teardown = None

    def setUp(self):
        from pyramid_webassets import get_webassets_env

        TempDirHelper.setup(self)

        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request, settings={
                'webassets.base_url': '/static',
                'webassets.base_dir': self.tempdir+'/static',
                'webassets.static_view': True,})
        self.config.include('pyramid_webassets')

        self.env = get_webassets_env(self.config)
        # Disable cache busting
        self.env.url_expire = False

        import sys
        sys.path.append(self.tempdir)

    def tearDown(self):
        TempDirHelper.teardown(self)
        testing.tearDown()

        import sys
        # remove tempdir path elements
        for pth in sys.path:
            if pth.startswith(self.tempdir):
                sys.path.remove(pth)

        # remove tempdir modules
        for name,module in sys.modules.items():
            if module is not None:
                if getattr(module, '__file__', '').startswith(self.tempdir):
                    del sys.modules[name]

    def test_asset_spec_passthru_uses_static_url(self):
        from webassets              import Bundle
        from pyramid.path           import AssetResolver

        self.create_files({
                'dotted/__init__.py': '',
                'dotted/package/__init__.py': '',
                'dotted/package/name/__init__.py': '',
                'dotted/package/name/static/zing.css':
                '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec)
        self.request.static_url = Mock(return_value='http://example.com/foo/')

        urls = bundle.urls(self.env)
        path = AssetResolver(None).resolve(asset_spec).abspath()
        self.request.static_url.assert_called_with(path)
        assert urls == ['http://example.com/foo/']

    def test_asset_spec_source_is_resolved(self):
        from webassets import Bundle

        self.create_files({
                'dotted/__init__.py': '',
                'dotted/package/__init__.py': '',
                'dotted/package/name/__init__.py': '',
                'dotted/package/name/static/zing.css':
                '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec, output='gen/zung.css')

        urls = bundle.urls(self.env)
        assert urls == ['http://example.com/static/gen/zung.css']
        urls[0] = urls[0][len(self.request.application_url):]
        assert file(self.tempdir+urls[0]).read() == '* { text-decoration: underline }'

    def test_asset_spec_output_is_resolved(self):
        from webassets import Bundle

        self.create_files({
            'static/__init__.py': '',
            'dotted/__init__.py': '',
            'dotted/package/__init__.py': '',
            'dotted/package/name/__init__.py': '',
            'dotted/package/name/static/zing.css':
            '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec, output='static:zung.css')

        urls = bundle.urls(self.env)
        assert urls == ['http://example.com/static/zung.css']
        urls[0] = urls[0][len(self.request.application_url):]
        assert file(self.tempdir+urls[0]).read() == '* { text-decoration: underline }'

    def test_asset_spec_missing_file(self):
        from webassets import Bundle
        from webassets.exceptions import BundleError

        self.create_files({
                'dotted/__init__.py': '',
                'dotted/package/__init__.py': '',
                'dotted/package/name/__init__.py': ''})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec)

        with self.assertRaises(BundleError) as cm:
            bundle.urls(self.env)

        fname = self.tempdir+'/dotted/package/name/static/zing.css'
        assert str(cm.exception.message) == ("'%s' does not exist" % (fname,))

    def test_asset_spec_missing_package(self):
        from webassets import Bundle
        from webassets.exceptions import BundleError

        self.create_files({
                'dotted/__init__.py': '',
                'dotted/package/__init__.py': '',
                'dotted/package/name/__init__.py': '',
                'dotted/package/name/static/zing.css':
                '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.rabbits:static/zing.css'
        bundle = Bundle(asset_spec)

        with self.assertRaises(BundleError) as cm:
            bundle.urls(self.env)

        assert cm.exception.args[0].message == 'No module named rabbits'

    def test_asset_spec_no_static_view(self):
        from webassets import Bundle

        self.create_files({
                'dotted/__init__.py': '',
                'dotted/package/__init__.py': '',
                'dotted/package/name/__init__.py': '',
                'dotted/package/name/static/zing.css':
                '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec)

        # webassets will copy the file into a place that it can generate
        # a url for
        urls = bundle.urls(self.env)
        domain = 'http://example.com/static/webassets-external/'

        assert domain in urls[0]
        assert len(urls) == 1

    def test_assec_spec_globbing(self):
        from webassets import Bundle

        self.create_files({
            'static/__init__.py': '',
            'static/zing.css':
            '* { text-decoration: underline }',
            'static/zang.css':
            '* { text-decoration: underline }'})
        asset_spec = 'static:z*ng.css'
        bundle = Bundle(asset_spec)

        urls = bundle.urls(self.env)
        assert len(urls) == 2
        assert 'http://example.com/static/zing.css' in urls
        assert 'http://example.com/static/zang.css' in urls

    def test_asset_spec_load_path_and_mapping(self):
        from webassets import Bundle

        asset_path = self.tempdir + '/dotted/package/name/static/'
        self.env.append_path(asset_path, 'http://static.example.com')

        self.create_files({
            'dotted/__init__.py': '',
            'dotted/package/__init__.py': '',
            'dotted/package/name/__init__.py': '',
            'dotted/package/name/static/zing.css':
            '* { text-decoration: underline }'})
        asset_spec = 'dotted.package.name:static/zing.css'
        bundle = Bundle(asset_spec, output=asset_spec.replace('zing', 'zung'))

        urls = bundle.urls(self.env)
        assert urls == ['http://static.example.com/zung.css']
