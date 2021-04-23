


# Implementační dokumentace k 2. úloze do IPP 2019/2020

Jméno a přijmení: **Samuel Gajdoš**

Login: **xgajdo26**

 

## Interpret XML reprezentace kódu (interpret.py)

Program *interpret.py* interpretuje jazyk *IPPCode20*, ktorý je do *interpret.py* poslaný vo formáte *XML*.
Hlavné telo programu *interpret.py* sa skladá zo spracovávania argumentov, analýzy *XML* formátu a následne cyklu na čítanie samotných inštrukcií.

### Spracovávanie argumentov
Na spracovávanie argumentov sa využíva funkcia `getopt`. Tieto parametre sa uložia do poľa `opt`, ktoré sa spracuje a nastaví premenné na správne hodnoty. V prípade uvedenia iba jedného z argumentov `--source=file` alebo `--input=file`, sa do premennej pre neuvedený parameter uloží štandardný vstup a z neho sa načítajú hodnoty. Pri uvedení ďalších parametrov sa ich príznaky nastavia na *True*.
### Analýza XML formátu
Pomocou knižnice *ElementTree* sa vstupný *XML* formát uloží do stromovej štruktúry. K jeho koreňu sa pristupuje pomocou premennej `root`. Následne prebieha kontrola hlavičky a ďalších povinných ale aj dobrovoľných atribútov.
*XML* strom sa podľa atribútu `order` zoradí a pomocou cyklu sa kontrolujú ďalšie parametre. Napríklad, či sa atribút `order` neopakuje, či je kladný a pod. Okrem toho  sa v cykle vyhľadávajú prípadné inštrukcie *Label*, jej návestia sa ukladajú do slovníka *LBL*. Jeho kľúče sú názvy návestí a jeho hodnoty sú čísla o ktorú inštrukciu v poradí ide.
### Čítanie inštrukcií
Pred samotným cyklom sa inicializujú rámce, ktoré sú reprezentované slovníkmi.
Kľúče sú mená premenných a ich hodnoty sú hodnoty premenných, ich typ je reprezentovaný typom v jazyku *Python*. Preto aj prístup k nim sa kontroluje pomocou funkcie `isinstance()`.
Následné beží cyklus, ktorý podľa poradia inštrukcií v stromovej štruktúre číta a vykonáva inštrukcie. 
Hlavnou funkciou na dekódovanie inštrukcií je `opCodeParse(instruction)`.
Každá inštrukcia má svoju funkciu na vykonanie, až na niektoré, ktoré sú spojené do jednej funkcie s využitím objektov.
#### Triedy programu:
***String***: Trieda pre vykonanie inštrukcií STRI2INT, CONCAT, GETCHAR.
***Not***: Jednoduchá trieda pre vykonanie inštrukcie NOT.
***Arithmetic***: Trieda pre aritmetické inštrukcie: ADD, SUB, MUL, IDIV, LT, GT, EQ, AND, OR.
***Stack***: Trieda pre ADT zásobník, využitie: dátový zásobník, zásobník rámcov, zásobník volaní inšt. CALL.
### Chybové stavy
V prípade chybových stavov sa volá funkcia `writeErr(errcode)`, kde `errcode` je návratová hodnota v prípade danej chyby. Tie sú pre zjednodušenie reprezentované ako globálne premenné.
### Rozšírenie STATI
Pri parametri `--stats=file` sa dané štatistiky uložia do súboru. V prípade, že sa súbor na výpis nenašiel, vytvorí sa nový. Parameter `--vars` slúži na výpis maximálneho počtu premenných využitých v programe a `--inst` na výpis počtu vykonaných inštrukcií. Tieto parametre sa môžu viackrát opakovať. V tom poradí v akom budú napísané sa aj do výstupného súboru vypíšu tieto štatistiky.

## Testovací rámec (test.php)
Program *test.php* slúži na otestovanie správnosti programov *parse.php* a *interpret.py*.
Jeho implementácia sa skladá zo spracovania vstupných parametrov, hlavnej funkcie na vykonanie testov a pomocných funkcií na výpis *html* výstupu.
### Spracovanie vstupných parametrov
Pomocou funkcie `getopt` sa spracujú vstupné parametre. Následne sa kontroluje, či údaje k zadaným parametrom sú korektné. Ak neboli zadané sú nahradené implicitnými hodnotami. Pri zadaní súborov programov sa kontrolujú či existujú. V prípade zadaného adresára aj to či sa naozaj jedná o adresár.
### Hlavná funkcia main_test
Funkcia `main_test($directory)` prechádza všetky testy v danom adresári. Podľa koncoviek sa všetky súbory zoradia do polí pre jednoduchšiu manipuláciu a možno aj o niečo rýchlejší prístup. Následne sa kontroluje či súbory `.in` a `.out` k súborom s koncovkou `.src` nechýbajú, ak áno tak sa vytvoria. Typ testovania prebieha na základe zadaných parametrov. V prípade zadania parametru `--recursive` sa do poľa adresárov ukladajú tie adresáre, ktoré sa nachádzajú v aktuálnom adresári. Funkcia `main_test` sa tak rekurzívne volá a ako parameter si vezme adresáre z tohto poľa.
### Pomocné funkcie na HTML výpis
*HTML* výstup sa ukladá do globálnej premennej `$html`. Tá sa postupne rozširuje o tabuľky s výsledkami testov.
Asi najzákladnejšia funkcia je `html_AddTest`, ktorá pridá výsledok jedného testu do tabuľky. Každý adresár je vo výstupe reprezentovaný vlastnou tabuľkou aj s výsledkami testov. Na konci celého testovania je vygenerovaná malá tabuľka s popisom 'TOTAL PASSED ALL' a následne s celkovým výsledkom testov pre všetky adresáre, kde boli vykonané testy.
Úplne na konci je vygenerovaná jednoduchá tabuľka testov, ktoré zlyhali a taktiež informácia o tom kde najskôr zlyhali, či to bol až nesprávny výstup alebo hneď nesprávny návratový kód.
 
