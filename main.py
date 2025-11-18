from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from vector import retriever
import build_restaurant
import google_address

model = OllamaLLM(model = 'llama3.2')

template = '''
You are an expert in answering questions restaurants.

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
'''

prompt = ChatPromptTemplate.from_messages(
    [HumanMessagePromptTemplate.from_template(template)]
)
chain = prompt | model

address = input("請輸入地址: ").strip()
radius = input("請輸入距離（公尺）: ").strip()

# address = "台中市南屯區黎明東街260號"
# radius = 1000
res = google_address.address_to_latlng(address)
if res["ok"]:
    print(f"地址: {address}")
    print(f"解析結果: {res['formatted_address']}")
    print(f"lat: {res['lat']}, lng: {res['lng']}")
    lat = res['lat']
    lng = res['lng']
else:
    print("找不到經緯度或發生錯誤:", res["error"])

if lat and lng and radius:
    build_restaurant.build_restaurant_list(lat, lng, radius)
else:
    print("無法建立餐廳清單，缺少經緯度或距離參數")

while True:
    print('\n\n-----------------------------------------')
    question = input('Ask your question (q to quit):  ')
    if question.lower() == 'q':
        break
    print('\n\n')

    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)
