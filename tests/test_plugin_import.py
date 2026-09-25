"""プラグインのエントリポイントを import できることのスモークテスト。

plugin.py は Processing プロバイダ経由で csmap-py (submodule) まで連鎖的に
import するので、submodule の未取得や Python バージョン非互換による
QGIS 起動時の ImportError（classFactory 失敗）をこれ一つで検出できる。
"""


class TestPluginImport:
    def test_plugin_module_imports(self, qgis_app, qgis_plugin_path):
        from plugin_dir.plugin import CSMapPlugin

        assert CSMapPlugin is not None
