from google.adk.agents import Agent
from google.genai import types
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp
import vertexai

# First PartyのBigQueryツール
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode


#設定
APP_NAME="bq_data_agent"
MODEL ="gemini-2.5-flash"
# エージェントの定義
INSTRUCTION = """
あなたはデータアナリティクスエージェントであり、複数のBigQeuryツールにアクセスすることができます。これらのBigQueryツールを活用して、ユーザーの質問に答えてください。
ユーザーはデータ分析について専門的な知見を持っていません。取得したデータを提示するだけでなく、そのデータに対して次にどのような分析を行うべきか、推奨されるネクストアクションをユーザーに提案してあげてください。
"""
DESCRIPTION = "ユーザーからの質問に対して、BigQueryのデータにSQLを実行して回答してください"

SAFETY_SETTINGS = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.OFF,
    )
]

GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    safety_settings=SAFETY_SETTINGS,
    temperature=0.5,
    max_output_tokens=65535,
    top_p=0.95,
)

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# ツールセットのインスタンス
bigquery_toolset = BigQueryToolset(
    tool_filter=[
        'list_dataset_ids', # データセットのリストツール
        'get_dataset_info', # データセットの情報取得
        'list_table_ids', # テーブル一覧のリスト
        'get_table_info', # テーブル情報のリスト
        'execute_sql', # SQL実行と結果取得
        'forecast', # BQMLで時系列予測
        'ask_data_insights', # テーブル内データへの質問回答
        ])


root_agent = Agent(
    name=APP_NAME,
    model=MODEL,
    description=DESCRIPTION,
    generate_content_config=GENERATE_CONTENT_CONFIG,
    instruction=INSTRUCTION,
    tools=[bigquery_toolset]
)

#Agent Engineへのデプロイ用
vertexai.init(
    project="", #プロジェクトID指定
    location="us-central1",
    staging_bucket="" #ADK情報を格納するバケットURL指定
)

app = AdkApp(
    agent=root_agent,
    enable_tracing=True
    )

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform==1.129.0",
        "google-adk==1.20.0"
    ],
    display_name="bq_data_agent", #Agent Engine上の表示名
    description="BigQuery内を探索・クエリして、あなたのデータ分析をサポートします。", #Agent Engine上の説明文
)

print(f"Deployment finished!")
print(f"Resource Name: {remote_app.resource_name}")