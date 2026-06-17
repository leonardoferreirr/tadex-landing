# Tadex Transportes — Landing Page

Landing institucional da Tadex Transportes (logística, 29 anos). HTML/CSS/JS puro, sem build, portável (WordPress via FTP ou Vercel estático).

## Estrutura
- `index.html` — página única (header, hero, serviços, soluções, cotação, diferenciais, depoimentos, CTA, footer)
- `styles.css` — design system (tokens de cor/tipo) + responsivo + animações
- `script.js` — menu mobile, sombra no header ao rolar, scrollspy, reveal on scroll
- `assets/` — logo, selo, fotos (WebP otimizado) e fontes Poppins self-hosted

## Paleta
- Laranja `#F54900` · Navy `#16223C` · Creme `#FAF1EA`

## Performance
Lighthouse mobile **98** (LCP 2.0s, CLS 0). Hero pré-carregado, fontes self-hosted, imagens WebP, terceiros zero.

## Rodar local
```
npx http-server . -p 4795 -c-1
```

## Deploy
Estático na Vercel (`vercel.json` com `framework: null`). Assets com cache imutável de 1 ano.
