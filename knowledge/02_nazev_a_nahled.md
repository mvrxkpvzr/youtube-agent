# 02 Název a náhled (balíček)

**Kdy číst:** fáze 1 (návrh u každého úhlu) a fáze 4 (finální 3 varianty do `publish/<lang>/titles_thumbnails.md`).

## Princip
Video na YouTube nejdřív soutěží o **klik** (CTR), pak o **čas sledování**. Dobrý název a náhled bez dodaného
slibu zvednou klik a zabijí retenci. [YouTube] Vestavěný A/B test názvů a náhledů v YouTube Studiu vybírá vítěze
podle **podílu času sledování**, ne podle CTR, právě proto. Cílem je tedy *poctivý* slib, který se vyplatí kliknout.

## Pravidla pro název
1. **Podstatné na začátek.** [Praxe] Na mobilu se název často ořízne kolem 40–60 znaků. První 3–5 slov nese slib.
   Celý název ideálně ≤ 60 znaků (limit 100). `craft_check.py` hlásí > 60 jako WARN.
2. **Kontrast nebo číslo.** „Za 12 000 $ dostali stan“ > „Příběh Fyre Festivalu“.
3. **Mezera ve zvědavosti, ne lež.** Název otevírá otázku, video na ni odpoví. Slib splň do 30 s videa [U nás, pravidlo kanálu].
4. **Extrémní, ale pravdivé sloveso.** [Praxe, uniklý dokument MrBeast, neověřená pravost] „Přežil“ táhne víc než „strávil“.
   U nás jen tehdy, když to fakta dovolí.
5. **Žádné:** VERZÁLKY přes celý název, víc než 1 emoji, „ŠOKUJÍCÍ PRAVDA“, otazník za oznamovací větou, jméno
   kanálu, hashtagy v názvu.
6. Česky přirozeně, nahlas přečtené. Když to zní jako titulek bulvárního webu, přepiš.

## Pravidla pro náhled (1280×720, čitelné na 160 px šířky)
1. **Max 3 prvky** [Praxe]: jeden hlavní objekt, max 3–4 slova textu, jeden kontrast (barva, razítko, šipka).
2. **Text doplňuje název, neopakuje ho.** Název říká „co“, náhled ukazuje „proč klikat“.
3. **Kontrast a čitelnost:** text ≥ 1/6 výšky obrázku, tmavý obrys nebo stín, žluto-černá / bílo-červená.
   Zkontroluj zmenšením na 160×90 (`ffmpeg -vf scale=160:-1`) a prohlédni.
4. **Obličej s emocí** pomáhá [Praxe, bez kontrolované studie], ale u nás **jen s právy k fotce**.
   Žádná realistická AI podoba skutečné osoby (pravidlo kanálu + YouTube povinné označení syntetického obsahu).
   Náhrada: vlastní 3D objekt, který nese příběh (stan, sendvič, razítko „FALEŠNÉ“).
5. **Žádná cizí loga** a značky jako hlavní prvek (eBay, Netflix). Vlastní maketa bez loga.
6. Vizuální podpis kanálu: stejné písmo (Archivo Black / Anton pro latinku bez háčků), akcent `#F2B134`.

## Postup
1. Ke každému úhlu (G1) jeden název a jeden náhled slovy. Pokud nejde napsat, úhel je slabý.
2. Ve fázi 4: 3 názvy a 3 koncepty náhledu, u každého „slib → kde ve videu se splní (čas)“.
3. Náhledy vyrob jako PNG (Blender still nebo Pillow), zmenši na 160 px a prohlédni.
4. Doporuč dvojici název + náhled, které nesou **stejný slib**.
5. Po publikaci: A/B test až 3 variant v YouTube Studiu (Test & Compare / A/B testing). Výsledek zapiš do `lessons.md`.

## Kontrolní otázky před G5
- Splní video slib z názvu do 30 s? (čas)
- Je text náhledu čitelný na 160 px?
- Neporušuje náhled práva (cizí foto, logo) ani pravidla o syntetickém obsahu?
