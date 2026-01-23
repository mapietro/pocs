import requests
import json

# --- SEUS DADOS ---
PHONE_NUMBER_ID = "875239575680979"  # Aquele ID que começa com 1 ou 2
ACCESS_TOKEN = "EAATmgrEZBe1wBQeHFDDUpmiwyyQ7njHo1BfejTt26x4kd3wm2rR6DIcRkdOtYZCkE4ZCYZB1iLMLhNH3TCR3uMhxpXKM28N7CwQqcgGMvYEpMHCBupYlbigSNu79KcyWIAwAISLrpccHDcdq63XhfnCjWLHRGZC2d1AX6WH8d5T45K53uPURVwV6O4fRRJAZDZD"
# Escolha um PIN forte de 6 dígitos (que você não esqueça!)
# Ex: Data de nascimento invertida, parte do CPF, etc.
NEW_SECURE_PIN = "458721" 

# --- A MÁGICA ---
# Para alterar o PIN, fazemos um POST na raiz do ID do telefone
url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Apenas o campo 'pin' é necessário para essa atualização
payload = {
    "messaging_product": "whatsapp",
    "pin": NEW_SECURE_PIN
}

print(f"🔒 Atualizando PIN de segurança para o ID: {PHONE_NUMBER_ID}...")

try:
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("\n✅ PIN ATUALIZADO COM SUCESSO!")
            print(f"Seu novo PIN de segurança é: {NEW_SECURE_PIN}")
            print("Guarde-o no seu cofre de senhas. A Meta vai pedir ele se você trocar de servidor.")
        else:
            print("\n⚠️ Algo estranho aconteceu:")
            print(json.dumps(data, indent=4))
    else:
        print(f"\n❌ Erro na atualização (Status {response.status_code}):")
        print(response.text)

except Exception as e:
    print(f"\n❌ Erro de execução: {str(e)}")