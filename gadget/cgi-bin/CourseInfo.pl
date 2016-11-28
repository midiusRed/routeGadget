#!/usr/bin/perl
$in{'eventid'}=1*$in{'eventid'};
$out = '';

open (SISAAN,"<$path"."radat_$in{'eventid'}.txt");
@d=<SISAAN>;
close(SISAAN);

if($in{"hajonnat"} ne ''){
    $in{"hajonnat"}=','.join(',',&uniq(split(/\,/,$in{"hajonnat"}))).',';
    $in{"hajonnat"}=','.$in{"hajonnat"}.',';

    foreach $rec (@d){
        chomp($rec);
        ($id,$status,$nimi,$viivat)=split(/\|/,$rec);
        if (index($in{"hajonnat"},','.$id.',')>-1){
            $viivat =~ s/R//g;
            $viivat =~ s/#//g;

            @tmp=split(/N/,$viivat);
            $viivat='';
            foreach $e (@tmp){
                if($yes{$e} eq ''){
                    $yes{$e}=1;
                    $viivat.='N'.$e;
                }
            }
            $out.= "$viivat"."N";
        }
    }
} else {
    foreach $rec (@d){
        chomp($rec);
        ($id,$status,$nimi,$viivat) = split(/\|/,$rec);
        if ($in{"sarja"} == $id || $in{"sarja"} eq '99999'){
            $viivat =~ s/R//g;
            $viivat =~ s/#//g;
            if ($in{"sarja"} eq '99999') {
                @tmp=split(/N/,$viivat);
                $viivat = '';
                foreach $e (@tmp){
                    if($yes{$e} eq ''){
                        $yes{$e} = 1;
                        $viivat .= $e.'N';
                    }
                }
            }
            $out .= $viivat;
        }
    }
}
$out =~ s/\r//g;
print "[{\"courses\":\"$out\"}]\n";