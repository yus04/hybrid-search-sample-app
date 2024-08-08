# hybrid-search-sample-app
本リポジトリのソースコードは、Azure AI Search を使ったフルテキスト検索、ベクトル検索、ハイブリッド検索が可能な検索サンプルアプリ用のものです。本サンプルアプリを起動することで、以下のスクリーンショットのような画面でパラメーターを調整しながら検索を試すことが可能です。
![screen](assets/screen.png)

## 前提条件
- Azure AI Search がデプロイされていること
- ベクトルフィールドを持つインデックスが作成されていること
- Azure OpenAI Service がデプロイされていること
- 埋め込みモデルがデプロイされていること
- Python のプログラムの実行に必要な各ライブラリのインストールが可能であること

## 利用手順
以下のコマンドを実行するか、ZIP ダウンロードをすることでソースコードを取得する。
```
git clone https://github.com/yus04/hybrid-search-sample-app.git
```

以下のコマンドを実行し、プログラムの実行に必要なライブラリをインストールする。

```
pip install -r requirements.txt
```

以下のコマンドを実行し、Streamlit アプリケーションサーバーを起動する。
```
streamlit run app.py
```
サーバーが起動したら http://localhost:8501 にアクセスする。

## params.txt の形式について
AOAI クライアント設定、AI Search クライアント設定、検索設定に関するパラメーター情報を params.txt に保存しています。params.txt は以下の形式で保存されており、セミコロンの後に登録している各パラメーター値が保存されます。
```
aoai_api_key;
aoai_api_version;
aoai_endpoint;
aoai_embedding_model;
ai_search_api_key;
ai_search_endpoint;
index_name;
query;
vector_fields;
search_mode;
filter;
highlight_fields;
query_type;
search_fields;
select;
top;
```

## Azure App Service へのデプロイ
本アプリケーションは、以下の構成の App Service で起動することを確認しています。
- スタック：Python
- バージョン：3.12
- スタートアップコマンド：以下に記述 (※)
```
streamlit run app.py --server.port 8000
```
(※) スタートアップコマンドは Azure ポータルの App Service の画面において、「設定」>「構成」>「スタートアップコマンド」から設定可能です。設定後は変更を反映させるため、念のため App Service を再起動させることを推奨。

## 参考文献
- [Vector search in Python (Azure AI Search)](
https://github.com/Azure/azure-search-vector-samples/blob/main/demo-python/code/basic-vector-workflow/azure-search-vector-python-sample.ipynb)
- [SearchClient クラス](
https://learn.microsoft.com/ja-jp/python/api/azure-search-documents/azure.search.documents.searchclient?view=azure-python)
- [VectorizedQuery クラス](
https://learn.microsoft.com/ja-jp/python/api/azure-search-documents/azure.search.documents.models.vectorizedquery?view=azure-python)