# EventFlow — App

App Android feito com **Vue 3 + Vite**, **Ionic** (componentes de interface) e **Capacitor** (empacota como app nativo e dá acesso a câmera, galeria e GPS).

## Rodar no navegador (desenvolvimento)

```bash
npm install
cp .env.example .env      # ajuste VITE_API_URL para a sua API
npm run dev
```

Abra no navegador e use as ferramentas de desenvolvedor no modo celular.
No navegador, a "câmera" vira um seletor de arquivo; no APK abre a câmera e a galeria de verdade.

## Gerar o APK

**Opção 1: GitHub Actions (recomendado, nada para instalar)**
Veja o README na raiz do repositório.

**Opção 2: no seu PC, com Android Studio**

```bash
npm run build
npx cap sync android
npx cap open android      # abre o Android Studio
```

No Android Studio: **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.
O arquivo sai em `android/app/build/outputs/apk/debug/app-debug.apk`.

> A URL da API é embutida no build. Se mudar a API, gere o APK de novo.

## Estrutura

```
src/
  main.js              inicialização (Ionic, rotas, sessão)
  router/index.js      rotas + guarda de login
  services/
    api.js             todas as chamadas à API (fetch + token JWT)
    sessao.js          sessão salva no aparelho (Capacitor Preferences)
    foto.js            câmera / galeria (Capacitor Camera)
    mapa.js            mapa Leaflet + marcadores
    formato.js         datas e preços em pt-BR
  views/               uma tela por arquivo
  components/          EventoCard (item da lista)
  theme.css            cores e estilos globais
android/               projeto Android gerado pelo Capacitor
```
