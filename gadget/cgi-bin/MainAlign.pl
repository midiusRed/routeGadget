#!/usr/bin/perl

# if not, then java ui
$in{'eventid'}=1*$in{'id'};
open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);
foreach $rec (@kartat) {
    chomp($rec);
    ($eventid,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes,$eventmode)=split(/\|/,$rec);
    if ($eventid eq $in{'eventid'}) {
        $eventname = $paiva.' '.$nimi;
        last;
    }
}
if($in{'eventid'}==0){$in{'eventid'}=0;$eventid=0;$karttaid=0;$tyyppi=0;}

($imwidth, $imheight, $format) = ImageSize($path.$karttaid.'.jpg');


open (SISAAN,"<$path/../mappage.html");

@page=<SISAAN>;
close(SISAAN);
$page=join('',@page);

$title="$eventname";

$notes= "<b>$eventname</b><br><br>$seura<br><br>$notes<br><br>";
if($in{'touch'} ne '1' && $in{'gps'} ne '1'){
    $notes.="<a href=\"\#\" onClick=\"document.location=(document.location+'&touch=1').replace('#','')\"><b class=\"touchbig\">&gt;&gt;Touch mode</b></a>"
}
$notes =~ s/\"//gi;
$notes =~ s/\\//gi;

$page=~ s/#eventid#/${eventid}/gi;
$page=~ s/#eventtype#/${tyyppi}/gi;
$page=~ s/#eventname#/${eventname}/gi;
$page=~ s/#mapid#/${karttaid}/gi;
$page=~ s/#mapheight#/${imheight}/gi;
$page=~ s/#mapwidth#/${imwidth}/gi;
$page=~ s/#eventnotes#/${notes}/gi;
$page=~ s/#eventmode#/${eventmode}/g;
$page=~ s/#title#/${title}/gi;
$page=~ s/#httppath#/${httppath}/gi;
$page=~ s/#ext#/${extension}/gi;
$page=~ s/#GPSDATA#//;
$page=~ s/#GPSSPLITS#/0/;
$GPSMODE=1*$GPSMODE;
$page=~ s/#GPSMODE#/0/;
$page=~ s/#GPSRATA#/0/;
$page=~ s/#GPSCLASS#/0/;
$page=~ s/#GPSATHLETE#/0/;

$page=~ s/#viewport#//gi;
$page=~ s/#touchmode#/0/gi;


$page=~ s/#zip#/0/gi;


### language parameters


open (SISAAN,"<".$path."/../languages.txt");
#binmode(SISAAN, ":utf8");
@terms=<SISAAN>;
close(SISAAN);

$langs="<option value=''>lang</option>\n";


foreach $rec (@terms) {
    chomp($rec);
    $rec=~ s/\n//g;
    $rec=~ s/\r//g;
    if($rec =~ /\=/ ){
        ($name,$rec)=split(/\=/,$rec,2);
        ($pois,$text,$pois)=split(/\"/,$rec,3);
        $name=~ s/ //g;
        if($name =~ /\_/){
            $term{$name}=$text;
            ($lang,$nro)=split(/\_/,$name);
            if($islang{$lang} eq ''){
                $langs.="<option value='$lang'>$lang</option>\n";
                $islang{$lang}=1;
            }
        }
    }
}

#####

$lang=$in{'lang'};
if($lang eq ''){
    $lang=$defaultlang;
}

for($i=0;$i<90;$i++){
    $s='term_'.$i;
    $r=$term{$lang.'_'.$i};
    if($term{$lang.'_'.$i} eq ''){
        $r=$term{'eng_'.$i};
    }
    $page=~ s/#${s}#/${r}/g;

}

$page=~ s/#languages#/${langs}/g;
$page=~ s/#lang#/${lang}/g;


####
print $page;