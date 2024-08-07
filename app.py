import pandas as pd
import streamlit as st
from typing import Any, List, Tuple, Union
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# グローバル変数の初期化
params = {  
    "aoai_api_key": "",  
    "aoai_api_version": "",  
    "aoai_endpoint": "",  
    "aoai_embedding_model": "",  
    "ai_search_api_key": "",  
    "ai_search_endpoint": "",  
    "index_name": "",  
    "query": "",  
    "vector_fields": "",  
    "search_mode": "",  
    "filter": "",  
    "highlight_fields": "",  
    "query_type": "",  
    "search_fields": "",  
    "select": "",  
    "top": "" 
}

def main():
    load_params_from_file()
    create_header()
    create_sidebar()
    click_button()
    create_params_table()
    create_footer()

def load_params_from_file():  
    with open("params.txt", "r") as f:  
        lines = f.readlines() 
        for line in lines:  
            key, value = line.strip().split(";")  
            params[key] = value

def create_header():
    st.set_page_config(page_title="Azure AI Search ハイブリッド検索サンプルアプリ", layout="wide")
    st.title("Azure AI Search ハイブリッド検索サンプルアプリ")
    st.write("Azure AI Search を使ったフルテキスト検索、ベクトル検索、ハイブリッド検索を比較するためのサンプルアプリです。")

def create_sidebar():
    st.sidebar.header("AOAI クライアント設定")
    params["aoai_api_key"] = st.sidebar.text_input("AOAI API キー (必須)", value=params["aoai_api_key"], help="Azure OpenAI Service を利用するための API キー")
    params["aoai_api_version"] = st.sidebar.text_input("AOAI API バージョン (必須)", value=params["aoai_api_version"], help="Azure OpenAI Service を利用するための API バージョン。2024/8 現在最新バージョンは 2024-02-01 です。")
    params["aoai_endpoint"] = st.sidebar.text_input("AOAI エンドポイント (必須)", value=params["aoai_endpoint"], help="Azure OpenAI Service を利用するためのエンドポイント。例: https://{resource-name}.openai.azure.com/")
    params["aoai_embedding_model"] = st.sidebar.text_input("AOAI 埋め込みモデルのデプロイ名 (必須)", value=params["aoai_embedding_model"], help="Azure OpenAI Service の埋め込みモデルのデプロイ名。例: text-embedding-ada-002-deploy")

    st.sidebar.header("AI Search クライアント設定")
    params["ai_search_api_key"] = st.sidebar.text_input("AI Search API キー (必須)", value=params["ai_search_api_key"], help="Azure AI Search を利用するための API キー")
    params["ai_search_endpoint"] = st.sidebar.text_input("AI Search エンドポイント (必須)", value=params["ai_search_endpoint"], help="Azure 検索サービスの URL エンドポイント。例: https://{resource-name}.search.windows.net")
    params["index_name"] = st.sidebar.text_input("インデックス名 (必須)", value=params["index_name"], help="接続するインデックスの名前。例: my-index")

    st.sidebar.header("検索設定")
    params["query"] = st.sidebar.text_input("検索クエリ (必須)", value=params["query"], help="ベクター化したり検索の実行が行われるクエリ。例: 'example search text'")
    params["vector_fields"] = st.sidebar.text_input("ベクトル検索対象フィールド", value=params["vector_fields"], help="検索されるベクトルに含める Collection(Edm.Single) 型のベクターフィールド。例: 'content'")
    params["search_mode"] = st.sidebar.radio('検索方法', ('フルテキスト検索', 'ベクトル検索', 'ハイブリッド検索'), index=0 if not params["search_mode"] else ['フルテキスト検索', 'ベクトル検索', 'ハイブリッド検索'].index(params["search_mode"]))

    st.sidebar.header("検索パラメーター")
    params["filter"] = st.sidebar.text_input("検索フィルター", value=params["filter"], help="検索クエリに適用する OData フィルター式。例: 'category eq 'electronics''")
    params["highlight_fields"] = st.sidebar.text_input("フィールドハイライト", value=params["highlight_fields"], help="ヒットハイライトに使用するフィールド名のコンマ区切りリスト。例: 'title,description'")
    params["query_type"] = st.sidebar.radio("クエリタイプ", ('simple', 'full', 'semantic'), index=0 if not params["query_type"] else ['simple', 'full', 'semantic'].index(params["query_type"]))
    params["search_fields"] = st.sidebar.text_input("フルテキスト検索フィールド", value=params["search_fields"], help="フルテキスト検索の対象となるフィールド名の一覧。例: 'title,content'")
    params["select"] = st.sidebar.text_input("取得フィールド", value=params["select"], help="取得するフィールドの一覧。指定しないと、スキーマで取得可能とマークされているすべてのフィールドが含まれます。例: 'title,description'")
    params["top"] = st.sidebar.number_input("検索の取得件数", min_value=1, value=int(params["top"]) if params["top"] else 10, help="取得する検索結果の数です。例: 10")

def create_params_table():
    st.subheader("パラメーター情報")
    st.write("以下は、Azure AI Searchで使用される各パラメーターの説明です。各パラメーターのデータ型、必要有無、および説明が含まれています。")
    data = [
        ["AOAI API キー", "str", "必須", "Azure OpenAI Service を利用するための API キー"],
        ["AOAI API バージョン", "str", "必須", "Azure OpenAI Service を利用するための API バージョン。2024/8 現在最新バージョンは 2024-02-01 です。"],
        ["AOAI エンドポイント", "str", "必須", "Azure OpenAI Service を利用するためのエンドポイント。例: https://{resource-name}.openai.azure.com/"],
        ["AOAI 埋め込みモデルのデプロイ名", "str", "必須", "zure OpenAI Service の埋め込みモデルのデプロイ名。例: text-embedding-ada-002-deploy"],
        ["AI Search API キー", "str", "必須", "Azure AI Search を利用するための API キー"],
        ["AI Search エンドポイント", "str", "必須", "Azure 検索サービスの URL エンドポイント"],
        ["インデックス名", "str", "必須", "接続するインデックスの名前"],
        ["検索クエリ", "str", "必須", "ベクター化したり検索の実行が行われるクエリ"],
        ["ベクトル検索対象フィールド", "str", "", "検索されるベクトルに含める Collection(Edm.Single) 型のベクターフィールド"],
        ["検索方法", "str", "必須", "フルテキスト検索、ベクトル検索、ハイブリッド検索の検索方法を選択"],
        ["検索フィルター", "str", "", "検索クエリに適用する OData フィルター式"],
        ["フィールドハイライト", "str", "", "ヒットハイライトに使用するフィールド名のコンマ区切りリスト"],
        ["クエリタイプ", "str", "", "検索クエリの構文を示す値。 既定値は 'simple' です。 クエリで Lucene クエリ構文が使用されている場合は、'full' を使用します。使用できる値は、'simple'、'full'、'semantic' です。"],
        ["フルテキスト検索フィールド", "list[str]", "", "フルテキスト検索の対象となるフィールド名の一覧"],
        ["取得フィールド", "list[str]", "", "取得するフィールドの一覧。指定しないと、スキーマで取得可能とマークされているすべてのフィールドが含まれます。"],
        ["検索の取得件数", "int", "", "取得する検索結果の数です"],
    ]
    df = pd.DataFrame(data, columns=["パラメーター名", "データ型", "必須", "説明"])
    st.table(df)

def create_footer():
    st.subheader("参考情報")
    st.markdown("[SearchClient クラス](https://learn.microsoft.com/ja-jp/python/api/azure-search-documents/azure.search.documents.searchclient?view=azure-python)") 
    st.markdown("[VectorizableTextQuery クラス](https://learn.microsoft.com/ja-jp/python/api/azure-search-documents/azure.search.documents.models.vectorizabletextquery?view=azure-python-preview)") 

def input_valid() -> Union[bool, None]:
    if params["aoai_api_key"] is "":
        st.error("AOAI API キーの入力は必須です。")
    elif params["aoai_api_version"] is "":
        st.error("AOAI API バージョンの入力は必須です。")
    elif params["aoai_endpoint"] is "":
        st.error("AOAI エンドポイントの入力は必須です。")
    elif params["aoai_embedding_model"] is "":
        st.error("AOAI 埋め込みモデル名の入力は必須です。")
    elif params["ai_search_api_key"] is "":
        st.error("AI Search API キーの入力は必須です。")
    elif params["ai_search_endpoint"] is "":
        st.error("AI Search エンドポイントの入力は必須です。")
    elif params["index_name"] is "":
        st.error("インデックス名の入力は必須です。")
    elif params["query"] is "":
        st.error("検索クエリの入力は必須です。")
    elif params["vector_fields"] is "" and params["search_mode"] != "フルテキスト検索":
        st.error("検索方法がフルテキスト検索ではない場合、ベクトル検索対象フィールドの入力は必須です。")
    elif params["highlight_fields"] is not "" and params["search_mode"] == "ベクトル検索":
        st.error("フィールドハイライトを利用する場合、検索方法をベクトル検索とすることはできません。")
    elif params["query_type"] is "semantic" and params["search_mode"] != "ベクトル検索":
        st.error("クエリタイプが semantic の場合、検索方法はベクトル検索である必要があります。")
    else:
        return True

def setting_clients() -> Tuple[SearchClient, AzureOpenAI]:
    credential = AzureKeyCredential(params["ai_search_api_key"])
    search_client = SearchClient(
        endpoint=params["ai_search_endpoint"],
        index_name=params["index_name"],
        credential=credential
    )
    aoai_client = AzureOpenAI(
        api_version=params["aoai_api_version"],
        azure_endpoint=params["aoai_endpoint"],
        api_key=params["aoai_api_key"]
    )
    return search_client, aoai_client

def vectorize(aoai_client: AzureOpenAI) -> Union[VectorizedQuery, None]:
    if params["search_mode"] == "フルテキスト検索":
        return None
    embedded_query = aoai_client.embeddings.create(
        input=params["query"],
        model=params["aoai_embedding_model"]
    ).data[0].embedding
    vector_query = VectorizedQuery(
        vector=embedded_query,
        fields=params["vector_fields"]
    )
    return vector_query

def search(search_client: SearchClient, vector_query: VectorizedQuery) -> List[Any]:
    results = search_client.search(
        search_text=params["query"] if params["query"] and params["search_mode"] != "ベクトル検索" else None,
        filter=params["filter"] if params["filter"] else None,
        highlight_fields=params["highlight_fields"] if params["highlight_fields"] else None,
        query_type=params["query_type"] if params["query_type"] else None,
        search_fields=[params["search_fields"]] if params["search_fields"] else None,
        select=params["select"] if params["select"] else None,
        top=params["top"] if params["top"] else None,
        vector_queries=[vector_query] if vector_query else None
    )
    return results

def show_search_result(results: List[Any]):
    st.subheader("検索結果")
    st.json([result for result in results])

def click_button():
    if st.sidebar.button("検索"):
        # 入力の検証
        if input_valid():
            # クライアントの設定
            search_client, aoai_client = setting_clients()
            # ベクトルクエリの生成
            vector_query = vectorize(aoai_client)
            # 検索
            results = search(search_client, vector_query)
            # 検索結果の表示
            show_search_result(results)
            # パラメーターの保存
            save_params_to_file()  
    
def save_params_to_file():  
    with open("params.txt", "w") as f:  
        for key, value in params.items():  
            f.write(f"{key};{value}\n") 

main()