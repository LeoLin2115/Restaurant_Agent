from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
import vector
import build_restaurant
import google_address

model = OllamaLLM(model = 'llama3.2', temperature=0.5)

template = '''
You are an expert in answering questions restaurants.
provide concise and accurate answers based on the provided reviews.

Here are some relevant reviews with three things restaurant name and type and comments: {reviews}

Here is the question to answer: {question}
'''

prompt = ChatPromptTemplate.from_messages(
    [HumanMessagePromptTemplate.from_template(template)]
)
chain = prompt | model

# address = input("請輸入地址: ").strip()
# radius = input("請輸入距離（公尺）: ").strip()

# # 從輸入的地址轉換成經緯度
# # address = "臺北市中正區北平西路3號" #台北車站
# # radius = 1000
# res = google_address.address_to_latlng(address)
# if res["ok"]:
#     print(f"地址: {address}")
#     print(f"解析結果: {res['formatted_address']}")
#     print(f"lat: {res['lat']}, lng: {res['lng']}")
#     lat = res['lat']
#     lng = res['lng']
# else:
#     print("找不到經緯度或發生錯誤:", res["error"])

# #將經緯度輸入到nominatim 抓取範圍內的餐廳資訊
# if lat and lng and radius:
#     build_restaurant.build_restaurant_list(lat, lng, radius)
# else:
#     print("無法建立餐廳清單，缺少經緯度或距離參數")

# 建立向量檢索器
retriever = vector.build_retriever()
# vector_store = vector.build_vector_store()
# 問答介面
# 將餐廳資訊輸入當作參考資料 詢問餐廳資訊
while True:
    print('\n\n-----------------------------------------')
    question = input('Ask your question (q to quit):  ')
    if question.lower() == 'q':
        break
    print('\n\n')

    # # 使用 similarity_search_with_score() 取得 (Document, score) 清單
    # hits = vector_store.similarity_search_with_score(question, k=10)

    # # 顯示每筆檢索結果與相似度，並把內容合併成 reviews 字串給 LLM
    # reviews_list = []
    # print("檢索結果（score 表示相似度/距離，依 Chroma 版本而定）：")
    # for doc, score in hits:
    #     # 簡短輸出：分數 + 文件摘要/前幾個字
    #     snippet = doc.page_content[:200].replace("\n", " ")
    #     print(f"  score={score:.4f}  |  snippet={snippet}")
    #     reviews_list.append(snippet)

    # reviews = "\n\n".join(reviews_list)
    reviews = retriever.invoke(question)
    # print(reviews)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)
