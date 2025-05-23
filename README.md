# qgis-csmap-plugin

<img src='./imgs/icon.png' alt="CSMap Plugin Icon" width="10%"><br>

- DEM を GeoTIFF 形式の CS 立体図に変換する QGIS プラグインです。<br>
- DEM の変換処理は[ csmap-py ](https://github.com/MIERUNE/csmap-py)を利用しているため，最新の QGIS LTR（Windows / macOS）で動作します。<br>

## インストール

- 本プラグインは[ QGIS Python Plugin Repository ](https://plugins.qgis.org/plugins/csmap-qgis-plugin)で公開されています。
- QGIS の［プラグイン > プラグインの管理とインストール...］にて `CSMap Plugin` と検索してインストール可能です。

### Windows をお使いの方へ

- Windows 版の QGIS では、プラグインの読み込みエラーが発生する場合があります。<br>
- [ csmap-py ](https://github.com/MIERUNE/csmap-py)による DEM の変換処理は rasterio と numpy により実行されているので，Windows 版の QGIS では rasterio を手動でインストールする必要があります。以下の手順でインストールしてください。<br>

rasterio インストール手順：

- Python コンソールを起動します。
- `!pip install rasterio` を実行します。赤文字で `WARNING` が表示されても，最下行に `Successfully installed ~` と表示されれば問題ありません。
- QGIS を再起動して，もう一度 Python コンソールを起動します。
- `import rasterio` を実行すると，本プラグインのアイコンが表示されます。

## 使用方法

- ツールバーのプラグインアイコンをクリックするか、プロセシングツールボックスを開いて［CSMap Plugin > CS 立体図を作成（CS 3D-Map）］をクリックするとプラグインを起動することができます。
- 入力レイヤ（DEM）：DEM（GDAL でサポートされている形式）を選択します。
- 必要に応じて、パラメータを設定します。
- 出力レイヤ：［一時ファイルに保存］もしくは［ファイルに保存］を選択します。
- 設定が完了したら、［実行］ボタンをクリックして変換を開始します。

<img src='./imgs/usage.png' alt="Usage Example of CSMap Plugin" width="70%">

## Development

1. install `uv`

   https://docs.astral.sh/uv

2. install dependencies with uv

   ```sh
   # macOS
   uv venv --python /Applications/QGIS.app/Contents/MacOS/bin/python3 --system-site-packages

   # Windows（適切なバージョンのQGISのディレクトリを参照すること）
   uv venv --python C:\Program Files\QGIS 3.28.2\apps\Python39\python.exe --system-site-packages
   ```

3. （when VS Code）select the virtual environment as the Python interpreter in VS Code

   1. Open the Command Palette［ `Cmd + Shift + P` on macOS, `Ctrl + Shift + P` on Windows ］

   2. Find and Select `Python: Select Interpreter`

   3. From the list of available interpreters that appears, choose the virtual environment you created earlier, such as `/.venv/bin/python` （It is usually listed near the top and may be marked as "Recommended"）

## Authors

- Keita Uemori([@Geo-Jagaimo](https://github.com/Geo-Jagaimo))
- Shota Yamamoto([@geogra-geogra](https://github.com/geogra-geogra))
