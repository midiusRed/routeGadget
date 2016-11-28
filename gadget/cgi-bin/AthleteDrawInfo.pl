#!/usr/bin/perl
$sarja=1*$in{'sarja'};
$eventid=$in{'eventid'}*1;

open (SISAAN,"<".$path."kilpailijat_".$eventid.".txt");
@d=<SISAAN>;
close(SISAAN);

foreach $rec (@d) {
    chomp($rec);
    $rec =~ s/\"//g;
    $rec =~ s/\n//g;
    $rec =~ s/\r//g;
    @r=split(/\|/,$rec);
    if ($r[1] == $sarja && $r[0] < 50000) { #>50000 - gps трек
        $out[$#out+1] = "{\"$r[0]\":\"$r[3]\"}";
    }
}

$out='['.join(',',@out)."]\n";
utf8::decode($out);
print $out;