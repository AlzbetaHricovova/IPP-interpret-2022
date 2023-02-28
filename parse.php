<?php 
    # Alžbeta Hricovová, xhrico00

    ini_set('display_errors', 'stderr');

    const INSTRUCTIONS_0 = array("createframe", "pushframe", "popframe", "return", "break");
    const INSTRUCTIONS_1 = array("defvar", "call", "pushs", "pops", "write", "label", "jump", "exit", "dprint");
    const INSTRUCTIONS_2 = array("move", "int2char", "read", "strlen", "type");
    const INSTRUCTIONS_3 = array("add", "sub", "mul", "idiv", "lt", "gt", "eq", "and", "or", "not", "stri2int", "concat", "getchar", 
                            "setchar", "jumpifeq", "jumpifneq");
    const TYPES = array("string", "int", "bool", "nil", "LF", "TF", "GF");

    # kontrola či vstup obsahuje pred inštrukciami identifikátor jazyka, prázdne riadky a komentáre sa ignorujú
    function my_header($stdin) {
        while (($line = fgets($stdin)) !== false) {
            $line = explode("#", $line);
            $line = $line[0];
            $line = trim($line);

            $words = preg_split("/\s+/", $line);
            switch(true) {
                case (strcmp(" ", $words[0]) === 1): break;
                case (strcasecmp(".IPPcode22", $words[0]) === 0):  
                    if(count($words) !== 1) {
                        exit(21);
                    }
                    return;
                default: exit(21); 
            }   
        }
        exit(21);
    }

    # kontrola či má operačný kód správny počet opeandov
    # $words - slová na riadku oddelené medzerami/ tabulátormi
    # $operands_count - správny počet operandov pre daný operačný kód
    function operands_control($words, $operands_count) {       
        if($operands_count !== (count($words) - 1)) {
            exit(23);
        }
    }

    # kontrola či daný string je celé číslo 
    # ak intval vyhodí 0, kontrola či string nepredstavuje číslo 0
    function number_control($string) {
        if(intval($string) === 0) {
            if(preg_match("/^[0][x][0]+$/", $string) === 0 and preg_match("/^[0][X][0]+$/", $string) === 0 and preg_match("/^[0]+$/", $string) === 0) {
                exit(23);
            }
        }
        if(str_contains($string, ".") or str_contains($string, ",")) {
            exit(23);
        }
    }
     
    # kontrola či string obsahuje len tisknuteľné znaky a \000-\999 a násladne postup na prepis problematických znakov XML
    function string_control($name) {   
        if(preg_match("/(\\\\\d\\d\\D)|(\\\\\d\\D)|(\\\\\D)/", $name) === 1 or preg_match("/[\x1-\x20\x23]/", $name) === 1) {
            exit(23);
        }
        return xml_characters($name);

    }

    # prepis problematických znakov XML
    function xml_characters($name) {
        $name = str_replace('&', "&amp;", $name);
        $name = str_replace('"', "&quot;", $name);
        $name = str_replace("'", "&apos;", $name);
        $name = str_replace('<', "&lt;", $name);
        $name = str_replace('>', "&gt;", $name);
        return $name;
    }

    # kontrola mena premennej a návestia - iba alfanumerické a špeciálne znaky, nezačína sa číslom
    function var_control($name) {
        if(preg_match("/^[a-zA-Z_\-$&%*!?]+[a-zA-Z_\-$&%*!?\d]*/", $name) === 0) {
            exit(23);
        }
    }

    # XML argument 
    # $type - typ argumentu
    # $value - text
    # $order - poradie argumentu (1, 2, 3)
    function write_argument($xw, $type, $value, $order) {
        xmlwriter_start_element($xw, 'arg' . $order);
        xmlwriter_start_attribute($xw, 'type');
        xmlwriter_text($xw, $type);
        xmlwriter_end_attribute($xw);
        xmlwriter_write_raw($xw, $value);
        xmlwriter_end_element($xw);
    }
 
    # kontrola parametrov, vypísanie --help nápovedy
    if($argc > 1) {
        if($argc == 2 and (!strcmp($argv[1], "--help") or !strcmp($argv[1], "-help"))) {
            echo "Skript typu filter načíta zo štandardného vstupu zdrojový kód v IPPcode22, skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný výstup XML reprezentáciu programu podľa špecifikácie.\n";
            exit(0);
        }
        exit(10);
    }

    $stdout = fopen('php://stdout', 'w') or exit(12);

    $xw = xmlwriter_open_memory();
    xmlwriter_set_indent($xw, 1);
    $res = xmlwriter_set_indent_string($xw, '    ');

    xmlwriter_start_document($xw, '1.0', 'UTF-8');

    xmlwriter_start_element($xw, 'program');
    xmlwriter_start_attribute($xw, 'language');
    xmlwriter_text($xw, 'IPPcode22');
    xmlwriter_end_attribute($xw);
 
    $stdin = fopen('php://stdin', 'r') or exit(11);
    my_header($stdin);

    # rozdelenie riadku # a bielymi znakmi
    $order = 0;
    while (($line = fgets($stdin)) !== false) {
        $line = explode("#", $line);
        $line = $line[0];
        $line = trim($line);

        $words = preg_split("/\s+/", $line);

        # preskočenie prázdneho riadku
        if(strcmp(" ", $words[0]) === 1) {  
            continue;
        }
      
        # kontrola operačného kódu a počtu operandov
        switch(true) {
            case (in_array(strtolower($words[0]), INSTRUCTIONS_0)): operands_control($words, 0); break;
            case (in_array(strtolower($words[0]), INSTRUCTIONS_1)): operands_control($words, 1); break;
            case (in_array(strtolower($words[0]), INSTRUCTIONS_2)): operands_control($words, 2); break;
            case (in_array(strtolower($words[0]), INSTRUCTIONS_3)): operands_control($words, 3); break;
            default: exit(22);
        }

        $order++;
        xmlwriter_start_element($xw, 'instruction');
        xmlwriter_start_attribute($xw, 'order');
        xmlwriter_text($xw, $order);
        xmlwriter_start_attribute($xw, 'opcode');
        xmlwriter_text($xw, strtoupper($words[0]));
        xmlwriter_end_attribute($xw); 

        # delenie slov @
        for($i = 1; $i < count($words); $i++) {
            if(str_contains($words[$i], "@")) {
                $variable = explode("@", $words[$i]);
                if(!in_array($variable[0], TYPES) or count($variable) !== 2) {
                    exit(23);
                }

                switch($variable[0]) {
                    case ("int"): number_control($variable[1]); write_argument($xw, "int", $variable[1], $i); break;
                    case ("bool"): if(strcmp($variable[1], "true") !== 0 and strcmp($variable[1], "false") !== 0) {exit (23);} 
                        write_argument($xw, "bool", $variable[1], $i); break;
                    case ("nil"): if(strcmp($variable[1], "nil") !== 0) { exit(23);} write_argument($xw, "nil", "nil", $i);; break;
                    case ("string"): $variable[1] = string_control($variable[1]); write_argument($xw, "string", $variable[1], $i); break;
                    default: var_control($variable[1]); write_argument($xw, "var", xml_characters($words[$i]), $i);
                }

            } else {
                var_control($words[$i]);
                if(strcasecmp($words[0], "read") === 0 and in_array($words[$i], TYPES)) {
                    write_argument($xw, "type", $words[$i], $i);
                } else {
                    write_argument($xw, "label", $words[$i], $i);
                }
            } 
        }  
        xmlwriter_end_element($xw);          
    }

    xmlwriter_end_element($xw);
    xmlwriter_end_document($xw);
    echo xmlwriter_output_memory($xw);
    
    fclose($stdin);
    fclose($stdout);
    exit(0);
?> 