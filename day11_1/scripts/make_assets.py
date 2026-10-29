"""외부 이미지 요청 없이 사용할 로컬 상품 일러스트를 생성합니다. Python 표준 라이브러리만 사용."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'static' / 'images'
ART = {
    'mug': '''<ellipse cx="202" cy="285" rx="94" ry="13" fill="#615947" opacity=".13"/>
<path d="M257 132h22c60 0 59 91 3 94h-24" fill="none" stroke="#c6ad83" stroke-width="20"/>
<path d="M115 124h150l-10 126q-3 31-63 31t-65-31z" fill="url(#ceramic)"/>
<ellipse cx="190" cy="124" rx="75" ry="18" fill="#d9c7a5"/><ellipse cx="190" cy="123" rx="63" ry="12" fill="#866b4a"/>
<path d="M137 151l8 88q2 14 18 18" fill="none" stroke="#fff" stroke-width="7" opacity=".24"/>
<path d="M172 86q-14-14 1-29m30 29q-14-14 1-29" fill="none" stroke="#fbfaf4" stroke-width="4" opacity=".6"/>''',
    'lamp': '''<ellipse cx="200" cy="300" rx="90" ry="12" fill="#615947" opacity=".13"/>
<path d="M194 172h13v112h-13z" fill="url(#wood)"/><ellipse cx="200" cy="284" rx="54" ry="12" fill="#9b7555"/>
<path d="M178 264h44l25 23h-94z" fill="url(#wood)"/>
<path d="M155 65h90l56 120H99z" fill="url(#linen)"/>
<ellipse cx="200" cy="185" rx="101" ry="13" fill="#ddd1b8"/>
<path d="M171 69l-28 107m48-107l-9 107m29-107l9 107m10-107l28 107" stroke="#b5a98c" stroke-width="2" opacity=".25"/>
<path d="M212 286q50 15 78-4" stroke="#646354" stroke-width="2" fill="none"/>''',
    'chair': '''<ellipse cx="204" cy="308" rx="99" ry="12" fill="#615947" opacity=".13"/>
<path d="M132 155l-9 145m38-103l7 106m82-107l-3 106m25-147l17 147" stroke="url(#wood)" stroke-width="13" stroke-linecap="round"/>
<path d="M131 83q69-27 142 0l-5 88q-68 15-134 0z" fill="url(#wood)"/>
<path d="M142 98q56-14 117 0m-114 17q56-14 111 0" stroke="#b68b5e" stroke-width="2" fill="none" opacity=".7"/>
<path d="M128 184q70-16 148 0l20 32q-88 27-188 0z" fill="#a77b4f"/>
<path d="M128 177q70-16 148 0l20 31q-88 27-188 0z" fill="url(#wood)"/>''',
    'bag': '''<ellipse cx="200" cy="302" rx="92" ry="12" fill="#615947" opacity=".13"/>
<path d="M148 129V94q0-49 50-49t50 49v35" stroke="#bdaf8e" stroke-width="16" fill="none"/>
<path d="M114 118h172l12 159q-84 31-195 0z" fill="url(#linen)"/>
<path d="M123 130h153l10 138q-85 19-171 0z" stroke="#beb49a" fill="none" stroke-width="2" stroke-dasharray="3 4"/>
<path d="M150 120v39m98-39v39" stroke="#c1b395" stroke-width="13"/>
<text x="200" y="225" text-anchor="middle" font-family="Georgia,serif" font-size="28" fill="#75785f" letter-spacing="2">ondo</text>''',
    'clock': '''<ellipse cx="201" cy="302" rx="103" ry="12" fill="#615947" opacity=".1"/>
<circle cx="200" cy="173" r="112" fill="url(#wood)"/><circle cx="200" cy="173" r="102" fill="#f3efe3"/>
<path d="M200 83v12m90 78h-12m-78 90v-12m-90-78h12" stroke="#8a826b" stroke-width="3"/>
<path d="M200 114v59l43 28" stroke="#4b5547" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="200" cy="173" r="6" fill="#a47d52"/>
<path d="M153 94l5 9m89-9l-5 9m-122 25l9 5m142-5l9-5m-9 94l9 5m-151-5l-9 5m38 21l-5 9m89-9l5 9" stroke="#c2bca7" stroke-width="2"/>''',
    'vase': '''<ellipse cx="200" cy="304" rx="79" ry="12" fill="#615947" opacity=".13"/>
<path d="M200 166q-8-74 14-134m-12 104q-41-62-55-91m53 64q42-56 67-62" fill="none" stroke="#737e52" stroke-width="3"/>
<path d="M213 66q-37-4-22-34 28 0 22 34m-9 35q30-25 40-6-9 22-40 6m-45-29q-29 1-25-28 26-2 25 28m77-1q-3-33 28-27 9 25-28 27" fill="#8a9669"/>
<path d="M172 135h56l-5 30q58 35 45 101-8 37-68 37t-68-37q-13-66 45-101z" fill="url(#ceramic)"/>
<ellipse cx="200" cy="135" rx="28" ry="7" fill="#ab8e66"/>
<path d="M177 186q-30 23-23 65" fill="none" stroke="#fff" stroke-width="8" opacity=".17"/>''',
}
DEFS = '''<defs>
<linearGradient id="ceramic"><stop stop-color="#c2a77b"/><stop offset=".42" stop-color="#e0cba5"/><stop offset="1" stop-color="#ba9b70"/></linearGradient>
<linearGradient id="wood"><stop stop-color="#b98c5d"/><stop offset=".5" stop-color="#ddbd8e"/><stop offset="1" stop-color="#a4794e"/></linearGradient>
<linearGradient id="linen"><stop stop-color="#c9bfa4"/><stop offset=".5" stop-color="#f2ebd8"/><stop offset="1" stop-color="#cabe9f"/></linearGradient>
</defs>'''
if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    for key, art in ART.items():
        (ROOT / f'{key}.svg').write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 350">{DEFS}{art}</svg>', encoding='utf-8')
    print(f'{len(ART)} assets created')
