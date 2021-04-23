<?php
# 1. Projekt z predmetu IPP, parse.php
# Autor: Samuel Gajdos
# Rok: 2020

//Pre chybne vypisy
ini_set('display_errors', 'stderr');

//definicia hodnot chyb
const erLS = 23;
const erPar = 10;
const erStdin = 11;
const erStdout = 12;
const erHead = 21;
const erOpcode = 22;

// Vypis chyb
function writeErr($errcode)
{
    global $order, $xml;
    switch ($errcode) {
        case erLS:
            fwrite(STDERR, "Chyba v " . $order . ". instrukcii.. :");
            fwrite(STDERR, "lexikalna alebo syntakticka chyba.\n");
            break;
        case erPar:
            fwrite(STDERR, "Chyba, zle zadany alebo nespravny pocet parametrov programu.\n");
            break;
        case erStdin:
            fwrite(STDERR, "Chyba, nespravny vstup.\n");
            break;
        case erStdout:
            fwrite(STDERR, "Chyba, nespravny vystup.\n");
            break;
        case erHead:
            fwrite(STDERR, "Chyba, nespravne napisana alebo ziadna hlavicka programu.\n");
            break;
        case erOpcode:
            fwrite(STDERR, "Chyba v " . $order . ". instrukcii.. :");
            fwrite(STDERR, "nespravny zapisany operacny kod.\n");
    }
    exit($errcode);
}
///////////////// XML FUNKCIE /////////////////
// Vypis hlavicky XML a nastavenie odsadenia
function writeXmlHead()
{
    global $xml;
    xmlwriter_set_indent($xml, true);
    xmlwriter_set_indent_string($xml, '    ');
    xmlwriter_start_document($xml, '1.0', 'utf-8');
    xmlwriter_start_element($xml, 'program');
    xmlwriter_start_attribute($xml, 'language');
    xmlwriter_text($xml, 'IPPcode20');
    xmlwriter_end_attribute($xml);
}

// Vypis argumentov XML
function writeXmlArg($word, $type) {
    global $xml, $arg_order;
    xmlwriter_start_element($xml, 'arg' . $arg_order);
    xmlwriter_start_attribute($xml, 'type');
    xmlwriter_text($xml, $type);
    xmlwriter_end_attribute($xml);
    xmlwriter_text($xml, $word);
    xmlwriter_end_element($xml);
    $arg_order++;
}

// Vypis napovedy
function writeHelp() {
    echo "Vitajte! Toto je stručná nápoveda k jazyku IPPcode20:\n";
    echo "parse.php je program na kontrolu syntaktickej a lexikalnej správnosti programu.\n\n";
    echo "Program sa môže spustiť s následujúcim parametrom:\n";
    echo "  --help (-h): Výpis nápovedy\n\n";
    echo "Program načíta zo štandartného vstupu program v IPPcode20.\n";
    echo "Na štandartný výstup sa vypisuje XML výpis ak kontrola programu prebehla v poriadku.\n";
    echo "Pre viac informácii navvšitvte web: \n";
    exit(0);

}

///////////////// FUNKCIE LEXIKALNEJ, SYNTAKTICKEJ KONTROLY /////////////////
// Kontrola ci je nazov var napisany spravne
function checkVarName($word, $isint)
{
    $word = str_split($word);
    foreach ($word as $c)
    {
            if (preg_match('/^[a-zA-Z0-9]+$/', $c) === 1) {
                continue;
            } elseif (strpbrk($c, '_-$&%*!?')) {
                continue;
            } elseif ($isint) {
                if ($c == '+') {
                    continue;
                }
                else writeErr(erLS);
            } else writeErr(erLS);
    }
    return 0;
}

// Kontrola ci je var napisany spravne
function checkVar($word)
{
    // kontrola ramca
    if (($word[0] == 'L') || ($word[0] == 'T') || ($word[0] == 'G')) {
        if ($word[1] == 'F') {
            if ($word[2] == '@') {
                $namevar = strstr($word, '@');
                $namevar = substr($namevar, 1);
            } else writeErr(erLS);
        } else writeErr(erLS);
    } else writeErr(erLS);

    //kontrola ci je premenna napisana spravne
    if (preg_match('/^\d/', $namevar) !== 1) {

        checkVarName($namevar, false);

    } else writeErr(erLS);

    writeXmlArg($word, "var");
    return 0;
}

// Kontrola ci je symb napisany spravne
function checkSymb($word)
{
    if ($type = strstr($word, '@', true)) {
        if (strcmp($type, "string") == 0) {
            $word = strstr($word, '@');
            $word = substr($word, 1);
            if (preg_match('/^(\\\\[0-9]{3}|[^\\\\])*$/', $word)) {

                writeXmlArg($word, "string");

            } else writeErr(erLS);
            return 0;
        }
        elseif (strcmp($type, "int") == 0) {
            $word = strstr($word, '@');
            $word = substr($word, 1);
            checkVarName($word, true);
            writeXmlArg($word, "int");
            return 0;
        }
        elseif (strcmp($type, "bool") == 0) {
            $word = strstr($word, '@');
            $word = substr($word, 1);
            if ((strcmp($word, "true") == 0) || (strcmp($word, "false") == 0)) {

                writeXmlArg($word, "bool");
            } else writeErr(erLS);
            return 0;
        }
        elseif (strcmp($type, "nil") == 0) {
            $word = strstr($word, '@');
            $word = substr($word, 1);
            if (strcmp($word, "nil") == 0) {

                writeXmlArg($word, "nil");
            } else writeErr(erLS);
            return 0;
        }
	    else checkVar($word);

    } else writeErr(erLS);
    return 0;
}

// Kontrola ci je label napisany spravne
function checkLab($word) {
    if (preg_match('/^\d/', $word) !== 1) {

        checkVarName($word, false);
        writeXmlArg($word, "label");

    } else writeErr(erLS);

    return 0;
}

// Kontrola ci je type napisany spravne
function checkType($word) {
    if ((strcmp($word, "string") == 0) || (strcmp($word, "bool") == 0) || (strcmp($word, "int") == 0)) {
        writeXmlArg($word, "type");
    } else writeErr(erLS);

    return 0;
}

// Kontrola ci pocet parametrov instrukcie sedi
function checkPar($params, $opCount) {
    if (count($params) == $opCount) {
        return 0;
    }
    else writeErr(erLS);
    return 0;
}

// Dekoder instrukcie: kontrola operacnych kodov, a nasledna kontrola ich argumentov
function instDec($words)
{
    if ((strcmp($words[0],"CREATEFRAME") == 0) || (strcmp($words[0],"PUSHFRAME") == 0) || (strcmp($words[0],"POPFRAME") == 0) || (strcmp($words[0],"RETURN") == 0) || (strcmp($words[0],"BREAK") == 0)) {
        checkPar($words, 1);
    }
    elseif ((strcmp($words[0], "DEFVAR") == 0) || (strcmp($words[0], "POPS") == 0)) {
        checkPar($words, 2);
        checkVar($words[1]);
    }
    elseif ((strcmp($words[0], "PUSHS") == 0) || (strcmp($words[0], "WRITE") == 0) || (strcmp($words[0], "EXIT") == 0) || (strcmp($words[0], "DPRINT") == 0)) {
        checkPar($words, 2);
        checkSymb($words[1]);
    }
    elseif ((strcmp($words[0], "CALL") == 0) || (strcmp($words[0], "LABEL") == 0) || (strcmp($words[0], "JUMP") == 0)) {
        checkPar($words, 2);
        checkLab($words[1]);
    }
    elseif ((strcmp($words[0], "MOVE") == 0) || (strcmp($words[0], "INT2CHAR") == 0) || (strcmp($words[0], "STRLEN") == 0) || (strcmp($words[0], "TYPE") == 0) || (strcmp($words[0], "NOT") == 0)) {
        checkPar($words, 3);
        checkVar($words[1]);
        checkSymb($words[2]);
    }
    elseif (strcmp($words[0], "READ") == 0) {
        checkPar($words, 3);
        checkVar($words[1]);
        checkType($words[2]);
    }
    elseif ((strcmp($words[0], "ADD") == 0) || (strcmp($words[0], "SUB") == 0) || (strcmp($words[0], "MUL") == 0) || (strcmp($words[0], "IDIV") == 0) || (strcmp($words[0], "LT") == 0) ||
        (strcmp($words[0], "GT") == 0) || (strcmp($words[0], "EQ") == 0) || (strcmp($words[0], "AND") == 0) || (strcmp($words[0], "OR") == 0) ||
        (strcmp($words[0], "STRI2INT") == 0) || (strcmp($words[0], "CONCAT") == 0) || (strcmp($words[0], "GETCHAR") == 0) || (strcmp($words[0], "SETCHAR") == 0))
    {
        checkPar($words, 4);
        checkVar($words[1]);
        checkSymb($words[2]);
        checkSymb($words[3]);
    }
    elseif ((strcmp($words[0], "JUMPIFEQ") == 0) || (strcmp($words[0], "JUMPIFNEQ") == 0)) {
        checkPar($words, 4);
        checkLab($words[1]);
        checkSymb($words[2]);
        checkSymb($words[3]);
    }
    else writeErr(erOpcode);
    return 0;
}

///////////////// TELO PROGRAMU /////////////////
//kontrola argumentov
if ($argc == 2 )
{
    if ((strcmp($argv[1], "--help" ) == 0) || (strcmp($argv[1], "-h" ) == 0)) {
        writeHelp();
    }
    else {
        writeErr(erPar);
    }
}
if ($argc > 2) {
    writeErr(erPar);
}

//kontrola hlavicky programu
while($line = fgets(STDIN)) {
    if ($newline = strstr($line, '#', true)) { // odstrani cast komentara
        $line = $newline;
    }
    $line = ltrim($line); // odstrani biele znaky zlava
    $line = rtrim($line); // odstrani biele znaky sprava

    if (($line === '') || ($line[0] == '#')) { //ak je $line prazdny string alebo iba komentar ideme na dalsi riadok..
        continue;
    }
    $words = preg_split('/[\s]+/', $line); // rozdeli line na slova
    $words[0] = strtoupper($words[0]); // Nastavi hlavicku na velke pismena

    // Kontrola ci sa jedna o hlavicku
    if (strcmp($words[0], ".IPPCODE20") == 0)
        break;
    else
        writeErr(erHead);
}

//uvod do XML vystupu, XML hlavicka a pod.
$xml = xmlwriter_open_memory();
writeXmlHead();

//kontrola hlavneho programu
$arg_order = 1; // order argumentov
$order = 1; // order instrukcii v XML

while($line = fgets(STDIN)) {


    if ($newline = strstr($line, '#', true)) { // odstrani cast komentara
        $line = $newline;
    }
    $line = ltrim($line); // odstrani biele znaky zlava
    $line = rtrim($line); // odstrani biele znaky sprava

    if (($line === '')||($line[0] == '#')){ //ak je $line prazdny string alebo iba komentar ideme na dalsi riadok..
        continue;
    }
    $words = preg_split('/[\s]+/', $line); // rozdeli line na slova
    $words[0] = strtoupper ($words[0]); // vsetky znaky prveho slova(opcode) budu velkymi pismenami

    // Vypis instrukcie do XML
    xmlwriter_start_element($xml, 'instruction');
    xmlwriter_start_attribute($xml, 'order');
    xmlwriter_text($xml, $order);
    xmlwriter_start_attribute($xml, 'opcode');
    xmlwriter_text($xml, $words[0]);
    xmlwriter_end_attribute($xml);

    instDec($words);
    $order++; // poradie instrukcie sa zvysi o 1
    $arg_order = 1;

    xmlwriter_end_element($xml); //Koniec instrukcie
}

// Koniec programu, vypis XML
xmlwriter_end_element($xml);
xmlwriter_end_document($xml);
echo xmlwriter_output_memory($xml);

?>
