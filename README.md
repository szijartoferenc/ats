![image](https://github.com/user-attachments/assets/59379868-84a9-4ba5-a42e-67aac45d08fa)


1. Projekt célja: A projekt célja, hogy egy AI-alapú ATS rendszert építsek, amely képes önéletrajzokat és álláshirdetéseket elemezni, és összehasonlítani azokat az iparági kulcsszavak, készségek és pontszámok alapján. Az alkalmazás képes a kulcsszavak kiemelésére, az iparági szavak generálására, és egy vizuális értékelést nyújt a felhasználó számára, amely segíti a munkaadókat a legalkalmasabb jelöltek kiválasztásában.

2. Alkalmazás felépítése: A program egy Streamlit-alapú webalkalmazás, amely könnyen használható felülettel rendelkezik és többféle fájltípust (PDF, DOCX, TXT) képes kezelni. Az alkalmazás kulcsfontosságú elemei:

    Dokumentumok feldolgozása: PDF, DOCX és TXT fájlok szövegének kinyerése.

    AI alapú elemzés: Google Generative AI (Gemini) API használata a munkaerőpiaci kereslet és a jelölt profil összehasonlításához.

    Vizuális megjelenítés: Kulcsszavak sűrűségét és pontszámokat megjelenítő grafikonok, táblázatok és diagramok.

    Interaktivitás: A felhasználó feltöltheti az önéletrajzát és a munkaköri leírást, majd az alkalmazás összehasonlítja azokat és visszajelzést ad.

3. Fejlesztési folyamat:

a) Technológiai választás és inicializálás: A projektet Pythonban készítettem, a következő kulcsfontosságú könyvtárakat használva:

    Streamlit: Az alkalmazás frontend fejlesztésére, könnyen használható interaktív felületet biztosít.

    Pandas: Az adatok kezelésére és a kulcsszavak gyakoriságának kiszámítására.

    Plotly: Az interaktív diagramok és grafikonok készítésére.

    PyMuPDF (fitz): PDF fájlok szövegének kinyerésére és előnézetének generálására.

    Google Generative AI: Az AI-alapú tartalom generálására és az önéletrajzok elemzésére.

b) Fájlok kezelése: A felhasználó által feltöltött fájlokat a rendszer a következő módon dolgozza fel:

    PDF fájlok: A PDF szövegét a PyMuPDF könyvtár segítségével olvassuk be.

    DOCX fájlok: A python-docx könyvtárral dolgozzuk fel, hogy a dokumentum összes szöveges tartalmát ki tudjuk nyerni.

    TXT fájlok: Egyszerű szöveges fájlok, amelyek tartalmát közvetlenül beolvassuk.

c) Kulcsszavak és iparági szavak elemzése: A rendszer a munkaadó által megadott álláshirdetés alapján generál kulcsszavakat az AI segítségével. A Gemini API segítségével generáltam 10 releváns kulcsszót, amelyek az álláshirdetéshez kapcsolódnak, majd összehasonlítom ezeket a feltöltött önéletrajz kulcsszavaival.

d) AI alapú értékelés: Az AI képes az önéletrajzok és az álláshirdetés közötti hasonlóságot kiértékelni, figyelembe véve az iparági kulcsszavakat, és visszajelzést ad a jelölt alkalmasságáról. Az elemzés során az AI kimenete a következőket tartalmazza:

    Kiemelt kulcsszavak (egyező és hiányzó).

    A jelölt alkalmassági pontszáma (0-100).

    A hiányzó készségek kategorizálása (technikai vs. soft skills).

    Fejlesztési tippek.

e) Vizualizáció és szűrés: Az alkalmazás grafikus megjelenítést biztosít a kulcsszavak sűrűségének és az alkalmassági pontszámoknak. A Plotly segítségével diagramokat generálunk, amelyek lehetővé teszik a felhasználó számára, hogy könnyen áttekintse a kulcsszavak gyakoriságát és az alkalmasság különböző szempontjait.

    Kulcsszavak gyakoriságának megjelenítése: A rendszer megjeleníti a kulcsszavak gyakoriságát egy diagram formájában.

    Alkalmassági pontszámok: A különböző álláshirdetésekhez tartozó alkalmassági pontszámok összehasonlítása egy színes diagramon.

f) Exportálás: A felhasználók képesek exportálni az adatokat CSV vagy Excel formátumban, amely tartalmazza a kulcsszavak gyakoriságát és az alkalmassági pontszámokat.

4. Funkciók és optimalizálás:

    Törlő gomb: A felhasználó képes törölni a beillesztett álláshirdetést, ha újabb adatokat szeretne megadni.

    Pontszámok szűrése: A rendszer lehetőséget biztosít arra, hogy csak az utolsó 5 elem pontszámát jelenítse meg, így könnyebben nyomon követhető a fejlődés.

    PDF exportálás: A grafikonok és táblázatok PDF formátumban való exportálása segíti a jelentéskészítést.

5. Tesztelés és hibakeresés: A fejlesztési folyamat során folyamatosan teszteltem a rendszer különböző részeit, beleértve a fájlok feldolgozását, az AI válaszokat, valamint a grafikus megjelenítést. A hibákat gyorsan orvosoltam, és gondoskodtam arról, hogy a rendszer minden típusú bemeneti adatot helyesen kezeljen.

6. Következő lépések: A rendszer jövőbeli fejlesztése magában foglalja a többféle nyelv támogatását, a felhasználói visszajelzések integrálását, és az AI elemzési algoritmusok további finomhangolását a még pontosabb eredmények érdekében.
