#!/usr/bin/perl

$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."kartat.txt") || die;
@data=<HANDLE>;
close(HANDLE);

$scale = 5000;
$dpi = 300;

if (open(HANDLE, "<".$path."kartat_dpi.txt")) {
    @data_dpi=<HANDLE>;
    close(HANDLE);

    foreach $rec_dpi (@data_dpi) {
        ($id_map,$scale_map,$dpi_map) = split(/\|/, $rec_dpi);
        if ($id_map eq $in{'jpgid'}) {
            $scale = $scale_map;
            $dpi = $dpi_map;
            last;
        }
    }
}

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html><head><STYLE>";
&tyyli;
print "</STYLE>
</head>
<body BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "<h3>Редактирование карты:</h3>";
print "<form action=reittimanager.".$extension." method=post>
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=savejpgedit>";

foreach $rec (@data) {
    ($id,$nimi,$copyright,$x1,$e1,$y1,$n1,$x2,$e2,$y2,$n2,$x3,$e3,$y3,$n3) = split(/\|/,$rec);
    if ($id eq $in{'jpgid'}) {
        print "<input type=hidden name=jpgid value=\"$in{'jpgid'}\">\n";
        print "Name:<br><input type=text name=jpgname value=\"$nimi\">\n";

        print '<p>Масштаб: <select name="map_scale">';
        foreach $scale_map ((4000,5000,7500,10000,15000)) {
            print '<option value="'.$scale_map.'"'.($scale_map == $scale ? ' selected' : '').'>1:'.$scale_map.'</option>';
        }
        print '</select> dpi: <select name="map_dpi">';
        foreach $dpi_map ((150,200,300,600)) {
            print '<option value="'.$dpi_map.'"'.($dpi_map == $dpi ? ' selected' : '').'>'.$dpi_map.'</option>';
        }
        print '</select></p>';

        print "<br>Copyright text:<br><input type=text name=copyright value=\"$copyright\">\n";

        print "<p>Map georeference. Three points, map image poimts<br>in pixels from top left corner, easting and northing in WGS84 degrees.\n";
        print "<p>Point 1:<br>X (from left):<br><input type=text name=x1 value=\"$x1\">\n";
        print "<br>Easting:<br><input type=text name=e1 value=\"$e1\">\n";
        print "<br>Y (from top):<br><input type=text name=y1 value=\"$y1\">\n";
        print "<br>Northing:<br><input type=text name=n1 value=\"$n1\">\n";

        print "<p>Point 2:<br>X (from left):<br><input type=text name=x2 value=\"$x2\">\n";
        print "<br>Easting:<br><input type=text name=e2 value=\"$e2\">\n";
        print "<br>Y (from top):<br><input type=text name=y2 value=\"$y2\">\n";
        print "<br>Northing:<br><input type=text name=n2 value=\"$n2\">\n";

        print "<p>Point 3:<br>X (from left):<br><input type=text name=x3 value=\"$x3\">\n";
        print "<br>Easting:<br><input type=text name=e3 value=\"$e3\">\n";
        print "<br>Y (from top):<br><input type=text name=y3 value=\"$y3\">\n";
        print "<br>Northing:<br><input type=text name=n3 value=\"$n3\">\n";

        last;
    }
}

print "<p><input type=submit value=\"  Save   \" size=20> </form><p></body></html>";