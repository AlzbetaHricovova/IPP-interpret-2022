import argument as ar
import xml.etree.ElementTree as ET
import sys
from collections import deque, OrderedDict

#Alžbeta Hricovová, xhrico00

GF = {}
deque = deque()

#sort list podľa order
def my_sort(item):
    return int(item.attrib['order'])

#kontrola, či je to var a rozdelenie podľa @
def var_control(instruction):
    if (instruction.attrib['type'] != 'var'):
        exit(53)
    var = instruction.text
    return var.split("@")

#kontrola, či je var definovaná v GF
def GF_control_initialized(var):
    if (var[1] not in GF):
        exit(54)
    if (GF[var[1]] == None):
        exit(56)

#kontrola, či je var deklarovaná v GF
def GF_control(var):
    if (var[1] not in GF):
        exit(54)

#return string_číslo na int hodnotu
def number_to_decimal(value):
    if ('x' in value.text or 'X' in value.text):
        number = int(value.text, base=16)
    elif (value.text[0] == '0' or ((value.text[0] == '+' or value.text[0] == '-') and value.text[1] == '0')):
        number = int(value.text, base=8)
    else:
        number = int(value.text)
    return number

#určenie bool hodnoty
def bool(value):
    value = value.text.lower()
    if (value != 'true'):
        value = False
    else:
        value = True
    return value

#prevod stringu na hodnotu podľa typu
def typing(arg):
    if (arg.type == 'int'):
        return number_to_decimal(arg)
    elif (arg.type == 'bool'):
        return bool(arg)
    else:
        return arg.text

#pops inštrukcia
def pops(instruction):
    if (deque == ()):
        exit(56)
    var = var_control(instruction[0])
    if (var[0] == 'GF'):            # LF a TF
        GF_control(var)
        GF[var[1]] = deque.pop()

#defvar inštrukcia
def defvar(instruction):
    var = var_control(instruction[0])
    if (var[0] == 'GF'):            # LF a TF
        if (var[1] in GF):
            exit(52)
        GF[var[1]] = None

#write inštrukcia
def write(instruction):
    if (instruction[0].attrib['type'] not in ['var', 'string', 'int', 'bool', 'nil']):
        exit(53)
    if (instruction[0].attrib['type'] == 'nil'):
        print('', end='')
    elif (instruction[0].attrib['type'] == 'var'):
        symb = instruction[0].text
        symb = symb.split("@")
        if (symb[0] == 'GF'):
            GF_control_initialized(symb)
            if (GF[symb[1]].type == 'nil'):
                print('', end='')
            else:
                print(GF[symb[1]].text, end='')      # LF a TF

    else:
        print(instruction[0].text, end='')

#read inštrukcia
def read(instruction):
    if(inputFile != None):
        try:
            f = open(inputFile, "r")
            value = f.readline()
        except EOFError:
            value = 'nil'

    else:
        value = input()
    if(value == '' or value == 'nil'):
        value = 'nil'
        type = 'nil'
    else:
        type = instruction[1].text.lower()
        if (instruction[1].attrib['type'] != 'type'):
            exit(53)
            if (type not in ['bool', 'int', 'string']):
                exit(57)
        if (type == 'bool'):
            value = value.lower()
            if (value != 'true'):
                value = 'false'
        elif (type == 'int'):
            arg = ar.Argument('int', value)
            try:
                number_to_decimal(arg)
            except ValueError:
                value = 'nil'
                type = 'nil'

    var = var_control(instruction[0])
    if (var[0] == 'GF'):                # LF a TF
        GF_control(var)
        GF[var[1]] = ar.Argument(type, value)

#int2char inštrukcia
def int2char(instruction):
    if (instruction[1].attrib['type'] not in ['var', 'int']):
        exit(53)
    if (instruction[1].attrib['type'] == 'var'):
        var2 = var_control(instruction[1])
        if (var2[0] == 'GF'):            # LF a TF
            GF_control_initialized(var2)
            value = GF[var2[1]]
            if (value.type != 'int'):
                exit(53)
        else:
            return

    else:
        value = ar.Argument('int', instruction[1].text)
    number = number_to_decimal(value)
    if (number < 0 or number > 1114111):
        exit(58)
    var1 = var_control(instruction[0])
    if (var1[0] == 'GF'):                # LF a TF
        GF_control(var1)
        GF[var1[1]] = ar.Argument('string', chr(number))

#stri2int inštrukcia
def stri2int(instruction):
    var = var_control(instruction[0])
    arg1 = symbol(instruction[1], 'string')
    value = symbol(instruction[2], 'int')

    number = number_to_decimal(value)
    if (number > len(arg1.text) - 1 or number < 0):
        exit(58)
    if (var[0] == 'GF'):                # LF a TF
        GF_control(var)
        num =ord(arg1.text[number])
        num = str(num)
        GF[var[1]] = ar.Argument('int', num)

#súčet
def add(n1, n2):
    return n1 + n2

#rozdiel
def sub(n1, n2):
    return n1 - n2

#násobenie
def mul(n1, n2):
    return n1 * n2

#delenie
def idiv(n1, n2):
    if (n2 == 0):
        exit(57)
    return n1 // n2

#inštrukcie add, sub, mul, idiv, and, or, not
def aritmetic(instruction, op_code, type, do_number, is_not_not):
    var = var_control(instruction[0])
    arg1 = symbol(instruction[1], type)

    if (is_not_not):
        arg2 = symbol(instruction[2], type)

    if (do_number):
        number1 = number_to_decimal(arg1)
        number2 = number_to_decimal(arg2)
    if (op_code == 'add'):
        result = add(number1, number2)
    elif (op_code == 'sub'):
        result = sub(number1, number2)
    elif (op_code == 'mul'):
        result = mul(number1, number2)
    elif (op_code == 'idiv'):
        result = idiv(number1, number2)
    elif (op_code == 'and'):
        value1 = bool(arg1)
        value2 = bool(arg2)
        result = value1 and value2
    elif (op_code == 'or'):
        value1 = bool(arg1)
        value2 = bool(arg2)
        result = value1 or value2
    else:
        result = not (bool(arg1))
    if (var[0] == 'GF'):        # LF a TF
        GF_control(var)
        GF[var[1]] = ar.Argument(type, str(result))

#inštrukcie qt, lt, eq
def args_for_compare(instruction, op_code):
    if (instruction[1].attrib['type'] in ['int', 'bool', 'string', 'nil']):
        arg1 = ar.Argument(instruction[1].attrib['type'], instruction[1].text)
    else:
        var1 = var_control(instruction[1])
        if (var1[0] == 'GF'):    # LF a TF
            GF_control_initialized(var1)
            arg1 = GF[var1[1]]
            if (arg1.type not in ['int', 'bool', 'string', 'nil']):
                exit(53)
        else:
            return

    if (instruction[2].attrib['type'] in ['int', 'bool', 'string', 'nil']):
        arg2 = ar.Argument(instruction[2].attrib['type'], instruction[2].text)
    else:
        var2 = var_control(instruction[2])
        if (var2[0] == 'GF'):   # LF a TF
            GF_control_initialized(var2)
            arg2 = GF[var2[1]]
            if (arg2.type not in ['int', 'bool', 'string', 'nil']):
                exit(53)
        else:
            return

    if ((arg1.type == 'nil' or arg2.type == 'nil') and op_code != 'eq'):
        exit(53)
    if (arg1.type != 'nil' and arg2.type != 'nil' and arg1.type != arg2.type):
        exit(53)

    value1 = typing(arg1)
    value2 = typing(arg2)

    if (op_code == 'eq'):
        result = (value1 == value2)
    elif (op_code == 'lt'):
        result = (value1 < value2)
    else:
        result = (value1 > value2)

    return result

#volanie porovnania a naplnenie premennej/return výsledok porovnania pre jumpifeq/jumpifneq
def my_compare(instruction, op_code, value):
    result = args_for_compare(instruction, op_code)
    if (value):
        var = var_control(instruction[0])
        if (var[0] == 'GF'):    # LF a TF
            GF_control(var)
            if (result):
                result = 'true'
            else:
                result = 'false'
            GF[var[1]] = ar.Argument('bool', result)
    else:
        return result

#exit inštrukcia
def my_exit(instruction):
    arg = symbol(instruction[0], 'int')
    number = number_to_decimal(arg)
    if (number < 0 or number > 49):
        exit(57)
    exit(number)

#jump inštrukcia
def jump(instruction):
    if (instruction[0].attrib['type'] != 'label'):
        exit(53)
    if (instruction[0].text not in labels):
        exit(52)
    key = labels[instruction[0].text]
    obj = dict_instructions[key]
    index = list_instructions.index(obj)
    return index

#parsovanie <symb> do class Argument
def symbol(symb, type):
    if (symb.attrib['type'] == type):
        arg = ar.Argument(type, symb.text)
    else:
        var = var_control(symb)
        if (var[0] == 'GF'):  # LF a TF
            GF_control_initialized(var)
            arg = GF[var[1]]
            if (arg.type != type):
                exit(53)
        else:
            return
    return arg

#concat inštrukcia
def concat(instruction):
    arg1 = symbol(instruction[1], 'string')
    arg2 = symbol(instruction[2], 'string')
    str = arg1.text + arg2.text
    var = var_control(instruction[0])
    if(var[0] == 'GF'):
        GF_control(var)
        GF[var[1]] = ar.Argument('string', str)

#strlen inštrukcia
def strlen(instruction):
    arg = symbol(instruction[1], 'string')
    length = len(arg.text)
    var = var_control(instruction[0])
    if (var[0] == 'GF'):
        GF_control(var)
        GF[var[1]] = ar.Argument('int', str(length))

#getchar inštrukcia
def getchar(instruction):
    arg1 = symbol(instruction[1], 'string')
    arg2 = symbol(instruction[2], 'int')
    number = int(arg2.text)
    if(number < 0 or number >= len(arg1.text)):
        exit(58)
    var = var_control(instruction[0])
    if (var[0] == 'GF'):
        GF_control(var)
        GF[var[1]] = ar.Argument('string', arg1.text[number])

#setchar inštrukcia
def setchar(instruction):
    arg1 = symbol(instruction[1], 'int')
    number = int(arg1.text)
    arg2 = symbol(instruction[2], 'string')
    if(arg2.text == ''):
        exit(58)
    var = var_control(instruction[0])
    if(var[0] == 'GF'):
        GF_control_initialized(var)
        if(GF[var[1]].type != 'string'):
            exit(53)
        string = GF[var[1]].text
        if(number < 0 or number >= len(string)):
            exit(58)
        if(len(string) - 1 == number):
            string = string[:number] + arg2.text[0]
        else:
            string = string[:number] + arg2.text[0] + string[number + 1:]
        GF[var[1]] = ar.Argument('string', string)

#type inštrukcia
def my_type(instruction):
    type = instruction[1].attrib['type']
    if(type == 'label'):
        exit(53)
    if(type == 'var'):
        var1 = var_control(instruction[1])
        if(var1[0] == 'GF'):
            GF_control(var1)
            value = GF[var1[1]]
            if(value == None):
                type = ''
            else:
                type = value.type
    var = var_control(instruction[0])
    if(var[0] == 'GF'):
        GF_control(var)
        GF[var[1]] = ar.Argument('type', type)

#dprint inštrukcia
def dprint(instruction):
    if (instruction[0].attrib['type'] not in ['var', 'string', 'int', 'bool', 'nil']):
        exit(53)
    if (instruction[0].attrib['type'] == 'nil'):
        print('', end='', file=sys.stderr)
    elif (instruction[0].attrib['type'] == 'var'):
        symb = instruction[0].text
        symb = symb.split("@")
        if (symb[0] == 'GF'):
            GF_control_initialized(symb)
            if (GF[symb[1]].type == 'nil'):
                print('', end='', file=sys.stderr)
            else:
                print(GF[symb[1]].text, end='', file=sys.stderr)  # LF a TF

    else:
        print(instruction[0].text, end='', file=sys.stderr)

#move inštrukcia
def move(instruction):
    if (instruction[1].attrib['type'] not in ['var', 'string', 'int', 'bool', 'nil']):
        exit(53)
    if (instruction[1].attrib['type'] == 'var'):
        symb = instruction[1].text
        symb = symb.split("@")
        if (symb[0] == 'GF'):
            GF_control_initialized(symb)
            arg = GF[symb[1]]
    else:
        arg = ar.Argument(instruction[1].attrib['type'], instruction[1].text)
    var = var_control(instruction[0])
    if(var[0] == 'GF'):
        GF_control(var)
        GF[var[1]] = arg


#vykonávanie jednotlivých inštrukcií
#key = index inštrukcie v usporiadanom zozname inštrukcií podľa order
def do(key):
    if (key >= len(list_instructions)):
        exit(0)
    instruction = list_instructions[key]
    op_code = instruction.attrib['opcode']
    op_code = op_code.lower()

    if (op_code == 'pushs'):
        deque.append(ar.Argument(instruction[0].attrib['type'], instruction[0].text))
    elif (op_code == 'pops'):
        pops(instruction)
    elif (op_code == 'defvar'):
        defvar(instruction)
    elif (op_code == 'write'):
        write(instruction)
    elif (op_code == 'read'):
        read(instruction)
    elif (op_code == 'int2char'):
        int2char(instruction)
    elif (op_code == 'stri2int'):
        stri2int(instruction)
    elif (op_code in ['add', 'sub', 'mul', 'idiv']):
        aritmetic(instruction, op_code, 'int', True, True)
    elif (op_code in ['and', 'or']):
        aritmetic(instruction, op_code, 'bool', False, True)
    elif (op_code == 'not'):
        aritmetic(instruction, op_code, 'bool', False, False)
    elif (op_code in ['lt', 'gt', 'eq']):
        my_compare(instruction, op_code, True)
    elif (op_code == 'label'):
        if (instruction[0].attrib['type'] != 'label'):
            exit(53)
        if (instruction[0].text in labels.keys()):
            exit(52)
        labels[instruction[0].text] = int(instruction.attrib['order'])
    elif (op_code == 'exit'):
        my_exit(instruction)
    elif (op_code == 'jump'):
        key = jump(instruction)
    elif (op_code in ['jumpifeq', 'jumpifneq']):
        result = my_compare(instruction, 'eq', False)
        if ((op_code == 'jumpifeq' and result) or (op_code == 'jumpifneq' and result == False)):
            key = jump(instruction)
    elif(op_code == 'concat'):
        concat(instruction)
    elif(op_code == 'strlen'):
        strlen(instruction)
    elif(op_code == 'getchar'):
        getchar(instruction)
    elif(op_code == 'setchar'):
        setchar(instruction)
    elif(op_code == 'type'):
        my_type(instruction)
    elif(op_code == 'dprint'):
        dprint(instruction)
    elif(op_code == 'move'):
        move(instruction)

    do(key + 1)


#kontrola parametrov
arguments = len(sys.argv)
sourceFile = None
inputFile = None
if (arguments == 2 and sys.argv[1] == '--help'):
    print(
        "Skript načíta XML reprezentáciu programu a tento program s využitím vstupu podľa parametrov příkazového riadku interpretuje a generuje výstup.")
    exit(0)
elif (1 < arguments < 4):
    for i in range(1, len(sys.argv)):
        if ('--source=' in sys.argv[i]):
            sourceFile = sys.argv[i][9:]
        elif ('--input=' in sys.argv[i]):
            inputFile = sys.argv[i][8:]
        else:
            exit(10)
else:
    exit(10)

if (sourceFile == None):
    sourceFile = input()
try:
    tree = ET.parse(sourceFile)
except:
    exit(31)
root = tree.getroot()

dict_instructions = {}
list_instructions = []
orders_set = set()
labels = {}
for child in root:
    if (int(child.attrib['order']) < 0 or child.attrib['order'] in orders_set or child.tag != 'instruction'):
        exit(32)
    orders_set.add(child.attrib['order'])
    list_instructions.append(child)
    dict_instructions[int(child.attrib['order'])] = child

dict_instructions = OrderedDict(sorted(dict_instructions.items()))

list_instructions.sort(key=my_sort)

do(0)

exit(0)