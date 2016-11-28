#!/usr/bin/perl
$sarja=1*$in{'sarja'};
$eventid=$in{'eventid'}*1;

$totpit[0]=0;
$splited[0][0]=0;
$viiva[0]='';
$rast[0]='';
$nim[0]='';
$ids[0]=0;
$idi[0]=0;
$celi[0]=0;
$gid[0]=0;

if($in{'zip'}==1){

    if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
        require Compress::Zlib;
        import Compress::Zlib;

        $gz = gzopen($path."merkinnat_".$in{'eventid'}.".txt.gz", "rb");
        $data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
        @merkinnat=split(/\n/,$data);

        $gz = gzopen($path."kilpailijat_".$in{'eventid'}.".txt.gz", "rb");
        $data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
        @kilpailijat=split(/\n/,$data);


    }else{

        require  IO::Uncompress::Unzip;
        import  IO::Uncompress::Unzip;
        $zipfile = $path."archive.zip";
        if(-e $path."archive_".$in{'eventid'}.".zip"){
            $zipfile = $path."archive_".$in{'eventid'}.".zip";
        }
        $u = new IO::Uncompress::Unzip $zipfile or die "Cannot open $zipfile: $UnzipError";
        $status2=1;

        for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
        {
            $prename=$name; $name = $u->getHeaderInfo()->{Name};

            if($name eq "merkinnat_$in{'eventid'}.txt"){
                $data='';
                while (($status = $u->read($buff)) > 0) {
                    $data.=$buff;
                }
                @merkinnat=split(/\n/,$data);
            }
            if($name eq "kilpailijat_$in{'eventid'}.txt"){
                $data='';
                while (($status = $u->read($buff)) > 0) {
                    $data.=$buff;
                }
                @kilpailijat=split(/\n/,$data);
            }
            if($name eq "ratapisteet_$in{'eventid'}.txt"){
                $data='';
                while (($status = $u->read($buff)) > 0) {
                    $data.=$buff;
                }
                @ratapisteet=split(/\n/,$data);
            }

            if($prename eq $name){$status2=0;}
        }
    }
} else {
    open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
    @merkinnat=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<$path"."ratapisteet_$in{'eventid'}.txt");
    @ratapisteet=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<".$path."kilpailijat_$in{'eventid'}.txt");
    @kilpailijat=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<".$path."kisat.txt");
    @kartat=<SISAAN>;
    close(SISAAN);

    $viesti = 0;
    $map_id = ''; #ид карты, чтобы вычитать scale, dpi
    foreach $rec (@kartat) {
        chomp($rec);
        @mapList = split(/\|/,$rec);
        if ($mapList[0] eq $in{'eventid'}) {
            if ($mapList[2] == 3) {
                $viesti = 1;
            }
            $map_id = $mapList[1];
            last;
        }
    }

    $scale = 7500;
    $dpi = 300;
    #scale и dpi хранятся в отдельном файле
    if ($map_id ne '' && open(SISAAN,"<".$path."kartat_dpi.txt")) {
        @dpiList = <SISAAN>;
        close(SISAAN);
        foreach $rec (@dpiList) {
            ($id,$map_scale,$map_dpi) = split(/\|/, $rec);
            if ($map_id eq $id) {
                $scale = $map_scale;
                $dpi = $map_dpi;
                last;
            }
        }
    }

    $kilp=1;

    foreach $rec (@merkinnat){ #обходим список путей
        chomp($rec);

        ($idkilp,$id,$nimi,$aika,$viivat,$rastito)=split(/\|/,$rec);
        if($id<50000){
            $ss=$id;
            $gid[$kilp]=0;
        }else{
            $ss=$id-50000;
            $gid[$kilp]=50000;
        }
        $viiva[$kilp]=$viivat;


        if($aika==nil){
            $celi[$kilp]=$idkilp;
        }else{
            $celi[$kilp]=$aika;
        }
        $nim[$kilp]=$nimi;
        $ids[$ss]=$kilp;
        $totpit[$kilp]=0;
        $kilp++;
    }
    $nn=$kilp;

    @distanceCoordsList = ();
    foreach $rec (@ratapisteet){
        chomp($rec);
        ($id,$rastit)=split(/\|/,$rec);
        push(@distanceCoordsList, $id, $rastit);
    }

    #$kilp=1;
    #while($kilp<$nn){
    #    $rast[$kilp]=$rasta[$celi[$kilp]];
    #    $kilp++;
    #}

    ## distance calculation
    $kilp=1;

    while($kilp<$nn){
        #if($viiva[$kilp] ne ''){


        #if($in{"k".$kilp}<100000){
        @reitti=split(/N/,$viiva[$kilp]); #находим дистанцию
        # @trast=split(/N/,$rast[$kilp]);
        $i = $#distanceCoordsList - 1; #здесь $i используется как итератор списка
        while ($i >= 0) {
            if ($distanceCoordsList[$i] == $celi[$kilp]) {
                @trast=split(/N/, $distanceCoordsList[$i + 1]);
                break;
            }
            $i -= 2;
        }

        if($gid[$kilp]==50000){
            $dd=20;
        }else{
            $dd=5;
        }

        $i=0; #индекс КП

        ($rx,$ry)=split(/\;/,@trast[$i]); #точка расположения старта
        $x0=0;
        $y0=0;
        $j=0;
        $pituus=0; #пройденное расстония до КП
        $totpit[$kilp]=0; #общее расстояние

        foreach $rec (@reitti){
            ($tx,$ty)=split(/\;/,$rec);

            if($j>0){
                $d=sqrt(($x0-$tx)*($x0-$tx)+($y0-$ty)*($y0-$ty));
                if($d>=3){
                    $x0=$tx;$y0=$ty;
                    if($i>0){
                        $pituus=$pituus+$d;
                    }
                }
            }else{
                $x0=$tx;$y0=$ty;
                $j=1;
            }

            if((abs($tx-$rx)<$dd)&&(abs($ty-$ry)<$dd)){
                #dpi - количество точек на 1 дюйм (2.54см)   300 / 2.54 =  118.11   1 == 7500 см   ((dist / (dpi / 2.54)) * scale) / 100
                $pituus = (($pituus / ($dpi / 2.54)) * $scale) / 100;
                $splited[$kilp][$i]=floor($pituus);
                $totpit[$kilp]+=floor($pituus);
                $pituus=0;
                $i++;
                ($rx,$ry)=split(/\;/,@trast[$i]); #позиция следующего кп
            }
        }

        #}
        #}
        $kilp++;
    }
}

$gpsid=',';
@temp=split(/\,/,$in{'kilp'});
foreach $rec (@temp){
    if($rec > 50000){
        $rec=$rec-50000;
    }
    $gpsid.=$rec.',';
}

$in{'kilp'}=','.$gpsid.',';

$nro=1;
$otsikko="<tr><td><a href=\"reitti.".$extension."?act=splitsbrowserjs&id=$eventid\" target=\"SPLITSBROWSER\">&gt;&gt;График сплитов</a></td>";

foreach $rec (@kilpailijat){
    chomp($rec);
    ($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$sija,$tulos,$valiajat)=split(/\|/,$rec);
    $s=','.${id}.',';

    @splits=split(/\;/,$valiajat);

    if($in{'kilp'} =~ /${s}/){

        $old=0;
        if($nro==1){
            $i=1;
        }
        $j=-1;
        $nimi=~ s/ /\&nbsp\;/g;
        $ulos="<tr><td onMouseover=\"hilitetrack($id+$gid[$ids[$id]]);\" onMouseOut=\"hilitegroup.clearLayers();\">".$nimi."|".$totpit[$ids[$id]]."м</td>";

        foreach $rec (@splits){
            chomp($rec);
            if($nro==1){
                $otsikko=$otsikko."<td>".$i."</td>";
                $i++;
            }
            $j++;
            $min=floor(($rec-$old)/60);
            $sec=($rec-$old)-60*floor(($rec-$old)/60);
            if ($sec <10) {$sec='0'.$sec;}
            $old=$rec;
            $kk=$splited[$ids[$id]][$j+1];
            $ulos=$ulos."<td onMouseover=\"hilitetrack($id+$gid[$ids[$id]],$j);\" onMouseOut=\"hilitegroup.clearLayers();\">$min.$sec | $kk</td>";
        }
        if($nro==1){
            $out.= "$otsikko</tr>\n";
        }
        $out.= "$ulos";
        if($i==$j){
            $out.= "<td>$nimi</td></tr>\n";
        }
        $nro++;
    }
}

###
$out=~ s/\"//g;
$out=~ s/\n//g;
utf8::decode($out);
print "[{\"1\":\"<table border='1' class='ctd'>$out</table>\"}]\n";