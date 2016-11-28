#!/usr/bin/perl
$in{'eventid'}=1*$in{'eventid'};

open (SISAAN,"<$path".'ratapisteet_'.$in{'eventid'}.'.txt');
@d=<SISAAN>;
close(SISAAN);

$out = '';
foreach $rec (@d){
    chomp($rec);
    ($id,$pisteet)=split(/\|/,$rec);
    $pisteet=~ s/\r//g;
    $pisteet=~ s/\n//g;
    if ($in{"course"} == $id) {
        $out = '"1":"'.$pisteet.'"';
        last;
    }
}

if ($in{'athlete'} ne '') {
    open (SISAAN,'<'.$path.'kilpailijat_'.$in{'eventid'}.'.txt');
    @d=<SISAAN>;
    close(SISAAN);

    foreach $rec (@d) {
        chomp($rec);
        $rec =~ s/\"//g;
        $rec =~ s/\n//g;
        $rec =~ s/\r//g;
        @r=split(/\|/,$rec);
        if ($in{'athlete'} eq $r[0]) {
            @r = split(';', $r[-1]);
            $out .= ',"athlete":'.scalar(@r);
            last;
        }
    }
}

print "{$out}\n";