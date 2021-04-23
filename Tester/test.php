<?php
# IPP projekt n.2, file: test.php
# Author: Samuel Gajdos
# Date: April 2020

### For error outputs ###
ini_set('display_errors', 'stderr');

### Constants for errors
const erPar = 10; ## parameter error


/**
 * Writes an error message and exits a program with error code.
 * @param $errcode
 * @param string $optional_str Addition to an error message
 */
function writeErr($errcode, $optional_str = '')
{
    global $order, $xml;
    switch ($errcode) {
        case erPar:
            fwrite(STDERR, "Chyba, zle zadany alebo nespravny pocet parametrov programu.\n");
            break;
    }
    fwrite(STDERR, $optional_str);
    exit($errcode);
}

/**
 * Writes a help in Slovak.
 */
function writeHelp()
{
    echo "Vitajte! Toto je stručná nápoveda k programu test.php:\n\n";
    echo "Program pracuje s následujúcimi parametrami:\n";
    echo "--help: Vypíše nápovedu.\n";
    echo "--directory=file: v zadanom file hlada testy, v pripade nezadania sa berie aktualny adresar.\n";
    echo "--recursive: Testy hlada nie len v danom adresari ale taktiez rekurzivne vo vsetkych jeho podadresaroch.\n";
    echo "--parse-script=file: Subor pre parse.php, v pripade nezadania berie sa subor v tomto adresari.\n";
    echo "--int-script=file: Subor pre interpret.py, v pripade nezadania berie sa subor v tomto adresari.\n";
    echo "--parse-only: bude testovny iba skript pre analýzu zdrojového kódu v IPPcode20\n";
    echo "--int-only: bude testovny iba skript pre interpret zdrojoveho kodu IPPcode20 v XML reprezentacii.\n";
    echo "--jexamxml=file: subor s JAR balíčkom s nástrojom A7Soft JExamXML. Ak je parameter vynechaný uvažuje se implicitné umiestnenie.\n";


    exit(0);
}

/**
 * Converts an array to a string and puts it in a temporary file, then returns the file.
 * @param $array
 * @return false|resource
 */
$tmp = tmpfile();
function tmpfile_array($array)
{
    $output_string = "";
    $length = count($array);
    $i = 0;
    foreach ($array as $line) {
        if (++$i === $length) {
            $output_string .= $line;
        }
        else {
            $output_string .= $line . "\n";
        }
    }
    global $tmp;

    fclose($tmp);
    $tmp = tmpfile();
    fseek($tmp, 0);
    fwrite($tmp, $output_string);
    $metadata = stream_get_meta_data($tmp);

    return $metadata['uri'];
}

### Global variable for HTML output ###
$html='<html lang="sk" dir="ltr" class="inited"><head>

<style>
table {border: none;}
  table tr:hover {background-color: #ddd;}

  td {border-bottom: 1px solid #ddd;}

table {border: none;}
table tr:hover {background-color: #bdc5cd;}

th {background-color: #bdc5cd ;}

  .dir {
                    text-align: left;
    background-color: #54616d !important;
    color: white;
  }

  .summary {
                    text-align: left;
    background-color: #003300 !important;
    color: white;
  }
</style>

</head>
<body>
  <h1 align="center">
  test.php results for IPPCode20
    </h1>
    
    <h3 align="center">
   VUT FIT Brno
   </h3>
';
### Global variables for tests info ###
$test_counter = 1;
$dir_pass_counter_rc = 0;
$dir_pass_counter_out = 0;
$total_tests = 0;
$total_passed = 0;
$failed_src_files = [];


/**
 * Creates a new table of test results in the directory.
 * @param $directory
 */
function html_TableStart($directory){
    global $html;
    $html .= '<table align="center" style="width:70%">
  <tr class="dir">
    <td colspan="7" align="center">DIRECTORY: <b>' . $directory . '</b></td>
  </tr>

  <tbody><tr>
<th width="5%">#</th>
<th width="44%">Test Name</th>
<th width="9%"> RC parse.php</th>
<th width="9%">RC interpret.py</th>
<th width="9%">RC<br>Expected</th>
<th width="12%">Test Result RC</th>
<th width="12%">Test Result OUT</th>
  </tr>
';
}

/**
 * Adds a new test result to a table
 * @param string $src File with a source code to test .src
 * @param int $parse_rc Return code parse.php
 * @param int $int_rc Return code interpret.php
 * @param int $expected_rc Expected return code from file .rc
 * @param bool $rc_pass True if a test return code matches a program return code.
 * @param bool $out_pass True if a test output matches a program output.
 */
function html_AddTest($src, $parse_rc = '', $int_rc = '', $expected_rc, $rc_pass, $out_pass)
{
    global $html, $test_counter, $dir_pass_counter_rc, $dir_pass_counter_out, $failed_src_files;

    if ($out_pass == true) {
        $out_pass = 'style="color:green;"><b>PASS</b>';
        $dir_pass_counter_out += 1;
    }
    else {
        $out_pass = 'style="color:red;"><b>FAIL</b>';
        $failed_src_files[$src] = 'OUT';
    }

    if ($rc_pass == true) {
        $rc_pass = 'style="color:green;"><b>PASS</b>';
        $dir_pass_counter_rc += 1;
    }
    else {
        $rc_pass = 'style="color:red;"><b>FAIL</b>';
        $failed_src_files[$src] = 'RC';
    }

    $html .= '<tr>
    <td align="center">' . $test_counter . '</td>
    <td>' . $src . '</td>
    <td align="center">' . $parse_rc . '</td>
    <td align="center">' . $int_rc . '</td>
    <td align="center">' . $expected_rc . '</td>
    <td align="center"' . $rc_pass . '</td>
    <td align="center"' . $out_pass . '</td>
  </tr>
  ';

    $test_counter += 1;
}

/**
 * End of a table for a certain directory.
 * @param $directory
 * @param int $dir_total_number_tests Number of successful tests
 */
function html_TableEnd($directory, $dir_total_number_tests)
{
    global $html, $dir_pass_counter_rc, $dir_pass_counter_out, $total_tests, $total_passed;

    $html .= '<tr class="summary">
    <td colspan="5" align="center">TOTAL PASSED IN: <b>'. $directory . '</b></td>
    <td align="center">RC: <b>'. $dir_pass_counter_rc . '/' . $dir_total_number_tests . '</b></td>
    <td align="center">OUT: <b>'. $dir_pass_counter_out . '/' . $dir_total_number_tests . '</b></td>
  </tr>
  </tbody></table>
  <p></p>
  ';

    ### Total number of successful tests for a final output.
    $total_tests += $dir_total_number_tests;
    $total_passed += $dir_pass_counter_out;
    $dir_pass_counter_rc = 0;
    $dir_pass_counter_out = 0;
}

/**
 * Writes a list of tests that failed. Writes the first occurence of fail.
 */
function html_FailedSrc()
{
    global $html, $failed_src_files;

    $html .= '<table align="center" style="width:70%">
    <tbody><tr>
<th width="70%">Failed Test File</th>
<th width="30%">Where Failed First</th>
  </tr>
    ';

    foreach ($failed_src_files as $src_file => $fail)
    {
        $html .= '<tr>
    <td>' . $src_file . '</td>
    <td align="center">' . $fail . '</td>
  </tr>
  ';
    }

    $html .= '</tbody></table>
    <p><br></p>
    ';
}

/**
 * Writes final results.
 */
function html_TotalEnd()
{
    global $html, $total_tests, $total_passed, $failed_src_files;
    $html .= '<table align="center" style="width:70%">
    <tr class="summary">
    <td colspan="5" align="center"><b>TOTAL PASSED ALL:</b></td>
    <td colspan="2" align="center"><b>'. $total_passed . '/' . $total_tests . '</b></td>   
    </tr>
    </tbody></table>
    <p><br></p>
    ';

    if (!empty($failed_src_files)) {
        html_FailedSrc();
    }
    $html.='
     <h4 align="right">
   Author: Samuel Gajdos, xgajdo26
     </h4>
   ';
    echo $html;
}

### Array of parameters for test.php ###
$longopts = array(
    "help",
    "directory:",
    "recursive",
    "parse-script:",
    "int-script:",
    "parse-only",
    "int-only",
    "jexamxml:",
);
$optind = null;
$options = getopt("", $longopts, $optind);

### Pri nespravnom pocte alebo nespravne zadanych argumentov hodi chybu
if ($optind != $argc) {
    writeErr(erPar);
}
if ($optind != count($options)+1){
    writeErr(erPar);
}

### Variables init which can be changed with program params ###
$directory = ".";
$recursive = false;
$parse_script = "parse.php";
$int_script = "interpret.py";
$parse_only = false;
$int_only = false;
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";

if (array_key_exists('help', $options)) {
    writeHelp();
}
if (array_key_exists('directory', $options)) {
    if (($directory = $options['directory']) === null)
        writeErr(erPar, "Nezadané directory.\n");
}
if (array_key_exists('parse-script', $options)) {
    if (($parse_script = $options['parse-script']) === null)
        writeErr(erPar, "Nezadaný parse-script.\n");
}
if (array_key_exists('int-script', $options)) {
    if (($int_script = $options['int-script']) === null)
        writeErr(erPar, "Nezadaný int-script.\n");
}
if (array_key_exists('jexamxml', $options)) {
    if (($jexamxml = $options['jexamxml']) === null)
        writeErr(erPar, "Nezadaný jexamxmlt.\n");
}
if (array_key_exists('int-only', $options)) {
    if (array_key_exists('parse-only', $options) or array_key_exists('parse-script', $options))
        writeErr(erPar, "S parametrom 'int-only' nemozu existovat parametre 'parse-only' alebo 'parse-script'.\n");
    else
        $int_only = true;
}
if (array_key_exists('parse-only', $options)) {
    if (array_key_exists('int-only', $options) or array_key_exists('int-script', $options))
        writeErr(erPar, "S parametrom 'parse-only' nemozu existovat parametre 'int-only' alebo 'int-script'.\n");
    else
        $parse_only = true;
}
if (array_key_exists('recursive', $options)) {
    $recursive = true;
}

### Ak file obsahuje na konci '/' -> odrezanie kvoli scandir funkcii
if (substr($directory, -1) == '/') {
    $directory = substr($directory, 0, -1);
}

### Testovanie existencie programov a adresatu na beh testov
if (!file_exists($parse_script)) {
    writeErr(erPar, "Súbor 'parse.php' sa nenašiel.\n");
}
if (!file_exists($int_script)) {
    writeErr(erPar, "Súbor 'interpret.py' sa nenašiel.\n");
}
if (!file_exists($directory) and !is_dir($directory)) {
    writeErr(erPar, "Zadané directory nie je správne.\n");
}
/**
 * Hlavná funkcia na beh testov, pri zadaní parametra '--recursive' sa táto funkcia volá rekurzívne.
 * @param string $directory Aktuálny adresár pre testovanie
 */
function main_test($directory)
{
    global $recursive, $parse_only, $parse_script, $int_only, $int_script, $jexamxml;

    $files = scandir($directory);

    $src_files = [];
    $in_files = [];
    $out_files = [];
    $rc_files = [];
    $dir_files = [];

    $directory = $directory . '/';

    ### Prejdenie vsetkych suborov/adresarov v akutalnom adresari, a ich triedenie do poli podla typu ###
    foreach ($files as $file) {
        if (substr($file, -4) == '.src') {
            array_push($src_files, substr($file, 0, -4));
            continue;
        }
        if (substr($file, -4) == '.out') {
            array_push($out_files, substr($file, 0, -4));
            continue;
        }
        if (substr($file, -3) == '.in') {
            array_push($in_files, substr($file, 0, -3));
            continue;
        }
        if (substr($file, -3) == '.rc') {
            array_push($rc_files, substr($file, 0, -3));
            continue;
        }
        ### Ak mame parameter --recursive ukladame si aj adresare ###
        if ($recursive == true and is_dir($directory . $file) and $file != "." and $file != "..") {
            array_push($dir_files, $file);
            continue;
        }
    }

    ### Abecedne zoradenie testov ###
    sort($src_files);

    if (count($src_files) != 0) {
        html_Tablestart($directory);

        foreach ($src_files as $name) {

            $input_path = $directory . $name . '.in';
            #Ak sa nenachadza .in subor, vytvorime prazdny
            if (!in_array($name, $in_files)) {
                $file = fopen($input_path, "w");
                fwrite($file, "");
                fclose($file);
            }

            $output_path = $directory . $name . '.out';
            #Ak sa nenachadza .out subor, vytvorime prazdny
            if (!in_array($name, $out_files)) {
                $file = fopen($output_path, "w");
                fwrite($file, "");
                fclose($file);
            }

            $rc_path = $directory . $name . '.rc';
            #Ak sa nenachadza .rc subor, vytvorime prazdny
            if (!in_array($name, $rc_files)) {
                $file = fopen($rc_path, "w");
                fwrite($file, "0");
                fclose($file);
                $rc = 0;
            } else {
                $rc = file_get_contents($rc_path, FILE_USE_INCLUDE_PATH);
            }

            $src = $directory . $name . '.src';
            $rc_pass = false;
            $out_pass = false;

            if ($parse_only == true) {
                exec('php7.4 ' . $parse_script . ' < ' . $src, $parse_out, $parse_rc);
                if ($rc == $parse_rc) {
                    $rc_pass = true;
                    if ($rc == 0) {
                        $parse_out_tmp = tmpfile_array($parse_out);
                        exec('java -jar ' . $jexamxml . ' ' . $output_path . ' ' . $parse_out_tmp, $jexamxml_out, $jexamxml_rc);
                        if ($jexamxml_rc == 0) {
                            $out_pass = true;
                        }
                    } else {
                        $out_pass = true;
                    }
                }
                html_AddTest($src, $parse_rc,null, $rc, $rc_pass, $out_pass);

            } elseif ($int_only == true) {
                exec('python3.8 ' . $int_script . ' --source=' . $src . ' < ' . $input_path, $int_out, $int_rc);
                if ($rc == $int_rc) {
                    $rc_pass = true;
                    if ($rc == 0) {
                        $int_out_tmp = tmpfile_array($int_out);
                        exec('diff ' . $output_path . ' ' . $int_out_tmp, $diff_out, $diff_rc);
                        if ($diff_rc == 0) {
                            $out_pass = true;
                        }
                    } else {
                        $out_pass = true;
                    }
                }
                html_AddTest($src, null, $int_rc, $rc, $rc_pass, $out_pass);

            } else {
                exec('php7.4 ' . $parse_script . ' < ' . $src, $parse_out, $parse_rc);
                if ($parse_rc != 0) {
                    if ($rc == $parse_rc) {
                        $rc_pass = true;
                        $out_pass = true;
                    }
                    html_AddTest($src, $parse_rc, null, $rc, $rc_pass, $out_pass);

                } else {
                    $parse_out_tmp = tmpfile_array($parse_out);

                    exec('python3.8 ' . $int_script . ' --source=' . $parse_out_tmp . ' < ' . $input_path, $int_out, $int_rc);
                    if ($rc == $int_rc) {
                        $rc_pass = true;
                        if ($rc == 0) {
                            $int_out_tmp = tmpfile_array($int_out);

                            exec('diff ' . $output_path . ' ' . $int_out_tmp, $diff_out, $diff_rc);
                            if ($diff_rc == 0) {
                                $out_pass = true;
                            }
                        } else {
                            $out_pass = true;
                        }
                    }
                    html_AddTest($src, $parse_rc, $int_rc, $rc, $rc_pass, $out_pass);
                }

            }

            $int_out = [];
            $parse_out = [];
            $jexamxml_out = [];

        }
        html_TableEnd($directory, count($src_files));
    }

    if ($dir_files != []){
        foreach ($dir_files as $dir) {
            main_test($directory . $dir);
        }
    }
}

main_test($directory);
html_TotalEnd();
?>