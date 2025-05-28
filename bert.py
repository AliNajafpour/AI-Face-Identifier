from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

model_name = "dslim/bert-base-NER"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

def extract_ner_bert(text):
    entities = ner_pipeline(text)
    people = [e["word"] for e in entities if e["entity_group"] == "PER"]
    locations = [e["word"] for e in entities if e["entity_group"] == "LOC"]
    organizations = [e["word"] for e in entities if e["entity_group"] == "ORG"]
    nationalities = [e["word"] for e in entities if e["entity_group"] == "MISC"]

    return {
        "names": list(set(people)),
        "locations": list(set(locations)),
        "organizations": list(set(organizations)),
        "nationalities": list(set(nationalities))
    }

with open('./results/data.txt', 'r') as f:
    text = f.read()

result = extract_ner_bert(text)
print("Names:", result["names"])
print("Locations:", result["locations"])
print("Organizations:", result["organizations"])
print("Nationalities:", result["nationalities"])