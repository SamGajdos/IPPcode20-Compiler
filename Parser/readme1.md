

# Implementační dokumentace k 1. úloze do IPP 2019/2020

Jméno a přijmení: **Samuel Gajdoš**

Login: **xgajdo26**

 

## Analyzátor kódu v IPPcode20 (parse.php)

Hlavné telo programu sa skladá z troch častí. Prvá časť kontroluje či programu boli zadané správne parametre,
v našom prípade argument --help. Druhá časť predstavuje cyklus while, ktorý číta program zo štandardného vstupu po riadkoch.
Ako náhle narazí na správnu hlavičku programu, ukončí cyklus. V opačnom prípade vyhodí chybu s operačným kódom 21. Tretia časť predstavuje skoro rovnaký cyklus, no kontroluje už iba inštrukcie napísané za hlavičkou.

**Kontrola hlavičky:**
Hľadá v programe hlavičku *IPPCODE20*, keďže na veľkosti písmen nezáleží, prevádza všetky znaky hlavičky na veľké.
Okrem komentárov a prázdnych riadkov sa musí táto hlavička objavovať v programe ako prvá. Po úspešnom skontrolovaní
môžeme prejsť na kontrolu inštrukcií.

**Kontrola inštrukcií:**
Program načíta jeden riadok (inštrukciu), ktorú následne rozdelí do poľa slov či tokenov (*$words*). Toto pole sa následne pošle do funkcie *instDec*, ktorá predstavuje "dekodér" inštrukcií. Na základe názvu inštrukcie ju potom ďalej kontroluje podľa ich parametrov.
Tieto parametre sa kontrolujú na základe ich "druhu" (var, symb, label) a taktiež sa kontroluje či bol zadaný správny počet operandov.
Využívajú sa na to funkcie *checkVarName*,*checkVar*,*checkSymb*, *checkLab* a pre počet parametrov funkcia *checkPar*. Ak kontrola prebehla v poriadku pokračuje sa na načítanie ďalšieho riadka(inštrukcie) v cykle až do konca vstupného programu.

**Chybové stavy:**
Pri nájdení chýb počas kontroly programu v IPPCode20 sa na chybný výstup vypíše daná chyba pomocou funkcie *writeErr*, ktorá má parameter chybného operačného kódu. Operačné kódy sú pre jednoduchosť v kóde reprezentované makrami.

**Výpis XML:**
Na štandartný výstup sa pri úspešnej kontrole programu vygeneroval odpovedajúci XML kód pomocou *XMLWriteru*.
Pomocné funkcie ku generovaniu sú *writeXmlHead* a *writeXmlArg*.
