# QA report – _example_test_text (de)

Video: `render/preview.de.mp4` · délka 121.3 s

## ERROR (0)

## WARN (12)
- titulky: 36 titulků, problémy: ['#2: kratší než 1 s', '#5: 17 zn./s', '#15: 17 zn./s', '#23: řádek > 42 znaků', '#23: 18 zn./s', '#24: 17 zn./s']
- WARN  shotlist.cs.json SC001: claim C001 is attributed – narration must name the source
- WARN  shotlist.cs.json SC002: claim C004 is attributed – narration must name the source
- WARN  shotlist.cs.json SC003: claim C002 is attributed – narration must name the source
- WARN  shotlist.cs.json SC003: claim C005 is attributed – narration must name the source
- WARN  shotlist.cs.json SC004: claim C006 is attributed – narration must name the source
- WARN  shotlist.de.json SC001: claim C001 is attributed – narration must name the source
- WARN  shotlist.de.json SC002: claim C004 is attributed – narration must name the source
- WARN  shotlist.de.json SC003: claim C002 is attributed – narration must name the source
- WARN  shotlist.de.json SC003: claim C005 is attributed – narration must name the source
- WARN  shotlist.de.json SC004: claim C006 is attributed – narration must name the source
- RUČNĚ: poslech celé stopy, kontrola výslovnosti jmen, vizuální kontrola každé karty, kontrola citací na obrazovce

## OK (10)
- rozlišení 1920x1080
- fps 25.0
- kodeky h264/aac 48000 Hz
- hlasitost -14.3 LUFS (cíl -14 ±1)
- true peak -1.3 dBFS (max -1.0)
- černé úseky ≥0,5 s: 0
- statický obraz ≥8 s: 0 (dlouhé karty bez pohybu působí jako slideshow)
- zpětný přepis: bez chyb
- validátor projektu: 0 errors, 10 warnings
- licence hlasu: [('qwen_de', 'Apache-2.0', True)]
