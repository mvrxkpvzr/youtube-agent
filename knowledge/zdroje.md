# Zdroje znalostní vrstvy (výzkum 21. 10. 2026)

Hledáno přes webové vyhledávání 21. 10. 2026. Některé stránky (support.google.com, alexanderjarvis.com) nešly z cloudu
přímo otevřít, proto jsou u nich uvedené sekundární zdroje. Štítky podle `README.md`.

## Pravidla YouTube [YouTube]
- Inauthentic content (dříve repetitious), účinnost 15. 7. 2025: Plagiarism Today https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/ ;
  The Week https://www.theweek.in/news/sci-tech/2025/07/10/youtube-rolls-out-new-rules-to-curb-ai-content-who-is-affected-and-who-is-safe.amp.html ;
  CineD https://cined.com/youtube-set-to-crack-down-on-ai-slop-with-monetization-policy-update (sekundární; oficiální text: YouTube Help „YouTube channel monetization policies“).
- Označení syntetického obsahu: Engadget https://www.engadget.com/youtube-lays-out-new-rules-for-realistic-ai-generated-videos-154248008.html ;
  NBC News https://www.nbcnews.com/tech/tech-news/youtube-says-will-require-creators-label-ai-content-rcna143937
- A/B test názvů a náhledů podle podílu času sledování: https://support.google.com/youtube/answer/13861714 , https://support.google.com/youtube/answer/16391400
- Kapitoly (00:00, ≥ 3, vzestupně): https://support.google.com/youtube/answer/9884579

## Retence, hook, struktura [Praxe]
- vidIQ, retence v 30. s (≥ 60–65 %): https://vidiq.com/blog/post/increase-audience-retention-youtube/
- Uniklý produkční dokument MrBeast (CTR/AVD/AVP, první minuta, minuty 3–6; pravost nepotvrzena):
  https://www.alexanderjarvis.com/memo-how-to-succeed-in-mrbeast-production/ , https://www.creatorhandbook.net/leaked-document-allegedly-reveals-mrbeasts-secrets-to-youtube-success-the-key-takeaways/
- B-roll jen když ilustruje (kontrolovaný test): https://www.opus.pro/blog/does-b-roll-increase-watch-time
- Retenční střih a propad 25–35 s: https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8
- Pravidlo „ale / proto“ (Parker & Stone, NYU 2014): https://perell.com/note/but-therefore-rule/ , https://en.wikipedia.org/wiki/Transition_(fiction)
- Outlier skóre: https://support.vidiq.com/en/articles/9660010-outliers , https://outlierkit.com/resources/outlier-scores/

## Balíček [Praxe]
- Délka názvu a oříznutí na mobilu (odhady 40–70 znaků): https://air.io/en/audience-growth/how-to-write-a-youtube-title-that-gets-clicked-research-across-11-niches
- Náhledy (kontrast, ≤ 3 prvky, čitelnost na mobilu; bez kontrolovaných studií): https://vidiq.com/blog/post/youtube-thumbnail-design-tips/

## Humor [Praxe]
- Komické prostředky (understatement, ironie): https://en.wikipedia.org/wiki/Comedic_device ; pravidlo tří, callback: https://nofilmschool.com/john-vorhaus-comedy-writing-tools

## Zvuk [Praxe]
- −14 LUFS, TP ≤ −1 dBTP, hudba 15–20 dB pod řečí: https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/ , https://vidpros.com/fix-background-music-too-loud-video/

## AI pach [Praxe]
- Znaky „AI slop“: https://www.vozo.ai/blogs/youtube/youtube-ai-slop , https://hackernoon.com/youtubes-ai-slop-crackdown-cant-tell-a-directed-ai-film-from-a-bot-farm

## Blender [Praxe]
- Cycles sampling, adaptivní vzorkování: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- EEVEE vyžaduje OpenGL i bez displeje (softwarově Mesa/llvmpipe): https://devtalk.blender.org/t/blender-2-8-unable-to-open-a-display-by-the-rendering-on-the-background-eevee/1436

## Zadání Miry (závazné)
- Role „Autonomous YouTube documentary creative director“, 21. 10. 2026 → `00_role.md`
- Prioritní modul: internetové archivy, autentické záběry a dokumentární střih → `12_vizualni_reserse_a_prava.md`
- Prioritní modul: profesionální hudba od lidských skladatelů → `09_hudba_a_zvuk.md`
- Module 4.0 Faceless documentary studio & continuous improvement → `01`, `04`, `06`, `11`, brány Q1–Q7 (`pipeline/gates.py`)
