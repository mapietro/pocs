import requests
import json

# --- CONFIGURAÇÕES ---
# Substitua pelos seus dados reais
PHONE_NUMBER_ID = "875239575680979"  # Aquele ID que começa com 1 ou 2
ACCESS_TOKEN = "EAATmgrEZBe1wBQeHFDDUpmiwyyQ7njHo1BfejTt26x4kd3wm2rR6DIcRkdOtYZCkE4ZCYZB1iLMLhNH3TCR3uMhxpXKM28N7CwQqcgGMvYEpMHCBupYlbigSNu79KcyWIAwAISLrpccHDcdq63XhfnCjWLHRGZC2d1AX6WH8d5T45K53uPURVwV6O4fRRJAZDZD"   # Aquele token do Usuário do Sistema

# Seu número pessoal para receber o teste (com 55 e DDD)
RECIPIENT_NUMBER = "5511990257244" 

url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Payload obrigatório para início de conversa (Template)
payload = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_NUMBER,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
}

print(f"🚀 Enviando Hello World do número oficial {PHONE_NUMBER_ID}...")

try:
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print("Resposta:")
    print(json.dumps(response.json(), indent=4))

except Exception as e:
    print(f"Erro: {e}")