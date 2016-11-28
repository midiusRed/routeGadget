#!/usr/bin/perl

open(HANDLE, "<".$path."kartat.txt") || die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){
    ($id,$nimi) = split(/\|/,$rec);
    if ($id eq $in{'jpgid'}) {
        ## ei printataan takaisin uudet tiedot

        $in{'copyright'}=~s/\n//g;
        $in{'copyright'}=~s/\r//g;

        $ulos = $ulos.$id.'|'.$in{'jpgname'}.'|'.$in{'copyright'}.'|'.$in{'x1'}.'|'.$in{'e1'}.'|'.$in{'y1'}.'|'.$in{'n1'}.'|'.$in{'x2'}.'|'.$in{'e2'}.'|'.$in{'y2'}.'|'.$in{'n2'}.'|'.$in{'x3'}.'|'.$in{'e3'}.'|'.$in{'y3'}.'|'.$in{'n3'}."\n";
    } else {
        $ulos = $ulos.$rec;
    }
}

open(HANDLE, ">".$path."kartat.txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;

if (open(HANDLE, "<".$path."kartat_dpi.txt")) {
    &lock_file;
    @data=<HANDLE>;
    &unlock_file;
    close(HANDLE);

    $ulos="";
    foreach $rec (@data){
        ($id) = split(/\|/,$rec);
        if ($id eq $in{'jpgid'}) {
            $ulos .= $in{'jpgid'}.'|'.$in{'map_scale'}.'|'.$in{'map_dpi'}."\n";
        } else {
            $ulos .= $rec;
        }
    }

} else {
    $ulos = $in{'jpgid'}.'|'.$in{'map_scale'}.'|'.$in{'map_dpi'};
}

open(HANDLE, ">".$path."kartat_dpi.txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html><head><STYLE>";
&tyyli;
print "</STYLE>
</head>
<body BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "Карта была успешно изменена!</body></html>";