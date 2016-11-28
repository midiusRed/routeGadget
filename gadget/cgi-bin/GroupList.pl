#!/usr/bin/perl
$eventid=$in{'eventid'}*1;
$scale = 7500;
$dpi = 300;

if($in{'zip'}==1){
    if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
        require Compress::Zlib;
        import Compress::Zlib;

        $gz = gzopen($path."kommentit_".$eventid.".txt.gz", "rb");
        $data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
        @kommentit=split(/\n/,$data);

        $gz = gzopen($path."sarjat_".$eventid.".txt.gz", "rb");
        $data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
        @d=split(/\n/,$data);
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

        for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream()){
            $prename=$name; $name = $u->getHeaderInfo()->{Name};

            if($name eq "kommentit_$in{'eventid'}.txt"){
                $data='';
                while (($status = $u->read($buff)) > 0) {
                    $data.=$buff;
                }
                @kommentit=split(/\n/,$data);
            }
            if($name eq "sarjat_$in{'eventid'}.txt"){
                $data='';
                while (($status = $u->read($buff)) > 0) {
                    $data.=$buff;
                }
                @d=split(/\n/,$data);
            }
            if($prename eq $name){$status2=0;}

        }
    }
    @sl = ();
    @ratapisteet=();
} else {
    open (SISAAN,"<$path"."kommentit_$in{'eventid'}.txt");
    @kommentit=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<".$path."sarjat_".$eventid.".txt"); #�������� �����
    @d=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<".$path."kilpailijat_".$eventid.".txt");
    @sl=<SISAAN>; #split list
    close(SISAAN);

    open (SISAAN,"<$path"."ratapisteet_$in{'eventid'}.txt");
    @ratapisteet=<SISAAN>;
    close(SISAAN);

    open (SISAAN,"<".$path."kisat.txt");
    @kartat=<SISAAN>;
    close(SISAAN);

    foreach $rec (@kartat) {
        chomp($rec);
        @mapList=split(/\|/,$rec);
        if ($mapList[0] eq $in{'eventid'}) {
            $map_id = $mapList[1];
            last;
        }
    }

    if (open(SISAAN, "<".$path."kartat_dpi.txt")) {
        @data_dpi=<SISAAN>;
        close(SISAAN);

        foreach $rec (@data_dpi) {
            ($id,$scale_map,$dpi_map) = split(/\|/, $rec);
            if ($id eq $map_id) {
                $scale = int($scale_map);
                $dpi = int($dpi_map);
                last;
            }
        }
    }
}

## lasketaan montako piirrosta on miss�kin sarjassa

foreach $rec (@kommentit) {
    chomp($rec);
    ($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$rec);
    $i++;

    $lkm{$idkilp}++;
}

$i = 0;
foreach $rec (@d) {
    chomp($rec);
    $rec =~ s/\"//g;
    $rec =~ s/\n//g;
    $rec =~ s/\r//g;
    @r=split(/\|/,$rec);
    $count = 0;
    foreach $splitValue (@sl) {
        if (index($splitValue, $r[1]) != -1) {
            $count++;
        }
    }
    ($id,$nimi) = split(/\|/,$ratapisteet[$i]); #�������� ������ (x,y) ��
    $i++;
    $pituus=0; #����� px
    $j = 0; #���������� ��
    $x0 = 0;
    $y0 = 0;
    chomp($nimi);
    foreach $id (split(/N/, $nimi)) {
        ($tx,$ty)=split(/\;/,$id);
        if ($j > 0) {
            $pituus += sqrt(($x0-$tx)*($x0-$tx)+($y0-$ty)*($y0-$ty));
        }
        $x0 = $tx;
        $y0 = $ty;
        $j++;
    }
    $j -= 2; #����� ����� � �����
    $pituus = floor((($pituus / ($dpi / 2.54)) * $scale) / 1000) / 100; #�������� ���������� � ��

    $rec = "{\"$r[0]\":\"$r[1] (".(1*$lkm{$r[0]})."/$count) $pituus�� $j��\"}";
}
print '['.join(',',@d)."]\n";