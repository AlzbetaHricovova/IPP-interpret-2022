<?php

    #Alžbeta Hricovová, xhrico00

    #funkcia na kontrolu jexam a jej výsledného súboru- test prešiel/neprešiel -> html výstup
    function jexam() {
        global $out, $name, $jexampath, $directory, $bool, $html, $ok;
        if(filesize($out) == 0 and filesize($name."-parse_out.out")==0) {
            $ok++;
            $bool = false;
            fwrite($html, "<b style=\"color:green;\">OK<br></b>\n");
        } elseif(filesize($out) != 0 and filesize($name."-parse_out.out")!=0) {                         
            system("java -jar ".$jexampath."jexamxml.jar ".$name."-parse_out.out ".$out." ".$directory."/delta.xml ".$jexampath."options");

            if(file_exists($directory."/delta.xml")) {
                $delta = fopen($directory."/delta.xml", "r") or exit(12);
            } else {
                $bool = false;
                fwrite($html, "<b style=\"color:red;\">NOK<br></b>\n");
                return;
            }

            $line_delta = fgets($delta);
            if(feof($delta)) {
                $ok++;
                fwrite($html, "<b style=\"color:green;\">OK<br></b>\n");
                return;
            }
            fwrite($html, "<b style=\"color:red;\">NOK<br></b>\n");
            
        } else {
            $bool = false;
            fwrite($html, "<b style=\"color:red;\">NOK<br></b>\n");
        }
    }

    #porovnanie .out súborov ->html výstp
    function out_control() {
        global $directory, $html, $ok;
        $file = fopen($directory."/diff.txt", 'r') or exit(11);
        $line = fgets($file);
        if($line == "") {
            $ok++;
            fwrite($html, "<b style=\"color:green;\">OK<br></b>\n");
        } else {
            fwrite($html, "<b style=\"color:red;\">NOK<br></b>\n");
        }
    }

    #porovnanie .rc súborov
    #výstup: bool - pokračovanie v porovnaní .out súborov
    function control() {
        global $directory, $html;
        $file = fopen($directory."/diff.txt", 'r') or exit(11);
        $line = fgets($file);
        if($line == "") {
            return true;
        }
        fwrite($html, "<b style=\"color:red;\">NOK<br></b>\n");
        return false;
              
    }

    # --help parameter
    if($argc == 2 and (!strcmp($argv[1], "--help") or !strcmp($argv[1], "-help"))) {
        echo "Skript slúži pre automatické testovanie (postupné) aplikácie parse.php a interpret.py. Skript prejde zadaný adresár s testmi a využije ich pre automatické otestovanie správnej funkčnosti jedného či oboch predchádzajúcich skriptov vrátane vygenerovania prehľadného súhrnu v HTML 5 na štandardný výstup.\n";
        exit(0);
    }


    $directory = Null;
    $recursive = false;
    $parse_script = Null;
    $int_script = Null;
    $parse_only = false;
    $int_only = false;
    $jexampath = Null;
    $noclean = false;

    #parsovanie parametrov
    for($i = 1; $i < $argc; $i++) {
        switch(true) {
            case(str_starts_with($argv[$i], "--directory=")): $directory = substr($argv[$i], 12); break;
            case(!strcmp($argv[$i], "--recursive")): $recursive = true; break;
            case(str_starts_with($argv[$i], "--parse-script=")): $parse_script = substr($argv[$i], 15); break;
            case(str_starts_with($argv[$i], "--int-script=")): $int_script = substr($argv[$i], 13); break;
            case(!strcmp($argv[$i], "--parse-only")): $parse_only = true; break;
            case(!strcmp($argv[$i], "--int-only")): $int_only = true; break;
            case(str_starts_with($argv[$i], "--jexampath=")): $jexampath = substr($argv[$i], 12); break;
            case(!strcmp($argv[$i], "--noclean")): $noclean = true; break;
            default: exit(10);
        }
    }    
    
    if($parse_only and ($int_only or $int_script)) {
        exit(10);
    }

    if($int_only and ($parse_only or $parse_script or $jexampath)) {
        exit(10);
    }

    if($jexampath and $jexampath[-1] != '/') {
        $jexampath = $jexampath . '/';
    }

    if(!$jexampath) {
        $jexampath = "/pub/courses/ipp/jexamxml/";
    }

    if(!$directory) {
        $directory = getcwd();
    }


    if(!is_dir($directory)) {
        exit(41);
    }

    if(!$parse_script) {               
        $parse_script = $directory."/parse.php";
    }

    if(!$int_script) {
        $int_script = $directory."/interpret.py";

    }

    if(!file_exists($parse_script) or !file_exists($int_script)) {
        exit(41);
    }

    $html = fopen($directory."/my_html.html", "w");
    fwrite($html, "<!DOCTYPE html>\n<html>\n<body>\n");
    fwrite($html, "\n<h1>TESTY</h1>\n");
    
    $bool = false;
    $all = 0;
    $ok = 0;
    $list_dir = scandir($directory) or exit(41);
    for($i = 0; $i < count($list_dir); $i++) {

        #uloženie testovaných súborov
        if(str_ends_with($list_dir[$i], ".src")) {
            $all++;
            $src =$list_dir[$i];
            $src = $directory."/".$src;
            $name = substr($list_dir[$i], 0, strlen($list_dir[$i])- 4);

            fwrite($html, "<text>".$name." = <text>");

            $name = $directory."/".$name;
            if(!file_exists($name.".in")) {
                $in = fopen($name.".in", "w") or exit(11);
            } else {
                $in = $name.".in";
            }
            if(!file_exists($name.".out")) {
                $out = fopen($name.".out", "w") or exit(11);
            } else {
                $out = $name.".out";
            }
            if(!file_exists($name.".rc")) {
                $rc = fopen($name.".rc", "w") or exit(11);
                fwrite($rc, "0\n") or exit(99);
            } else {
                $rc = $name.".rc";
            }
    
            if($parse_only) {
                system("php8.1 ".$parse_script." < ".$src." > ".$name."-parse_out.out", $return_value);
                system("echo ".$return_value." > ".$name."-parse.rc");
                system("diff ".$rc." ".$name."-parse.rc > ".$directory."/diff.txt");
                $bool = control();
                if($bool) {
                    jexam();                    
                }
    
            } elseif($int_only) {
                system("python3.8 ".$int_script." --input=".$in." --source=".$src." > ".$name."-int_out.out", $return_value);             
                system("echo ".$return_value."  > ".$name."-int.rc");
                system("diff ".$rc." ".$name."-int.rc > ".$directory."/diff.txt");
                $bool = true;
                if(control()) {
                    if($return_value == 0) {
                        system("diff ".$out." ".$name."-int_out.out > ".$directory."/diff.txt");
                        out_control();
                    } else {
                        $ok++;
                        fwrite($html, "<b style=\"color:green;\">OK<br></b>\n"); 
                    }   
                }
    
            } else {
                system("php8.1 ".$parse_script." < ".$src." > ".$name."-parse_out.out", $return_value);
                system("echo ".$return_value." > ".$name."-parse.rc");
                system("diff ".$rc." ".$name."-parse.rc > ".$directory."/diff.txt");
                $bool = control();
                if($bool) {
                    system("python3.8 ".$int_script." --input=".$in." --source=".$name."-parse_out.out"." > ".$name."-int_out.out", $return_value);
                    system("echo ".$return_value." > ".$name."-int.rc");
                    system("diff ".$out." ".$name."-int_out.out > ".$directory."/diff.txt");
                    out_control();                    
                }
            }  
                
            if(!$noclean) {
                unlink($directory."/diff.txt");
                if(!$parse_only and $bool) {
                    unlink($name."-int_out.out");    
                    unlink($name."-int.rc");
                }
                if(!$int_only) {
                    unlink($name."-parse.rc");
                    unlink($name."-parse_out.out");  #vymaz delta
                }
                if($parse_only and $bool) {
                    unlink($directory."/delta.xml");
                }
            }
    
        }
    
        if($recursive and is_dir($list_dir[$i]) and !str_starts_with($list_dir[$i], ".")) {
            
        }
    }

    fwrite($html, "\n<h3>Suma: ".$all.", uspelo: ".$ok."</h3>\n");
    fwrite($html, "</body>\n</html>\n");
    system("cat my_html.html");
    unlink($directory."/my_html.html");
    exit(0);
?>