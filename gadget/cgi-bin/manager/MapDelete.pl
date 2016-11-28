#!/usr/bin/perl

open(HANDLE, "<".$path."kartat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html><head><STYLE>";
&tyyli;
print "</STYLE></head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$ulos="";
foreach $rec (@data){
    ($id,$nimi) = split(/\|/, $rec);
    if($id eq $in{'jpgpois'}){
        ## ei printata takaisin
        print "<p>Удалено: ".$id.".jpg  $nimi<p>";
        ## poistetaan myцs itse tiedosto
        unlink $path.$id.".jpg";
    }else{
        $ulos=$ulos.$rec;
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

    $ulos = "";
    foreach $rec (@data) {
        ($id) = split(/\|/, $rec);
        if ($id ne $in{'jpgpois'}) {
            $ulos .= $rec;
        }
    }

    open(HANDLE, ">".$path."kartat_dpi.txt");
    &lock_file;
    print HANDLE $ulos;
    &unlock_file;
    close HANDLE;
}

print "</body></html>";