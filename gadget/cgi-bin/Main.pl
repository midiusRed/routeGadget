#!/usr/bin/perl

$in{'eventid'}=1*$in{'id'};

open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);
foreach $rec (@kartat) {
    chomp($rec);
    ($eventid,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes,$eventmode)=split(/\|/,$rec);
    if ($eventid eq $in{'eventid'}) {
        $eventname=$paiva.' '.$nimi;
        last;
    }
}
if($in{'eventid'}==0){$in{'eventid'}=0;$eventid=0;$karttaid=0;$tyyppi=0;}

($imwidth, $imheight, $format) = ImageSize($path.$karttaid.'.jpg');

### is archived event
$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" ||  $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){
    if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
        $archived=1;$in{'gps'}='';
    }else{
        require  IO::Uncompress::Unzip;
        import  IO::Uncompress::Unzip;

        $zipfile = $path."archive.zip";
        if(-e $path."archive_".$in{'eventid'}.".zip"){
            $zipfile = $path."archive_".$in{'eventid'}.".zip";
        }

        $u = new IO::Uncompress::Unzip $zipfile
            or die "Cannot open $zipfile: $UnzipError";
        $status2=1;

        for ($status = 1; $status > 0 && $status2 == 1 ; $status = $u->nextStream())
        {
            $prename=$name; $name = $u->getHeaderInfo()->{Name};
            if($name eq "sarjat_$in{'eventid'}.txt"){
                $archived=1;$in{'gps'}='';
            }
            if($prename eq $name){$status2=0;}
        }
        #print "#$name $status ";
        if($archived==0){
            #  such event does not exists
            exit;
        }
    }
}

########
$gpsdata='';
### GPS start
if($in{'gps'} ==1){ ## gps asemointi
    $GPSATHLETE=1*$in{'kilpailijagps'};
    open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt");

    while (defined ($rec = <SISAAN>)) {
        chomp($rec);
        ($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$sija,$tulos,$valiajat)=split(/\|/,$rec);

        if($id eq $in{'kilpailijagps'}){
            $valiajat=~ s/\r//g;
            $valiajat=~ s/\n//g;
            $GPSSPLITS=$valiajat;
            if(substr($GPSSPLITS,-1) ne ';'){
                $GPSSPLITS.=';';
            }
            $gpsclass=$sarjanro;
            if($tyyppi ne '3'){
                $gpsrata=$sarjanro;

            }else{
                $gpsrata=$sija;
            }
        }
    }
    close SISAAN;


    open(SISAAN, "<".$path."ratapisteet_$in{'eventid'}.txt");
    @d=<SISAAN>;
    close(SISAAN);

    foreach $rec (@d){
        chomp($rec);
        ($id,$rastit)=split(/\|/,$rec,2);
        if($id eq $gpsrata){
            $rpisteet=$rastit;
        }
    }

    $GPSSPLITS.='|'.$rpisteet;

    if($tyyppi eq '2'){
        $in{'calibtype'} = 'manual';
        $gpsrata=$in{'sarjagps'};
    }

    $GPSMODE=0;
    if($in{'calibtype'} eq 'manual'){
        $GPSMODE=1;

        ### pre calibrated map parameters

        open(HANDLE, "<".$path."kartat.txt")|| die;
        @kdata=<HANDLE>;
        close(HANDLE);
        $coord[0]='';
        $coord[4]='';

        foreach $rec (@kdata){
            chomp($rec);
            ($mapid,$mapname)=split(/\|/,$rec);
            if($karttaid eq $mapid){
                ($a,$b,$c,$s1x,$o1x,$s1y,$o1y,$s2x,$o2x,$s2y,$o2y,$s3x,$o3x,$s3y,$o3y)=split(/\|/,$rec);

                if($o1x != 0){

                    $s1y=-$s1y;
                    $s2y=-$s2y;
                    $s3y=-$s3y;

                    $lat0=$o1y;
                    $lon0=$o1x;
                    $kaavao1y=$o1y;
                    $kaavao1x=$o1x;

                    $r=6370000;
                    $pi=3.1415926535897932384626433832795;


                    $lat=$o1y;
                    $lon=$o1x;
                    $north= (($lat-$lat0)/360*2*$pi*$r);
                    $east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
                    $o1y=$north;
                    $o1x=$east;

                    $lat=$o2y;
                    $lon=$o2x;
                    $north= (($lat-$lat0)/360*2*$pi*$r);
                    $east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
                    $o2y=$north;
                    $o2x=$east;

                    $lat=$o3y;
                    $lon=$o3x;
                    $north= (($lat-$lat0)/360*2*$pi*$r);
                    $east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
                    $o3y=$north;
                    $o3x=$east;

                    $xnolla1=$o1x;
                    $ynolla1=$o1y;
                    $xi=$o2x-$xnolla1;$yi=$o2y-$ynolla1;$xj=$o3x-$xnolla1;$yj=$o3y-$ynolla1;

                    $xnolla=$s1x;
                    $ynolla=$s1y;
                    $x1 = $s2x-$xnolla;$y1 = $s2y-$ynolla;$x2 = $s3x-$xnolla;$y2 = $s3y-$ynolla;


                    #nollalla jakamisen esto
                    if($xj==0){$xj=0.000000000001;}
                    if($yj==0){$yj=0.000000000001;}
                    if(($xj * $yi - $yj * $xi)==0){$xj=$xj+0.000000000001;}
                    if(($yj * $xi - $xj * $yi)==0){$yj=$yj+0.0000000000001;}

                    $Gb = ($x1 * $xj - $x2 * $xi) / ($xj * $yi - $yj * $xi);
                    $Ga = ($x2 - $Gb * $yj) / $xj;

                    $Gd = ($y1 * $yj - $y2 * $yi) / ($yj * $xi - $xj * $yi);
                    $Gc = ($y2 - $Gd * $xj) / $yj;


                }
            }
        }



    }

    #################### track log processing
    $pi=3.1415926535897932384626433832795;
    $q = $in{CGI};

    if($in{'gpsurl'} =~ /http/i){
        require LWP::UserAgent;

        $ua = LWP::UserAgent->new;
        $ua->timeout(10);
        $ua->max_size(10485760); # 10 Mb;
        $response = $ua->get($in{'gpsurl'});

        if ($response->is_success) {
            $d= $response->decoded_content;  # or whatever
        } else {
            die $response->status_line;
            exit;
        }

    }else{
        $file = $q->param('tracklog');
        binmode $file;
        @d =<$file>;
        close($file);

        $d= join('',@d);
    }


    $pi=3.1415926535897932384626433832795;
    if($d =~ /\<gpx/i && $d =~ /\<trkpt/i){ ## gpx

        $GPSparam='';

        $splitter="<trkpt";


        ($pois, $d)=split(/<trkpt/,$d,2);
        @trackpoints=split(/<trkpt/,$d);

        $lat0=-987654;

        foreach $point (@trackpoints){

            $lat=-9999999;
            $lon=-9999999;
            $alt=-9999999;

            $point=~ s/Time/time/gi;

            $p1=index($point,'<time>');
            $p2=index($point,'</time>');
            if($p1>-1 && $p2>-1){
                #<Time>2006-04-01T05:00:05Z</Time>

                $tim=substr($point,$p1+6,$p2-$p1-6);
                $tim=~ s/Z//g;
                $tim=~ s/\-/\:/g;
                $tim=~ s/T/\:/g;
                ($tyear,$tmon,$tday,$thour,$tmin,$tsec)=split(/\:/,$tim);
                $tim=3600*$thour+60*$tmin+floor($tsec);
                $day=$tyear.'_'.$tmon.'_'.$tday;

            }

            $p1=index($point,"lat=\"");
            $p2=index($point,"\"",$p1+6);
            if($p1>-1 && $p2>-1){
                $lat=substr($point,$p1+5,$p2-$p1-5);
                $lat =~ s/ //g;
                $lat =~ s/\"//g;
            }

            $p1=index($point,"lon=\"");
            $p2=index($point,"\"",$p1+6);
            if($p1>-1 && $p2>-1){
                $lon=substr($point,$p1+5,$p2-$p1-5);
                $lon =~ s/ //g;
                $lon =~ s/\"//g;
            }

            $p1=index($point,'<ele>');
            $p2=index($point,'</ele>');
            if($p1>-1 && $p2>-1){
                $alt=substr($point,$p1+4,$p2-$p1-4);
                $alt =~ s/ //g;
                $alt=1*$alt;

            }

            if($lat!=-9999999 && $lon !=-9999999){

                $count++;
                if($lat0==-987654){
                    $lat0=$lat;
                    $lon0=$lon;
                    $daycount=0;

                    $tim0=$tim;
                    $day0=$day;
                }

                ## this not very scientific, byt must do for now ...
                $r=6370000;
                $northing=-floor(($lat-$lat0)/360*2*$pi*$r*100)/100;
                $easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi)*100)/100;

                if($day0 ne $day){
                    $day0 = $day;
                    $daycount++;
                }
                $tim=$tim+$daycount*60*60*24-$tim0;

                if($Ga ne ''){

                    #($lon,$lat)=($lat,$lon);
                    $lat0=$kaavao1y;
                    $lon0=$kaavao1x;

                    $north= (($lat-$lat0)/360*2*$pi*$r);
                    $east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
                    $easting = floor(100*($s1x+ ((($Ga*($east-$xnolla1) + $Gb*($north-$ynolla1))))))/100;
                    $northing= -floor(100*($s1y+ ((($Gc*($north-$ynolla1) + $Gd*($east-$xnolla1))))))/100;
                }

                $GPSparam.="$tim,$easting,$northing;";
                if($mineast>$easting){$mineast=$easting;}
                if($maxeast<$easting){$maxeast=$easting;}
                if($minnorth>$northing){$minnorth=$northing;}
                if($maxnorth<$northing){$maxnorth=$northing;}
            }
        }

        @ad=split(/\;/,$GPSparam);

        $GPSparam='';
        foreach $pt (@ad){
            @r=split(/\,/,$pt);
            if(  $r[0]>$edtim){
                if($edtim +60*60*2 < $r[0]){exit;}
                if($edtim ne '' && $edtim +1 < $r[0] ){

                    for($i=$edtim+1;$i<$r[0];$i++){

                        $tim=$i;
                        $easting=floor(100*(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast))/100;
                        $northing=floor(100*(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth))/100;

                        $GPSparam.="$tim,$easting,$northing;";
                    }
                }

                $GPSparam.=join(',',@r).";";
            }

            $edtim=$r[0];
            $edeast=$r[1];
            $ednorth=$r[2];
        }

    } # GPX


    if($d =~ /\<Samples\>/i && $d =~ /\<Longitude\>/i){  # suunto xml
        ($pois,$d)=split(/\<Sample\>/i,$d,2);
        $out='';
        @d=split(/\<Sample\>/i,$d);

        $lat0=-987654;

        foreach $rec (@d){

            ($pois,$lat)=split(/Latitude\>/i,$rec,2);
            ($lat,$dat)=split(/\</,$lat,2);


            ($pois,$lon)=split(/Longitude\>/i,$rec,2);
            ($lon,$dat)=split(/\</,$lon,2);



            ($pois,$utc)=split(/\<UTC\>/i,$rec,2);
            ($tim,$pois)=split(/\</,$utc,2);
            $tim=~ s/Z//g;
            $tim=~ s/\-/\:/g;
            $tim=~ s/T/\:/g;
            ($tyear,$tmon,$tday,$thour,$tmin,$tsec)=split(/\:/,$tim);
            $tsec=floor($tsec);
            $tim=3600*$thour+60*$tmin+$tsec;
            $day=$tyear.'_'.$tmon.'_'.$tday;


            if($lat ne '' && $lon ne ''){
                $lat=360*$lat/2/$pi;
                $lon=360*$lon/2/$pi;

                $count++;
                if($lat0==-987654){
                    $lat0=$lat;
                    $lon0=$lon;
                    $daycount=0;

                    $tim0=$tim;
                    $day0=$day;
                }

                ## this not very scientific, byt must do for now ...
                $r=6370000;
                $northing=-floor(($lat-$lat0)/360*2*$pi*$r*100)/100;
                $easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi)*100)/100;

                if($day0 ne $day){
                    $day0 = $day;
                    $daycount++;
                }
                $tim=$tim+$daycount*60*60*24-$tim0;

                if($Ga ne ''){

                    #($lon,$lat)=($lat,$lon);
                    $lat0=$kaavao1y;
                    $lon0=$kaavao1x;

                    $north= (($lat-$lat0)/360*2*$pi*$r);
                    $east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
                    $easting = floor(100*($s1x+ ((($Ga*($east-$xnolla1) + $Gb*($north-$ynolla1))))))/100;
                    $northing= -floor(100*($s1y+ ((($Gc*($north-$ynolla1) + $Gd*($east-$xnolla1))))))/100;
                }

                $GPSparam.="$tim,$easting,$northing;";
                if($mineast>$easting){$mineast=$easting;}
                if($maxeast<$easting){$maxeast=$easting;}
                if($minnorth>$northing){$minnorth=$northing;}
                if($maxnorth<$northing){$maxnorth=$northing;}
            }
        }

        @ad=split(/\;/,$GPSparam);

        $GPSparam='';
        foreach $pt (@ad){
            @r=split(/\,/,$pt);
            if(  $r[0]>$edtim){
                if($edtim +60*60*2 < $r[0]){exit;}
                if($edtim ne '' && $edtim +1 < $r[0] ){

                    for($i=$edtim+1;$i<$r[0];$i++){

                        $tim=$i;
                        $easting=floor(100*(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast))/100;
                        $northing=floor(100*(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth))/100;

                        $GPSparam.="$tim,$easting,$northing;";
                    }
                }

                $GPSparam.=join(',',@r).";";
            }
            $edtim=$r[0];
            $edeast=$r[1];
            $ednorth=$r[2];
        }
    }

    @d=split(/\;/,$GPSparam);

    if(@d < 3){
        print "No track points found. File format may not be correct. GPX and Suunto XML files are supported. <p>Reittiä ei saatu luettua. Tarkista, että tiedoto oli joko GPX tai Suunto XML tiedosto.";
        exit;

    }

    if($Ga eq ''){ # not if map is geo-referenced
        ### scale it to the center of the map
        $gpsdata='';
        @d=split(/\;/,$GPSparam);
        $size=$imheight/($maxnorth-$minnorth);
        $side=$imheight;
        if($imwidth/($maxeast-$mineast)<$size){
            $size=$imwidth/($maxeast-$mineast);
            $side=$imwidth;
        }

        foreach $rec (@d){
            ($t,$e,$n)=split(/\,/,$rec);

            $e=floor(($side*0.1+($e-$mineast)*$size*0.8)*100)/100;

            $n=floor(($side*0.1+($n-$minnorth)*$size*0.8)*100)/100;

            $gpsdata.="$t,$e,$n;";
        }

    }else{
        $gpsdata=$GPSparam;
    }



    # geo locate event

    if($geolocateevent == 1){

        open (SISAAN,"<$path/eventlocations.txt");
        @elocat=<SISAAN>;
        close(SISAAN);
        $posexist=0;
        foreach $eventl (@elocat){
            ($enumb,$elat,$elon)=split(/\|/,$eventl);
            if($enumb == $eventid){
                $posexist=1;
            }
        }
        if($posexist==0){

            open (HANDLE,">>"."$path/eventlocations.txt");
            &lock_file;
            print HANDLE $eventid."|".$lat0."|".$lon0."\n";
            &unlock_file;
            close HANDLE;

        }
    }
}
### GPS end

open (SISAAN,"<$path/../mappage.html");

@page=<SISAAN>;
close(SISAAN);
$page=join('',@page);

$title="$eventname";

if (length($notes) > 0) { $notes .= "<br>"; }
if (length($seura) > 0) { $notes = "$seura<br>".$notes; }
$notes= "<p style=\"max-width:350px\"><b>$eventname</b></p>".$notes."<td style=\"vertical-align: middle;\">";

if($in{'touch'} ne '1' && $in{'gps'} ne '1'){
    $notes.="<br><a href=\"\#\" onClick=\"document.location=(document.location+'&touch=1').replace('#','')\"><b class=\"touchbig\">&gt;&gt;Ñåíñîðíûé ðåæèì</b></a>"
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
$page=~ s/#GPSDATA#/${gpsdata}/;
$page=~ s/#GPSSPLITS#/${GPSSPLITS}/;
$GPSMODE=1*$GPSMODE;
$page=~ s/#GPSMODE#/${GPSMODE}/;
$page=~ s/#GPSRATA#/${gpsrata}/;
$page=~ s/#GPSCLASS#/${gpsclass}/;
$page=~ s/#GPSATHLETE#/${GPSATHLETE}/;

if($in{'touch'} ne ''){
    $viewport="<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,maximum-scale=1,minimum-scale=1\">";
    $page=~ s/#viewport#/${viewport}/gi;
    $page=~ s/#touchmode#/1/gi;
}else{
    $page=~ s/#viewport#//gi;
    $page=~ s/#touchmode#/0/gi;
}


$page=~ s/#zip#/${archived}/gi;


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

## disabling multiselect for ipad iphone
if($ENV{HTTP_USER_AGENT} =~ /ipad/i || $ENV{HTTP_USER_AGENT} =~ /iphone/i){
    $s='\(\"\#kilp\"\)\.MultiSelect';
    $r='("#kilp_disabled").MultiSelect';
    $page=~ s/${s}/${r}/;
}

####
print $page;