import token
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from dotenv import load_dotenv
import os

load_dotenv(override=True)

class DepressionModel:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME")
        self.token = os.getenv("token")
        self.save_dir = os.getenv("save_dir")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=self.token)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, token=self.token)
        self.device = os.getenv("device")
        
    def predict(self, text: str, max_len: int = 256):
        self.model.to(self.device)
        self.model.eval()
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            pred = torch.argmax(outputs.logits, dim=1).cpu().numpy()[0]

        label_map = {0: 'Minimal', 1: 'Mild', 2: 'Moderate', 3: 'Moderately Severe', 4: 'Severe'}
        return label_map[pred]