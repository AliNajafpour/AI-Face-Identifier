from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2", tokenizer="deepset/roberta-base-squad2")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def text_analysis(text):
    entities = ner_pipeline(text)
    name = None
    for entity in entities:
        if entity["entity_group"] == "PER":  # PER = Person
            name = entity["word"]
            break

    # Extract occupation and nationality using QA
    questions = {
        "occupation": "What is the occupation of the person?",
        "nationality": "What is the nationality of the person?",
    }

    results = {"name": name}
    for key, question in questions.items():
        answer = qa_pipeline(question=question, context=text)
        results[key] = answer["answer"] if answer["score"] > 0.2 else None

    print("Name:", results["name"])
    print("Occupation:", results["occupation"])
    print("Nationality:", results["nationality"])
    return results


with open('./test_assets/texts/text4.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text_analysis(text)