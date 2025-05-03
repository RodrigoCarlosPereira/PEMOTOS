import openai

class Prompt:
    def prompt(body):  
        pergunta = str(body.pergunta) 
        
        prompt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um atendente especializado em consórcios da Pernambuco Motos."},
                {"role": "user", "content": pergunta}  
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return prompt

       