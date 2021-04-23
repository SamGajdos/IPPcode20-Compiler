"""
    IPP projekt č.2, súbor: interpret.py
    Autor: Samuel Gajdoš
    Rok: 2020
"""

import xml.etree.ElementTree as ET
import sys
import getopt
import re

"""Globálne premenné pre chybné výstupy."""
undefined = 404.404

erPar = 10
erStdin = 11
erStdout = 12
erFormXML = 31
erStructXML = 32
erSemantic = 52
erWrongOperandType = 53
erNonExistingVar = 54
erNonExistingFrame = 55
erMissingValue = 56
erWrongValue = 57
erWrongString = 58
erIntern = 99


def writeErr(errcode):
    """ Funckia pre chybný výpis a ukončenie programu."""

    errSwitcher = {
        erPar: "Chyba, zle zadaný alebo nesprávny počet parametrov programu.\nPre výpis nápovedy použite parameter '--help'.",
        erStdin: "Chyba pri otváraní vstupných súborov.",
        erStdout: "Chyba pri otváraní výstupných súborov pre zápis.",
        erFormXML: "Chybný formát vo vstupnom súbore XML.",
        erStructXML: "Chyba, neočakávaná štruktúra XML.",
        erSemantic: "Chyba sémantiky vstupného programu IPPcode20.",
        erWrongOperandType: "Chyba, nesprávne typy operandov.",
        erNonExistingVar: "Chyba, nedefinovaná premenná alebo náveštie.",
        erNonExistingFrame: "Chyba, rámec neexistuje.",
        erMissingValue: "Chyba, chýbajúca hodnota.",
        erWrongValue: "Chyba, nesprávna hodnota operandu.",
        erWrongString: "Chybná práca s reťazcom.",
        erIntern: "Interná chyba programu, ospravedlňujeme sa, skúste to ochvíľu neskôr."
    }
    try:
        sys.stderr.write(errSwitcher.get(errcode, None) + f" V {i + 1}. inštrukcii s názvom " + instructions[i].attrib[
            'opcode'] + ".\n")
    except:
        sys.stderr.write(errSwitcher.get(errcode, None) + "\n")
    sys.exit(errcode)


def printHelp():
    """Funkcia pre výpis nápovedy."""

    print("### Stručná nápoveda pre interpret jazyka IPPCode20 ###")
    print("Platné argumenty:")
    print("'--help': výpis nápovedy.")
    print("\n'--source=file': zo súboru 'file' načíta XML reprezentáciu zdrojového kódu.")
    print("Pri vynechaní tohto parametru program načíta XML reprezentáciu zo štandartného vstupu.")
    print("\n'--input=file': zo súboru 'file' načíta uživateľský vstup pre samotnú interpretáciu.")
    print("Pri vynechaní tohto parametru program načíta vstup pre interpretáciu zo štandartného vstupu.")
    print("\n'--stats=file': do súboru 'file' zapíše štatistiku behu programu.")
    print("'--insts': do stats. súboru zapíše celkový počet vykonaných inštrukcií.")
    print("'--vars': do stats. súboru zapíše maximálny počet premenných použitých v programe.")
    print("Pri použití '--inst' alebo '--vars' nesmie chýbať parameter '--stats=file'")


class String:
    """ Trieda pre niektoré inštrukcie pre spracovávanie reťazcov."""

    def __init__(self, instruction):
        value1 = checkSymb(instruction[1])
        value2 = checkSymb(instruction[2])

        if value1 == undefined or value2 == undefined:
            writeErr(erMissingValue)

        if isinstance(value1, int) and not isinstance(value1, bool):
            self.type1 = 'int'
        elif isinstance(value1, str):
            self.type1 = 'str'
        else:
            writeErr(erWrongOperandType)

        if isinstance(value2, int) and not isinstance(value2, bool):
            self.type2 = 'int'
        elif isinstance(value2, str):
            self.type2 = 'str'
        else:
            writeErr(erWrongOperandType)

        self.symb1 = value1
        self.symb2 = value2

    def stri2int(self):
        if self.type1 == 'str' and self.type2 == 'int':

            if 0 <= self.symb2 < len(self.symb1):
                char = self.symb1[self.symb2]
                return ord(char)
            else:
                writeErr(erWrongString)
        else:
            writeErr(erWrongOperandType)

    def concat(self):
        if self.type1 == 'str' and self.type2 == 'str':

            return self.symb1 + self.symb2
        else:
            writeErr(erWrongOperandType)

    def getchar(self):
        if self.type1 == 'str' and self.type2 == 'int':
            if 0 <= self.symb2 < len(self.symb1):
                return self.symb1[self.symb2]
            else:
                writeErr(erWrongString)
        else:
            writeErr(erWrongOperandType)


class Not:
    """Trieda pre inštrukciu Not."""

    def __init__(self, instruction):
        value1 = checkSymb(instruction[1])

        if value1 == undefined:
            writeErr(erMissingValue)

        if isinstance(value1, bool):
            self.type = 'bool'
        else:
            writeErr(erWrongOperandType)

        self.symb1 = value1

    def nott(self):
        return not self.symb1


class Arithmetic:
    """Trieda pre aritmetické inštrukcie, ktoré majú 2 argumenty."""

    def __init__(self, instruction):
        value1 = checkSymb(instruction[1])
        value2 = checkSymb(instruction[2])

        if value1 == undefined or value2 == undefined:
            writeErr(erMissingValue)

        if isinstance(value1, int) and not isinstance(value1, bool) and \
                isinstance(value2, int) and not isinstance(value2, bool):
            self.type = 'int'
        elif isinstance(value1, bool) and isinstance(value2, bool):
            self.type = 'bool'
        elif isinstance(value1, str) and isinstance(value2, str):
            self.type = 'str'
        elif value1 == None or value2 == None:
            self.type = 'nil'
        else:
            writeErr(erWrongOperandType)

        self.symb1 = value1
        self.symb2 = value2

    def add(self):
        if self.type == 'int':
            return self.symb1 + self.symb2
        else:
            writeErr(erWrongOperandType)

    def sub(self):
        if self.type == 'int':
            return self.symb1 - self.symb2
        else:
            writeErr(erWrongOperandType)

    def mul(self):
        if self.type == 'int':
            return self.symb1 * self.symb2
        else:
            writeErr(erWrongOperandType)

    def idiv(self):
        if self.type == 'int':
            try:
                return self.symb1 // self.symb2
            except:
                writeErr(erWrongValue)
        else:
            writeErr(erWrongOperandType)

    def lt(self):
        if self.type == 'int':
            return self.symb1 < self.symb2
        elif self.type == 'bool':
            return self.symb1 is False and self.symb2 is True
        elif self.type == 'str':
            return len(self.symb1) < len(self.symb2)
        else:
            writeErr(erWrongOperandType)

    def gt(self):
        if self.type == 'int':
            return self.symb1 > self.symb2
        elif self.type == 'bool':
            return self.symb1 is True and self.symb2 is False
        elif self.type == 'str':
            return len(self.symb1) > len(self.symb2)
        else:
            writeErr(erWrongOperandType)

    def eq(self):

        if self.type == 'int':
            return self.symb1 == self.symb2
        elif self.type == 'bool':
            return self.symb1 == self.symb2
        elif self.type == 'str':
            return self.symb1 == self.symb2
        elif self.type == 'nil':
            return self.symb1 == self.symb2  # ak je aspon jeden oparand nil tak False, ak oba su nil tak True

    def andd(self):
        if self.type == 'bool':
            return self.symb1 and self.symb2
        else:
            writeErr(erWrongOperandType)

    def orr(self):
        if self.type == 'bool':
            return self.symb1 or self.symb2
        else:
            writeErr(erWrongOperandType)


class Stack:
    """ Trieda pre ADT zásobník, využitie: dátový zásobník, zásobník rámcov, zásobník volaní inšt. CALL."""

    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def top(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


def checkArgs(instruction, number):
    """ Funkcia skontroluje či má inštruckia správny počet argumentov a v spárvnom tvare a zoradí ich."""

    if len(instruction) != number:
        writeErr(erStructXML)

    instruction[:] = sorted(instruction, key=lambda child: (child.tag))

    j = 1
    for child in instruction:
        if child.tag[:3] != 'arg':
            writeErr(erStructXML)

        if child.tag[3] == str(j):
            j += 1
        else:
            writeErr(erStructXML)



def checkString(string):
    """ Funkcia skontroluje daný string, dekóduje escape sekvencie, v prípade None vráti prázdny string."""

    if string is None:
        return ''

    # Kontrola so znakmi s diaktritikou
    fail_group = re.findall(r"\\[0-9]{0,2}", string) and not re.findall(r"\\[0-9]{3}", string)

    if fail_group:
        writeErr(erStructXML)

    group = re.findall(r"\\([0-9]{3})", string)

    for match in group:
        string = re.sub("\\\\{0}".format(match), chr(int(match)), string)

    return string


def checkType(type):
    """Funkcia skontroluje správne napísaný type v XML."""

    if 'type' in type.attrib:
        if type.attrib['type'] == 'type':
            return type.text
        else:
            writeErr(erStructXML)
    else:
        writeErr(erStructXML)


def checkLabel(label):
    """Funkcia skontroluje správne napísaný label v XML."""

    if 'type' in label.attrib:
        if label.attrib['type'] == 'label':

            for c in label.text:
                if not re.match(r"[a-z,A-Z,0-9,_,$,&,%,*,!,?,\-]", c):
                    writeErr(erStructXML)

            if re.findall(r"\d", label.text[0]):
                writeErr(erStructXML)
            else:
                return label.text
        else:
            writeErr(erStructXML)
    else:
        writeErr(erStructXML)


def checkVarInFrame(var, frame):
    """ Funkcia skontroluje či sa premenná nachádza v rámci. Vracia hodnotu premennej."""

    varname = var.text[3:]

    if varname in frame:
        return frame[varname]
    else:
        writeErr(erNonExistingVar)


def checkVar(var):
    """ Funkcia skontroluje správny zápis premennej. Vracia rámec, kde sa údajne nachádza."""

    frame = None
    if 'type' in var.attrib:
        if var.attrib['type'] == 'var':
            name = var.text
            if name[0:3] == 'GF@':
                frame = GF
            elif name[0:3] == 'LF@':
                frame = LF
            elif name[0:3] == 'TF@':
                frame = TF
            else:
                writeErr(erStructXML)
        else:
            writeErr(erStructXML)
    else:
        writeErr(erStructXML)

    varname = var.text[3:]
    for c in varname:
       if not re.match(r"[a-z,A-Z,0-9,_,$,&,%,*,!,?,\-]",c):
           writeErr(erStructXML)

    if re.findall(r"\d", varname[0]):
        writeErr(erStructXML)

    if frame is not None:
        return frame
    else:
        writeErr(erNonExistingFrame)


def checkSymb(symb):
    """ Funkcia skontroluje správny zápis symbolu. Vracia jeho hodnotu."""

    if 'type' in symb.attrib:

        if symb.text is not None:
            if set('\n\t #').intersection(symb.text):
                writeErr(erStructXML)

        if symb.attrib['type'] == 'string':
            return checkString(symb.text)
        elif symb.attrib['type'] == 'int':
            try:
                return int(symb.text)
            except:
                writeErr(erSemantic)
        elif symb.attrib['type'] == 'bool':
            if symb.text == 'true':
                return True
            if symb.text == 'false':
                return False
            else:
                writeErr(erSemantic)
        elif symb.attrib['type'] == 'nil':
            return None

        elif symb.attrib['type'] == 'var':
            frame = checkVar(symb)
            return checkVarInFrame(symb, frame)
        else:
            writeErr(erStructXML)

    else:
        writeErr(erStructXML)


def instMOVE(instruction):
    checkArgs(instruction, 2)
    frame = checkVar(instruction[0])
    varName = instruction[0].text[3:]
    symb = checkSymb(instruction[1])
    if symb is undefined:
        writeErr(erMissingValue)

    if varName in frame:
        frame[varName] = symb
    else:
        writeErr(erNonExistingVar)


def instCREATEFRAME(instruction):
    checkArgs(instruction, 0)

    global TF
    TF = {}


def instPUSHFRAME(instruction):
    checkArgs(instruction, 0)

    global stackLF, LF, TF
    if TF is not None:
        stackLF.push(TF)
    else:
        writeErr(erNonExistingFrame)

    LF = stackLF.top()
    TF = None


def instPOPFRAME(instruction):
    checkArgs(instruction, 0)

    global stackLF, LF, TF

    if stackLF.isEmpty():
        writeErr(erNonExistingFrame)
    TF = stackLF.top()
    stackLF.pop()

    if not stackLF.isEmpty():
        LF = stackLF.top()
    else:
        LF = None


def instCALL(instruction):
    checkArgs(instruction, 1)

    global stackCall, i
    label = checkLabel(instruction[0])
    if label in LBL:
        stackCall.push(i)
        i = LBL[label]
    else:
        writeErr(erSemantic)


def instRETURN(instruction):
    checkArgs(instruction, 0)

    global stackCall, i
    if stackCall.isEmpty():
        writeErr(erMissingValue)
    else:
        i = stackCall.top()
        stackCall.pop()


def instDEFVAR(instruction):
    global var_counter
    checkArgs(instruction, 1)
    frame = checkVar(instruction[0])
    varName = instruction[0].text[3:]

    if varName in frame:
        writeErr(erSemantic)
    else:
        try:
            frame[varName] = undefined
        except:
            writeErr(erIntern)
    var_counter += 1


def instPUSHS(instruction):
    checkArgs(instruction, 1)
    symb = checkSymb(instruction[0])
    if symb is undefined:
        writeErr(erMissingValue)
    try:
        stackData.push(symb)
    except:
        writeErr(erIntern)


def instPOPS(instruction):
    checkArgs(instruction, 1)
    if stackData.isEmpty():
        writeErr(erMissingValue)

    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]

    frame[varName] = stackData.top()
    stackData.pop()


def instArithmetic(instruction, instStr):
    """Funkcia vytvorí objekt triedy Arithmetic, ktorý následne vykoná danú inštrukciu."""

    checkArgs(instruction, 3)
    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    arObj = Arithmetic(instruction)

    if instStr == 'ADD':
        frame[varName] = arObj.add()
    elif instStr == 'SUB':
        frame[varName] = arObj.sub()
    elif instStr == 'MUL':
        frame[varName] = arObj.mul()
    elif instStr == 'IDIV':
        frame[varName] = arObj.idiv()
    elif instStr == 'LT':
        frame[varName] = arObj.lt()
    elif instStr == 'GT':
        frame[varName] = arObj.gt()
    elif instStr == 'EQ':
        frame[varName] = arObj.eq()
    elif instStr == 'AND':
        frame[varName] = arObj.andd()
    elif instStr == 'OR':
        frame[varName] = arObj.orr()
    else:
        writeErr(erStructXML)


def instNOT(instruction):
    """Funkcia vytvorí objekt triedy Not, ktorý následne vykoná inštrukciu NOT."""

    checkArgs(instruction, 2)
    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    notObj = Not(instruction)
    frame[varName] = notObj.nott()


def instString(instruction, instStr):
    """Funkcia vytvorí objekt triedy String, ktorý následne vykoná danú inštrukciu."""

    checkArgs(instruction, 3)
    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    strObj = String(instruction)

    if instStr == 'CONCAT':
        frame[varName] = strObj.concat()
    elif instStr == 'GETCHAR':
        frame[varName] = strObj.getchar()
    elif instStr == 'STRI2INT':
        frame[varName] = strObj.stri2int()
    else:
        writeErr(erStructXML)


def instSETCHAR(instruction):
    checkArgs(instruction, 3)

    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    var = frame[varName]
    symb1 = checkSymb(instruction[1])
    symb2 = checkSymb(instruction[2])

    if var == undefined or symb1 == undefined or symb2 == undefined:
        writeErr(erMissingValue)

    if symb2 == '':
        writeErr(erWrongString)

    if isinstance(var, str) and isinstance(symb1, int) and not isinstance(symb1, bool) and isinstance(symb2, str):

        if 0 <= symb1 < len(var):
            var = var[:symb1] + symb2[0] + var[symb1 + 1:]
            frame[varName] = var
        else:
            writeErr(erWrongString)
    else:
        writeErr(erWrongOperandType)


def instSTRLEN(instruction):
    checkArgs(instruction, 2)

    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    symb = checkSymb(instruction[1])

    if symb == undefined:
        writeErr(erMissingValue)
    if isinstance(symb, str):
        try:
            frame[varName] = len(symb)
        except:
            writeErr(erWrongString)
    else:
        writeErr(erWrongOperandType)


def instINT2CHAR(instruction):
    checkArgs(instruction, 2)

    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    symb = checkSymb(instruction[1])
    char = ''
    if symb == undefined:
        writeErr(erMissingValue)
    if isinstance(symb, int) and not isinstance(symb, bool):
        try:
            char = chr(symb)
        except:
            writeErr(erWrongString)
    else:
        writeErr(erWrongOperandType)

    frame[varName] = char


def instTYPE(instruction):
    checkArgs(instruction, 2)

    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    symb = checkSymb(instruction[1])

    if isinstance(symb, int) and not isinstance(symb, bool):
        frame[varName] = 'int'
    elif isinstance(symb, bool):
        frame[varName] = 'bool'
    elif isinstance(symb, str):
        frame[varName] = 'string'
    elif symb is None:
        frame[varName] = 'nil'
    elif symb == undefined:
        frame[varName] = ''


def instREAD(instruction):
    checkArgs(instruction, 2)
    frame = checkVar(instruction[0])
    checkVarInFrame(instruction[0], frame)
    varName = instruction[0].text[3:]
    type = checkType(instruction[1])

    sys.stdin = user_input
    try:
        read_input = input()
    except:
        frame[varName] = None
        return

    if read_input is None or read_input=='':  # V pripade neplatneho. vstupu z terminalu
        frame[varName] = None
        return

    if type == 'int':
        try:
            frame[varName] = int(read_input)
        except:
            frame[varName] = None
    elif type == 'string':
        frame[varName] = read_input
    elif type == 'bool':
        if read_input.lower() == 'true':
            frame[varName] = True
        else:
            frame[varName] = False
    else:
        writeErr(erStructXML)


def instWRITE(instruction):
    checkArgs(instruction, 1)
    symb = checkSymb(instruction[0])

    if isinstance(symb, int) and not isinstance(symb, bool):
        print(str(symb), end='')
    elif isinstance(symb, bool):
        if symb is True:
            print('true', end='')
        else:
            print('false', end='')
    elif isinstance(symb, str):
        print(symb, end='')
    elif symb is None:
        print('', end='')
    elif symb == undefined:
        writeErr(erMissingValue)


def instLABEL(instruction):
    checkArgs(instruction, 1)

    global LBL
    label = checkLabel(instruction[0])
    if label in LBL:
        writeErr(erSemantic)
    else:
        LBL[label] = i - 1   # i sa na konci cyklu zvacsi o 1, preto davame i-1


def instJUMP(instruction):
    checkArgs(instruction, 1)

    global LBL, i
    label = checkLabel(instruction[0])
    if label in LBL:
        i = LBL[label]
    else:
        writeErr(erSemantic)


def instJUMPIFEQ(instruction):
    checkArgs(instruction, 3)
    arObj = Arithmetic(instruction)

    global LBL, i
    label = checkLabel(instruction[0])
    if label in LBL:
        if arObj.eq():
            i = LBL[label]
    else:
        writeErr(erSemantic)


def instJUMPIFNEQ(instruction):
    checkArgs(instruction, 3)
    arObj = Arithmetic(instruction)

    global LBL, i
    label = checkLabel(instruction[0])
    if label in LBL:
        if not arObj.eq():
            i = LBL[label]
    else:
        writeErr(erSemantic)


def instEXIT(instruction):
    checkArgs(instruction, 1)
    symb = checkSymb(instruction[0])

    if symb == undefined:
        writeErr(erMissingValue)

    if isinstance(symb, int) and not isinstance(symb, bool):
        if symb >= 0 and symb <= 49:
            sys.exit(symb)
        else:
            writeErr(erWrongValue)
    else:
        writeErr(erWrongOperandType)


def instDPRINT(instruction):
    checkArgs(instruction, 1)
    symb = checkSymb(instruction[0])

    if isinstance(symb, int) and not isinstance(symb, bool):
        sys.stderr.write(str(symb))
    elif isinstance(symb, bool):
        if symb is True:
            sys.stderr.write('true')
        else:
            sys.stderr.write('false')
    elif isinstance(symb, str):
        sys.stderr.write(symb)
    elif symb is None:
        sys.stderr.write('')
    elif symb == undefined:
        writeErr(erMissingValue)


def instBREAK(instruction):
    checkArgs(instruction, 0)

    # Pre vypis hodnot z Python zapisu do zapisu IPPCode20
    value_switcher = {
        None: "nil",
        True: "true",
        False: "false",
        404.404: "'undefined'"
    }

    sys.stderr.write('\nPočet vykonaných inštrukcií: ' + str(inst_counter) + "\n")
    sys.stderr.write('\nObsah rámca GF v tvare [názov_premennej] => [hodnota]:\n')

    for item in GF:
        value = value_switcher.get(GF.get(item))
        if value is None:
            value = GF.get(item)

        sys.stderr.write(item + ' => ' + str(value) + '\n')

    if TF is None:
        sys.stderr.write('\nObsah rámca TF je prázdny.\n')
    else:
        sys.stderr.write('\nObsah rámca TF v tvare [názov_premennej] => [hodnota]:\n')

        for item in TF:
            value = value_switcher.get(TF.get(item))
            if value is None:
                value = TF.get(item)

            sys.stderr.write(item + ' => ' + str(value) + '\n')


    if LF is None:
        sys.stderr.write('\nObsah rámca LF je prázdny.\n')
    else:
        sys.stderr.write('\nObsah rámca LF v tvare [názov_premennej] => [hodnota]:\n')
        for item in LF:
            value = value_switcher.get(LF.get(item))
            if value is None:
                value = LF.get(item)
            sys.stderr.write(item + ' => ' + str(value) + '\n')

    sys.stderr.write('Počet LF v zásobníku: ' + str(stackLF.size()) + "\n")


def opCodeParse(instruction):
    """Funkcia pre Analýzu inštrukcií a ich následné vykonanie."""

    try:
        opcode = instruction.attrib['opcode'].upper()
    except:
        writeErr(erStructXML)

    if opcode == 'MOVE':
        instMOVE(instruction)
    elif opcode == 'CREATEFRAME':
        instCREATEFRAME(instruction)
    elif opcode == 'PUSHFRAME':
        instPUSHFRAME(instruction)
    elif opcode == 'POPFRAME':
        instPOPFRAME(instruction)
    elif opcode == 'DEFVAR':
        instDEFVAR(instruction)
    elif opcode == 'CALL':
        instCALL(instruction)
    elif opcode == 'RETURN':
        instRETURN(instruction)
    elif opcode == 'PUSHS':
        instPUSHS(instruction)
    elif opcode == 'POPS':
        instPOPS(instruction)
    elif opcode == 'ADD':
        instArithmetic(instruction, 'ADD')
    elif opcode == 'SUB':
        instArithmetic(instruction, 'SUB')
    elif opcode == 'MUL':
        instArithmetic(instruction, 'MUL')
    elif opcode == 'IDIV':
        instArithmetic(instruction, 'IDIV')
    elif opcode == 'LT':
        instArithmetic(instruction, 'LT')
    elif opcode == 'GT':
        instArithmetic(instruction, 'GT')
    elif opcode == 'EQ':
        instArithmetic(instruction, 'EQ')
    elif opcode == 'AND':
        instArithmetic(instruction, 'AND')
    elif opcode == 'OR':
        instArithmetic(instruction, 'OR')
    elif opcode == 'NOT':
        instNOT(instruction)
    elif opcode == 'INT2CHAR':
        instINT2CHAR(instruction)
    elif opcode == 'STRI2INT':
        instString(instruction, 'STRI2INT')
    elif opcode == 'READ':
        instREAD(instruction)
    elif opcode == 'WRITE':
        instWRITE(instruction)
    elif opcode == 'CONCAT':
        instString(instruction, 'CONCAT')
    elif opcode == 'STRLEN':
        instSTRLEN(instruction)
    elif opcode == 'GETCHAR':
        instString(instruction, 'GETCHAR')
    elif opcode == 'SETCHAR':
        instSETCHAR(instruction)
    elif opcode == 'TYPE':
        instTYPE(instruction)
    elif opcode == 'LABEL':
        return
    elif opcode == 'JUMP':
        instJUMP(instruction)
    elif opcode == 'JUMPIFEQ':
        instJUMPIFEQ(instruction)
    elif opcode == 'JUMPIFNEQ':
        instJUMPIFNEQ(instruction)
    elif opcode == 'EXIT':
        instEXIT(instruction)
    elif opcode == 'DPRINT':
        instDPRINT(instruction)
    elif opcode == 'BREAK':
        instBREAK(instruction)
    else:
        writeErr(erStructXML)


###################### HLAVNÉ TELO PROGRAMU. ######################
################### Spracovávanie argumentov. ###################
try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "source=", "input=", "stats=", "vars", "insts"])
except getopt.GetoptError as err:
    writeErr(erPar)

# V pripade nečakaných, nesprávnych argumentov.
if args:
    writeErr(erPar)

# slovnik si v poradi uklada poradie parametrov k stats.
stats_order = []

source = None
user_input_file = None
stats = None
insts = False
vars = False
for o, file in opts:
    if o in ("", "--help"):
        printHelp()
        sys.exit(0)
    elif o in ("", "--source"):
        source = file
    elif o in ("", "--input"):
        user_input_file = file
    elif o in ("", "--stats"):
        stats = file
    elif o in ("", "--insts"):
        insts = True
        stats_order.append("insts")
    elif o in ("", "--vars"):
        vars = True
        stats_order.append("vars")
    else:
        writeErr(erPar)

if user_input_file is None and source is None:
    writeErr(erPar)

if source is not None:
    pass
else:
    source = sys.stdin

if user_input_file is not None:
    try:
        user_input = open(user_input_file, "r")
    except:
        writeErr(erStdin)

else:
    user_input = sys.stdin

if vars is True or insts is True:
    if stats is not None:
        try:
            stats = open(stats, "w")
        except:
            writeErr(erPar)
    else:
        writeErr(erPar)

################### Analýza/parsing XML formátu. ###################
try:
    tree = ET.parse(source)
except IOError:
    writeErr(erStdin)
except ET.ParseError:
    writeErr(erFormXML)

root = tree.getroot()

# Kontrola elementu program v XML vstupe
try:
    root.tag == 'program' and root.attrib['language'].upper() == 'IPPCODE20'
except:
    writeErr(erStructXML)

for key in root.attrib.keys():
    if key != 'name' and key != 'description' and key != 'language':
        writeErr(erStructXML)

# Zoradenie instrukcii pomocou atributu 'order'
try:
    root[:] = sorted(root, key=lambda child: (int(child.get('order'))))
except:
    writeErr(erStructXML)

#### Inicializácia Label slovníku ####
LBL = {}

# Pole referencií na inšturkcie programu IPPCode v XML formáte.
instructions = []
i = 0
previous_order = 0
for child in root:
    # print(child.tag, child.attrib)

    if child.tag != 'instruction' and len(child.attrib.keys()) == 2:
        writeErr(erStructXML)

    for key in child.attrib.keys():
        if key == 'order':
            try:
                actual_order = int(child.attrib['order'])
            except:
                writeErr(erStructXML)

            # ak sa poradie order opakuje alebo je mensie ako 1
            if actual_order == previous_order or actual_order < 1:
                writeErr(erStructXML)
            else:
                previous_order = actual_order

        elif key == 'opcode':
            if child.attrib['opcode'].upper() == 'LABEL':
                instLABEL(child)
        else:
            writeErr(erStructXML)

    instructions.append(child)
    i += 1

# Počet inštrukcií programu.
programLength = (len(instructions))

################### Inicializácie ###################
#### Inicializácia rámcov ####
GF = {}
TF = None
# Zásobník lokálnych rámcov.
stackLF = Stack()
LF = None

#### Inicializácia dátového zásobníku ####
stackData = Stack()

#### Inicializácia Call zásobníku ####
stackCall = Stack()

##############################################################
# Hlavný cyklus programu, číta inštrukcie podľa atribútu order.
# i -> iterativná premenná, mení sa na základe behu programu.
i = 0
inst_counter = 0  # pocitac instrukcii pre DPRINT a stats
var_counter = 0  # pocitac vsetkych premennych pre stats
while i < programLength:
    opCodeParse(instructions[i])
    i += 1
    inst_counter += 1

if stats is not None:
    for parameter in stats_order:
        if parameter == "insts":
            stats.write(str(inst_counter) + "\n")
        if parameter == "vars":
            stats.write(str(var_counter) + "\n")
