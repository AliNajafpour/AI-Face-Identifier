from transformers import pipeline

english_qa = pipeline("question-answering", model="deepset/roberta-base-squad2", tokenizer="deepset/roberta-base-squad2")
persian_qa =  pipeline("question-answering", model="pedramyazdipoor/persian_xlm_roberta_large")

english_ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
persian_ner = pipeline('ner', model='HooshvareLab/bert-base-parsbert-ner-uncased', grouped_entities=True)

def per_text_analysis(text):
    entities = persian_ner(text)
    names = []
    name = None
    for entity in entities:
        if entity["entity_group"] == "person":  
            names.append(entity['word'])

    name = max(set(names), key=names.count)

    # Extract occupation and nationality using QA
    questions = {
        "occupation": f"شغل {name} چیست؟",
        "nationality": f"ملیت {name} چیست؟",
    }

    results = {"name": name}
    for key, question in questions.items():
        answer = persian_qa(question=question, context=text)
        results[key] = answer["answer"] if answer["score"] > 0.2 else None

    print("Name:", results["name"])
    print("Occupation:", results["occupation"])
    print("Nationality:", results["nationality"])
    return results


def eng_text_analysis(text):
    entities = english_ner(text)
    names = []
    name = None
    for entity in entities:
        if entity["entity_group"] == "PER":  
            names.append(entity['word'])

    name = max(set(names), key=names.count)

    # Extract occupation and nationality using QA
    questions = {
        "occupation": f"What is the occupation of {name}?",
        "nationality": f"What is the nationality of {name}?",
    }

    results = {"name": name}
    for key, question in questions.items():
        answer = english_qa(question=question, context=text)
        results[key] = answer["answer"] if answer["score"] > 0.2 else None

    print("Name:", results["name"])
    print("Occupation:", results["occupation"])
    print("Nationality:", results["nationality"])
    return results


with open('./test_assets/texts/text4.txt', 'r', encoding='utf-8') as f:
    text = f.read()

eng_text_analysis(text)

text = ''' سروش بهروزی فر معلم المپیاد بسیاری از دانش اموزان بوده اگه دانش‌آموز دوره اولی هستی و عاشق ریاضی این پکیج برای توئه؛ این پکیج برا
ی توئیه که باهوشی و میخوای ذهن خودت رو تمرین بدی و زودتر از بقیه المپیاد ریاضی رو استارت بزنی؛ شایدم نخوای بری المپیاد ریاضی ولی عاشق ریاضی 
و میخوای ذهنت رو پرورش بدی که مثل ساعت کار کنه؛ در هر صورت این پکیح برای خودته! این پکیج شامل جلسات حل سوال هوش و ریاضیه که واقعا نیازی به دانش ریاض
ی ندارن و قراره بیشتر ذهنت و خلاقیتت رو پرورش بده؛ قراره با استاد بهروزی‌فر و رجبی توی این پکیج کلی سوال هوش و ریاضی حل کنید و خودتو آماده مسیر المپیاد کنی با سروش بهرو
زی فر که خودش مدال نقره ی المپیاد ریاضی داره و چندین سال هست که داره مدال آوران کشوری و جهانی المپیاد ریاضی رو
آموزش میده و خودش از طراحان سوال المپیاد ریاضی هست، راجع به مسیر المپیاد ریاضی و کار‌هایی که ما تو کلاس‌های المپیاد ریاضی باشگاه المپیاد طلایی‌ها می‌کنیم صحبت کردیم.. برای کسایی که خودخوان میخوان بخونن دیدن این ویدیو واجبه!ه'''

per_text_analysis(text)

#output: 
# Name: Trump
# Occupation: None
# Nationality: None
# Name: سروش بهرو زی فر
# Occupation:  معلم المپیاد
# Nationality: None
# {'name': 'سروش بهرو زی فر', 'occupation': ' معلم المپیاد', 'nationality': None}
