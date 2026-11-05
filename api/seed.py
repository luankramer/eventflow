"""Popula o banco com um usuário de teste e alguns dados de exemplo de Rio Branco.

Uso:  python seed.py
Pode rodar mais de uma vez: só cria o que ainda não existe.
"""
from datetime import date, time, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Categoria, Evento, Local, Usuario
from app.security import gerar_hash

USUARIO = {"nome": "Usuário Teste", "email": "teste@eventflow.com", "senha": "123456"}

# nome, cor, ícone (o app mostra cada tipo de evento com essa cor e esse ícone)
CATEGORIAS = [
    ("Música", "#E8175D", "musica"),
    ("Gastronomia", "#FFB800", "gastronomia"),
    ("Esporte", "#12B5A5", "esporte"),
    ("Cultura", "#6B2FA8", "arte"),
    ("Tecnologia", "#2F6BFF", "tecnologia"),
]

LOCAIS = [
    ("Parque da Maternidade", -9.9747, -67.8076, "Av. Getúlio Vargas, Rio Branco - AC"),
    ("Gameleira", -9.9696, -67.8094, "Calçadão da Gameleira, Segundo Distrito, Rio Branco - AC"),
    ("Arena da Floresta", -9.9890, -67.8394, "Rio Branco - AC"),
    ("UniNorte", -9.9739, -67.8167, "Rio Branco - AC"),
]

EVENTOS = [
    ("Festival de Música na Praça", "Shows de bandas locais ao ar livre.", 10, time(19, 0), "0", "Música", "Gameleira"),
    ("Feira Gastronômica Acreana", "Comidas típicas e produtores da região.", 17, time(17, 30), "15", "Gastronomia", "Parque da Maternidade"),
    ("Corrida Noturna 5K", "Corrida aberta com kit e medalha.", 24, time(20, 0), "60", "Esporte", "Parque da Maternidade"),
    ("Semana de Tecnologia", "Palestras e minicursos de desenvolvimento.", 31, time(8, 0), "25.5", "Tecnologia", "UniNorte"),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        usuario = db.scalar(select(Usuario).where(Usuario.email == USUARIO["email"]))
        if usuario is None:
            usuario = Usuario(nome=USUARIO["nome"], email=USUARIO["email"], senha_hash=gerar_hash(USUARIO["senha"]))
            db.add(usuario)

        categorias = {c.nome: c for c in db.scalars(select(Categoria))}
        for nome, cor, icone in CATEGORIAS:
            if nome not in categorias:
                categorias[nome] = Categoria(nome=nome, cor=cor, icone=icone)
                db.add(categorias[nome])
            elif not categorias[nome].cor:
                categorias[nome].cor, categorias[nome].icone = cor, icone

        locais = {l.nome: l for l in db.scalars(select(Local))}
        for nome, lat, lng, endereco in LOCAIS:
            if nome not in locais:
                locais[nome] = Local(nome=nome, latitude=lat, longitude=lng, endereco=endereco)
                db.add(locais[nome])
        db.flush()

        existentes = set(db.scalars(select(Evento.nome)))
        hoje = date.today()
        for nome, desc, dias, hora, preco, cat, loc in EVENTOS:
            if nome in existentes:
                continue
            db.add(Evento(
                nome=nome, descricao=desc, data=hoje + timedelta(days=dias), hora=hora,
                preco=Decimal(preco), categoria=categorias[cat], local=locais[loc],
                criado_por_id=usuario.id,
            ))
        db.commit()
    print(f"Seed concluído. Login de teste: {USUARIO['email']} / {USUARIO['senha']}")


if __name__ == "__main__":
    main()
