from transformers import pipeline

# بارگذاری مدل QA
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2", tokenizer="deepset/roberta-base-squad2")

def extract_info_qa(text):
    questions = {
        "name": "What is the name of the person?",
        "occupation": "What is the occupation of the person?",
        "nationality": "What is the nationality of the person?",
    }

    results = {}
    for key, question in questions.items():
        answer = qa_pipeline(question=question, context=text)
        if answer['score'] > 0.2:  # فیلتر پاسخ‌های ضعیف
            results[key] = answer['answer']
        else:
            results[key] = None

    return results

with open('./results/data.txt', 'r') as f:
    text = f.read()

info = extract_info_qa(text)
print("Name:", info["name"])
print("Occupation:", info["occupation"])
print("Nationality:", info["nationality"])