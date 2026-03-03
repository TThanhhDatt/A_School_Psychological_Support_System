from app.core.predict_function import DepressionModel

class Services:
    def __init__(self):
        self.model = DepressionModel()
        
    def get_welcome_message(self):
        return {"message": "Hello, World!"}

    def get_model_predict(self, text):
        response = self.model.predict(text=text)
        return response