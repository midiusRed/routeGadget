#!/usr/bin/perl

open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

open(SISAAN, "<".$path."kartat.txt");
@tmaps=<SISAAN>;
close(SISAAN);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML><head><STYLE>";
&tyyli;
print "</STYLE></head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<h3>RouteGadget Manager</h3><hr>";
print "<p><b>Events:</b>";
print "<p><a href=\"reittimanager.".$extension."?act=uusi1&keksi=$in{'keksi'}\">Add new event</a><p>";
print "<hr><b>Update split times (SI csv only):</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=uploadsplits><select name=kisaid>\n";
print "<option value=valitse>Select event\n";
$str = '';
foreach $rec (@data) {
    chomp( $rec );
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    $str = "<option value=$id> (id: $id) $paiva $nimi\n".$str;
}
print $str."</select>&nbsp;&nbsp;<input type=submit value=\"   OK   \" size=20> </form><p>";

print "<p><hr><b>Delete event:</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=poistakisa><select name=kisaid>\n";
print "<option value=valitse>Select\n";
$str = '';
foreach $rec (@data) {
    chomp($rec);
    chomp($rec);
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split(/\|/, $rec, 7);
    $str = "<option value=$id> (id: $id) $paiva $nimi\n".$str;
}
print $str."</select>&nbsp;&nbsp;<input type=submit value=\" Delete \" size=20> </form><p>";
print "<hr><b>Delete a route drawing (select first event):</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=valitsepiirrospois><select name=kisaid>\n";
print "<option value=valitse>Select\n";
$str = '';
foreach $rec (@data) {
    chomp( $rec );
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    $str = "<option value=$id> (id: $id) $paiva $nimi\n".$str;
}
print $str."</select>&nbsp;&nbsp;<input type=submit value=\"   OK   \" size=20> </form><p>";

print "<hr><b>Delete course/class (select event):</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=valitseratapois><select name=kisaid>\n";
print "<option value=valitse>Select\n";
foreach $rec (@data) {
    chomp( $rec );
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    print "<option value=$id> (id: $id) $paiva $nimi\n";
}
print "</select>&nbsp;&nbsp;<input type=submit value=\"   OK   \" size=20> </form><p><hr>";

print "<b>Edit raster map information (name, copyright text, georeference)</b>";
print "<p><a href=reittimanager.".$extension."?act=valitsejpg&keksi=$in{'keksi'}>Select map to be edited</a><p>";

print "<hr><b>Delete a raster map</b>";
print "<p><a href=reittimanager.".$extension."?act=valitsejpgpois&keksi=$in{'keksi'}>Select map to be deleted</a><p>";
print "<hr><b>Load routes as dxf -file (select event):</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=routedxf><select name=kisaid>\n";
print "<option value=valitse>Select\n";
foreach $rec (@data) {
    chomp( $rec );
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    print "<option value=$id> (id: $id) $paiva $nimi\n";
}
print "</select>&nbsp;&nbsp;<input type=submit value=\"Load dxf\" size=20> </form><p>";
print "<hr><b>Edit event information (name, date, club, level):</b>";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=editoitietoja><select name=kisaid>\n";
print "<option value=valitse>Select\n";
foreach $rec (@data) {
    chomp( $rec );
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    print "<option value=$id> (id: $id) $paiva $nimi\n";
}
print "</select>&nbsp;&nbsp;<input type=submit value=\"   edit    \" size=20> </form><p>";
print "<hr><b>Add courses to some event (only events created without any result files)</b><p>
<a href=reittimanager.".$extension."?act=lisaaratoja&keksi=$in{'keksi'}>Select event</a>";
print "<hr><b>Load preprocessed event from another RouteGadget</b> <p>
<a href=reittimanager.".$extension."?act=valitsetapahtumalataus&keksi=$in{'keksi'}>Upload event</a><br><p>";
if ($allow_clubname_edit == '1') {
    print "<hr><b>Configure Club Names Dropdown List</b> <p>
<a href=reittimanager.".$extension."?act=configclubnames&keksi=$in{'keksi'}>Configure Club Names Dropdown List</a><br><p>";
}
foreach $rec (@tmaps) {
    chomp( $rec );
    chomp( $rec );
    ($id, $nimi, $cop, $geor) = split( /\|/, $rec );

    if ($geor != 0) {
        $gr{$id} = 1;
    }

}

print "<hr><b>Georeference event's map</b> with GPX file: <form target=_blank action=../reitti.".$extension."?kieli= method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=map>";
print "<select name=mapid>\n";
print "<option value=0>Select\n";
foreach $rec (@data) {
    chomp( $rec );
    ($id, $karttaid, $tyyppi, $nimi, $paiva, $seura, $taso) = split( /\|/, $rec, 7 );
    if ($gr{$karttaid} == 1) {
        print "<option value=$karttaid>(Georeferenced) Event $id $nimi $paiva</option>\n";
    } else {
        print "<option value=$karttaid>(Georef missing)Event $id $nimi $paiva</option>\n";
    }
}

foreach $rec (@tmaps) {
    chomp( $rec );
    chomp( $rec );
    ($id, $nimi, $cop, $geor) = split( /\|/, $rec );
    if ($gr{$id} == 1) {
        print "<option value=$id>(Georeferenced) Map $id $nimi</option>\n";
    } else {
        print "<option value=$id>(Georef missing) Map $id $nimi</option>\n";
    }
}
print "</select><input type=hidden name=calib value=1><input type=hidden name=gps value=1><input type=hidden name=id value=0>";
print "<br>Select GPX file:&nbsp;&nbsp;<input type=file name=tracklog>&nbsp;&nbsp;&nbsp;&nbsp;<input type=submit value=\"   Go   \" size=20> </form><p>";

print "<hr><p><b>Live GPS tracking:</b>";
print "<p><a href=\"reittimanager.".$extension."?act=edittracking&keksi=$in{'keksi'}\">Configure live tracking parameters</a><p>";
print "<p><b>Upload live tracking map image</b>";
print "<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=uploadgpsmap>";
print "<p>Select map image (gif or jpg)<br><input type=file name=karttakuva>";
print "&nbsp;&nbsp;<input type=submit value=\"   Upload   \" size=20> </form><p>";
print "<form target=_blank action=../reitti.".$extension."?kieli= method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=map><input type=hidden name=id value=0><input type=hidden name=calib value=1><input type=hidden name=gps value=1>";
print "<p><b>Calibrate map with GPX file</b>
<br>Select GPX file:&nbsp;&nbsp;<input type=file name=tracklog>&nbsp;&nbsp;&nbsp;&nbsp;<input type=submit value=\"   Go   \" size=20> </form><p>";

print "<form target=_blank action=../reitti.".$extension."?kieli= method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=map><input type=hidden name=id value=0><input type=hidden name=regtest value=1><input type=hidden name=gps value=1>";
print "<p><b>Check map calibration with a GPX file</b>
<br>Select GPX file:&nbsp;&nbsp;<input type=file name=tracklog>&nbsp;&nbsp;&nbsp;&nbsp;<input type=submit value=\"   Go   \" size=20> </form><p>";

print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=savenewjpgmap>\n";
print "Save current georeferenced tracking map to map register as <input name=jpgname value='map name'>
&nbsp;&nbsp;<input type=submit value=\"Save\" size=20> </form><p>";

print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=regmaptotracking>Select registered map for tracking: <select name=jpgid>\n";
print "<option value=valitse>Select\n";
foreach $rec (@tmaps) {
    chomp( $rec );
    chomp( $rec );
    ($id, $nimi, $cop, $geor) = split( /\|/, $rec );

    if ($geor != 0) {
        $gr{$id} = 1;
    }

    print "<option value=$id> id $nimi\n";
}
print "</select>&nbsp;&nbsp;<input type=submit value=\"  OK   \" size=20> </form><p>";

print "<p><a href=\"../reitti.".$extension."?piirrarastit=1&id=0&eventtype=2&act=map&keksi=$in{'keksi'}\">Draw tracking courses</a><p>";
print "<p><a href=\"reittimanager.".$extension."?act=deltrackingcourses&keksi=$in{'keksi'}\">Delete all tracking courses </a><p>";
print "<p><a href=\"reittimanager.".$extension."?act=initgpslast&keksi=$in{'keksi'}\">Initialize live tracking </a> Do this always once before you start new tracking session.<br>(Clears old tracking data, so it will cause any truoble. Note, previous trackings will be deleted)<p>";
#print "<p><a href=\"reittimanager.".$extension."?act=trackingon&keksi=$in{'keksi'}\">Turn tracking On </a> (Public access to RG tracking page)";
#print "<p><a href=\"reittimanager.".$extension."?act=trackingoff&keksi=$in{'keksi'}\">Turn tracking Off </a> (No public access to RG tracking page)";
#print "<p><a href=\"reittimanager.".$extension."?act=gpslivetorgevent&keksi=$in{'keksi'}\">Convert event to be normal RG event </a> (to be archived and replayed in normal RG mode. Do this when event is over) <p>";
print "<hr>";

print "<hr></html>";