"""Popula o banco com um usuário de teste e alguns dados de exemplo de Rio Branco.

Uso:  python seed.py
Pode rodar mais de uma vez: só cria o que ainda não existe.
(Na nuvem não precisa: com SEED_DEMO=true a API faz isso sozinha ao subir.)
"""
from app.dados_exemplo import USUARIO, popular

if __name__ == "__main__":
    popular()
    print(f"Seed concluído. Login de teste: {USUARIO['email']} / {USUARIO['senha']}")
