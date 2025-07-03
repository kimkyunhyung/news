# ... existing code in 테스트.txt ...

import torch
from transformers import LLaMAForConditionalGeneration, LLaMALogger

# Load pre-trained model and tokenizer
model_name = "facebook/llama-8b"
model = LLaMAForConditionalGeneration.from_pretrained(model_name)
tokenizer = LLaMATokenizer.from_pretrained(model_name)

def get_associations(keywords, sentence):
    # Preprocess input text
    inputs = tokenizer(sentence, return_tensors="pt")

    # Compute associations using the model
    outputs = model(**inputs, attention_mask=torch.ones_like(inputs["input_ids"]))

    # Get associations as a list of tuples (keyword, score)
    associations = []
    for keyword in keywords:
        association_score = torch.cosine_similarity(model.get_input_embeddings()(tokenizer(keyword).unsqueeze(0))[0], 
                                                     outputs.last_hidden_state[0]).item()
        associations.append((keyword, association_score))

    return associations

keywords = ["AI", "Machine Learning"]
sentence = "This is a sample sentence."
associations = get_associations(keywords, sentence)
print(associations)

# ... existing code in 테스트.txt ...