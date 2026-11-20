// Original anime-style character, drawn in SVG. Same face for every candidate: only the name tag changes.
// face(expr, tag, opts) -> SVG string. expr: 'neutral' | 'happy' | 'shock'
window.face = function (expr, tag, o = {}) {
  const skin = '#f2c6a0', hair = '#2a1f5c', hairHi = '#3a3f8f', iris = o.iris || '#2f6bff';
  const ink = '#1a1446';
  let eyes = '', mouth = '', extra = '', brows = '';
  if (expr === 'happy') {
    eyes = `<path d="M128 232 Q160 198 192 232" fill="none" stroke="${ink}" stroke-width="9" stroke-linecap="round"/>
            <path d="M208 232 Q240 198 272 232" fill="none" stroke="${ink}" stroke-width="9" stroke-linecap="round"/>`;
    mouth = `<path d="M168 290 Q200 330 232 290 Z" fill="#7a1f2b" stroke="${ink}" stroke-width="6" stroke-linejoin="round"/>
             <path d="M180 306 Q200 320 220 306" fill="#ff8a9a"/>`;
    extra = `<ellipse cx="140" cy="268" rx="22" ry="10" fill="#ff8aa8" opacity=".6"/><ellipse cx="260" cy="268" rx="22" ry="10" fill="#ff8aa8" opacity=".6"/>`;
    brows = `<path d="M130 188 Q160 172 188 184" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M212 184 Q240 172 270 188" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  } else if (expr === 'shock') {
    eyes = `<ellipse cx="160" cy="232" rx="32" ry="40" fill="#fff" stroke="${ink}" stroke-width="7"/><ellipse cx="240" cy="232" rx="32" ry="40" fill="#fff" stroke="${ink}" stroke-width="7"/>
            <circle cx="160" cy="236" r="6" fill="${ink}"/><circle cx="240" cy="236" r="6" fill="${ink}"/>`;
    mouth = `<ellipse cx="200" cy="305" rx="22" ry="28" fill="#5a1520" stroke="${ink}" stroke-width="6"/>`;
    extra = `<g stroke="#5a7bff" stroke-width="6" opacity=".75"><line x1="145" y1="140" x2="145" y2="185"/><line x1="170" y1="135" x2="170" y2="182"/><line x1="195" y1="132" x2="195" y2="180"/><line x1="220" y1="135" x2="220" y2="182"/><line x1="245" y1="140" x2="245" y2="185"/></g>
             <path d="M300 170 Q318 200 300 222 Q282 200 300 170 Z" fill="#9ad8ff" stroke="${ink}" stroke-width="5"/>`;
    brows = `<path d="M128 178 Q158 196 188 186" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M212 186 Q242 196 272 178" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  } else {
    eyes = [160, 240].map(x => `<ellipse cx="${x}" cy="232" rx="30" ry="38" fill="#fff" stroke="${ink}" stroke-width="6"/>
            <ellipse cx="${x}" cy="238" rx="22" ry="30" fill="${iris}"/><ellipse cx="${x}" cy="244" rx="11" ry="15" fill="${ink}"/>
            <circle cx="${x - 9}" cy="222" r="8" fill="#fff"/><circle cx="${x + 9}" cy="252" r="4" fill="#fff"/>
            <path d="M${x - 32} 214 Q${x} 186 ${x + 32} 214" fill="none" stroke="${ink}" stroke-width="9" stroke-linecap="round"/>`).join('');
    mouth = `<path d="M184 300 Q200 310 216 300" fill="none" stroke="${ink}" stroke-width="6" stroke-linecap="round"/>`;
    brows = `<path d="M130 182 Q160 170 188 180" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M212 180 Q240 170 270 182" stroke="${hair}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  }
  return `<svg viewBox="0 0 400 520" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <path d="M70 230 L52 120 L110 70 L150 30 L210 20 L270 36 L320 80 L350 140 L332 250 L300 300 L100 300 Z" fill="${hair}" stroke="${ink}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M40 520 L60 430 Q90 380 160 368 L240 368 Q310 380 340 430 L360 520 Z" fill="#5b3cc4" stroke="${ink}" stroke-width="8"/>
  <path d="M160 368 L200 430 L240 368 Z" fill="#fff" stroke="${ink}" stroke-width="6"/>
  <path d="M192 400 L208 400 L216 470 L200 490 L184 470 Z" fill="#e8364f" stroke="${ink}" stroke-width="5"/>
  <rect x="172" y="320" width="56" height="60" fill="${skin}" stroke="${ink}" stroke-width="7"/>
  <ellipse cx="110" cy="240" rx="18" ry="28" fill="${skin}" stroke="${ink}" stroke-width="7"/><ellipse cx="290" cy="240" rx="18" ry="28" fill="${skin}" stroke="${ink}" stroke-width="7"/>
  <path d="M110 160 Q108 290 200 345 Q292 290 290 160 Z" fill="${skin}" stroke="${ink}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M100 175 L118 110 L142 150 L160 92 L186 145 L208 88 L228 146 L252 96 L268 150 L288 112 L302 178 L282 150 L262 168 L240 132 L220 170 L198 128 L178 170 L156 134 L136 170 L116 150 Z" fill="${hair}" stroke="${ink}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M160 100 L176 132 L190 98" fill="none" stroke="${hairHi}" stroke-width="6" stroke-linecap="round"/>
  ${brows}${eyes}
  <path d="M198 258 L192 280 L204 280" fill="none" stroke="#c98a6a" stroke-width="5" stroke-linecap="round"/>
  ${mouth}${extra}
  <g transform="rotate(-4 300 450)"><rect x="232" y="420" width="136" height="54" rx="6" fill="#fff" stroke="${ink}" stroke-width="5"/>
  <text x="300" y="456" text-anchor="middle" font-family="BG" font-size="${tag.length > 7 ? 17 : 20}" fill="${ink}">${tag}</text></g>
</svg>`;
};
