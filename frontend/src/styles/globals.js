export const GLOBAL_STYLES = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --cream:#faf7f2;--warm-white:#fffef9;
  --bark:#3d2b1f;--bark-mid:#5c4033;--bark-light:#7a5c4a;
  --amber:#c8722a;--amber-l:#e8944a;
  --sage:#5a7a5a;
  --parchment:#f0e8d8;--parchment-d:#ddd0b8;
  --panel:#16110e;--panel-l:#201810;
  --mono:#f0c060;
  --cyan:#4ab8c8;--cyan-d:#2a8898;
  --violet:#9878d8;--violet-d:#6040b0;
  --green:#5ab87a;--red:#d86858;
  --r:16px;--rs:8px;
}
html,body,#root{height:100%;font-family:'DM Sans',sans-serif;background:var(--cream);color:var(--bark);overflow:hidden}
.app{display:flex;height:100vh}

@media(max-width:1100px){.rp{display:none}}
@media(max-width:720px){.lp{display:none}.bub{max-width:85%}}
`;
