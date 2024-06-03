# qgis-plugin-template

QGIS3.x プラグイン開発のひな形

## Preparation

### Windows

- Windowsを利用する場合は、pyproject.tomlを開き、[packages]内のコメントアウトを削除し、プロジェクトに適したバージョンのQGIS内のPythonを参照してください。

```
packages = [
  { include = "qgis", from = "C:\\Program Files\\QGIS 3.28.2\\apps\\qgis\\python" },
]
```

1. install `Poetry`

    ```sh
    pip install poetry
    ```

2. install dependencies with Poetry

    ```sh
    # QGIS内のPython実行ファイルを参照する（開発ターゲットのバージョンのQGIS）
    # macOS, bash
    poetry env use /Applications/QGIS.app/Contents/MacOS/bin/python3
    # Windows, Powershell
    poetry env use "C:\Program Files\QGIS 3.28.2\apps\Python39\python.exe"

    poetry install
    ```

    仮想環境がカレントディレクトリに作成されます。

3. (when VSCode) 仮想環境をVSCode上のPythonインタプリタとして選択

    VSCodeはカレントディレクトリの仮想環境を検出しますが、手動で選択する必要がある場合もあります。  

    1. [Cmd + Shift + P]でコマンドパレットを開く
    2. [Python: Select Interpreter]を見つけてクリック
    3. 利用可能なインタプリタ一覧が表示されるので、先ほど作成した仮想環境を選択（通常、リストの一番上に"Recommended"として表示される）
