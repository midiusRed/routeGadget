#!/usr/bin/perl
################################################################### 
#  reitti.cgi or reitti.pl                                        #           
###################################################################
# Reittihärveli   -      Sovellus suunnistuksen reittipiirrosten  #
#                           keräykseen  ja esittämiseen           #
# Distributed by: jryyppo <t gmail.com                            #
# ================================================================#
# Copyright (c) 2003-2014 Jarkko Ryyppö - All Rights Reserved.    #
# Software by:        Jarkko Ryyppö                               #
# Sponsored by:       -                                           #
$RG_version='20150203';
###################################################################
# The software is free for non-commercial use.  The software can  #
# be used only for purposes related to the sport of orienteering. #
#                                                                 #
# This program comes as it is. Use it at your own risk. This is   #
# software with ABSOLUTELY NO WARRANTY. This program is           #
# distributed in the hope that it will be useful, but             #
# WITHOUT ANY WARRANTY; without even the implied warranty of      #
# FITNESS FOR A PARTICULAR PURPOSE.                               #
#                                                                 #
# Developers of this software are not responsible for what the    #
# user does with help of this software.                           #
#                                                                 #
#     THE USER MUST NOT USE SOFTWARE FOR ILLEGAL ACTIONS.         #
#                                                                 #
# By installing and/or using our software, you agree with these   #
# terms of use.                                                   #
###################################################################
use CGI::Carp qw(fatalsToBrowser);
use Fcntl ":flock";
use POSIX;
use CGI qw(:cgi-lib :standard);
$CGI::POST_MAX=1024 * 10000;  # max 10000K posts
use POSIX qw(strftime);
use Encode;
ReadParse();

## default language for the new js UI:
$defaultlang='ru';

if($in{'act'} =~ /js/i || ($in{'act'} eq 'map' && $in{'keksi'} eq '' && $in{'java'} ne '1')){
#$charset_default='UTF-8';
$charset_default='WINDOWS-1251';
#binmode(STDOUT, ":utf8");
#binmode(STDOUT, ":raw:perlio");
## overkill no-no-never-ever-cache approach
print header(
-type=>"text/html; charset=".$charset_default,
    # date in the past
    -expires       => 'Sat, 26 Jul 1997 05:00:00 GMT',
    # always modified
    -Last_Modified => strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime),
    # HTTP/1.0
    -Pragma        => 'no-cache',
    # HTTP/1.1 + IE-specific (pre|post)-check
    -Cache_Control => join(', ', qw(
        private
        no-cache
        no-store
        must-revalidate
        max-age=0
        pre-check=0
        post-check=0
    )),
);
}else{
##
@languages=('en','ru');

## You can add new languages by (1)adding new item here, (2) adding language texts with 
## correct parameter names to map.txt (like <param name=en_11 value="Zoom">) 
## and making new file "lang_YOURLANGUAGE.txt"   
## (you can figure it out with these examples I hope)
##
## 1. Default language: (choices are currently 'ca','de','ee','en','es','fi','fr','he','lt','lv','no','ru','se')
$default_lang='ru';

##  
## Default charset:
#$charset_default='ISO-8859-1';
$charset_default='WINDOWS-1251';

# Language spesific charsets:
## $charset{'fi'}='ISO-8859-1';  ## example
#$charset{'ru'}='WINDOWS-1251';

if($in{'act'} eq 'help'){
	if($charset{$in{'kieli'}} ne ''){
		$charset_default=$charset{$in{'kieli'}};
	}
}

print "Content-Type: text/html; charset=".$charset_default."\n\n";

}


$livepasswd=''; # password disabled if empty

if($in{'lang'} eq '' && $in{'kieli'} ne ''){
$in{'lang'}=$in{'kieli'};
}
#########################

##
## 2. File locking (turn this off if you get lock errors or 500 errors no matter what you do)
##
#$locking=1; # locking is on
$locking=0; # locking is off
##
## 3. Paths
## For UNIX, Linux:
 $path='../kartat/';	## file path to "kartat" folder
 $httppath='../';	## http path to the folder of leaflet.js, gadget.gif etc
##
## For IIS (Windows):
#$path='C:/inetpub/wwwroot/gadget/kartat/'; ## file path to "kartat" folder
# $httppath='../'; ## http path to the folder reitti.jar is located
## 
$norouteanim=1;
##
## Save event location using map calibration or gps uploads, so sites 
# like omaps.worldofo.com can geo locate map/event.  1=yes, 0 =no

$geolocateevent=1;

##
## 4.  OGraphApplet: 1=yes, 0 =no
$OGraphApplet=0;
##
## 5.  Splitsbrowser : 1=yes, 0 =no
$Splitsbrowser=1;
##
## 6.  Splitalyzer : 1=yes, 0 =no
$splitsalyzer=0;
##
## 7. Event level names:

# Default event level names
$eLevel{'I'}='Ìåæäóíàðîäíûå';
$eLevel{'N'}='Âñåðîññèéñêèå';
$eLevel{'R'}='Îáëàñòíûå';
$eLevel{'L'}='Ãîðîäñêèå';
$eLevel{'T'}='Òðåíèðîâî÷íûå';

# menu texts if not in Finnish:
$latestRoutes = 'Ïîñëåäíèå ïóòè';
$events = 'Ñîáûòèÿ:';
$latestEvents = 'Ïîñëåäíèå ñîáûòèÿ';
$eventsByOrg = 'Ñîáûòèÿ ïî êëóáàì';
$eventsByDate = 'Ñîáûòèÿ ïî äàòàì';

# default Club name (for pre-opening the menu tree);
$defaultClub='';
#$menuStyle='list';

# number of events to display on the index page
$display_in_index=25;
## Language specifics
if($in{'kieli'} eq 'en'){
	$eLevel{'I'}='International';
	$eLevel{'N'}='National';
	$eLevel{'R'}='Regional';
	$eLevel{'L'}='Local';
	$eLevel{'T'}='Training';
	$latestRoutes='Latest&nbsp;routes';
    $events='Events:';
    $latestEvents='Latest events';
    $eventsByOrg='Events by club';
    $eventsByDate='Events by date';
}

## GPS track sorting. 0= list gps tracks at the end of the list, 1 = list gpst track after drawn route, sortet by result
$GPSsort = 1;
#########################################################################################
if($httppath eq ''){$httppath='./';}

$gadgeticon=$httppath.'logo6.ico';

$logo=$httppath.'gadget.gif';
$piste=$httppath.'piste.gif';

## Check extension
$apu=$0;
$apu=~ s/\\/\//g;
@apu = split (/\//,$apu);
($remove,$extension)= split(/\./,$apu[$#apu]);
###################

#################### rgjs section begins#############################
$in{'eventid'}=1*$in{'eventid'};

## kohdistus
if($in{'act'} eq 'map' && $in{'keksi'} ne '' && $in{'java'} ne '1' && $in{'kohdistus'}== 1) {
	require 'MainAlign.pl';
	exit;
}

################# jskohdistus ####################
if ($in{"act"} eq "jskohdistus"){   
 open (SISAAN,"<$path"."rastikanta_$in{'eventid'}.txt");
 
print '[';
 
 $c=0;
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$x,$y)=split(/\|/,$rec);
       $x=($x*10); $y=($y*10);
if($c>0){
print ",{\"$c\":\"$x,$y\"}";
}else{
print "{\"$c\":\"$x,$y\"}";
}
$c++;
}
close(SISAAN); 
 print ']';
}
####
if($in{'act'} eq 'map' && $in{'keksi'} eq '' && $in{'java'} ne '1') {
	require 'Main.pl';
	exit;
}


###################################
#ñïèñîê ãðóïï
if($in{'act'} eq 'jsclassescourses'){
	require 'GroupList.pl';
	exit;
}

######################################
#ñôîðìèðîâàòü ñïëèòû
if($in{'act'} eq 'jskilp'){
	$in{'eventid'}=1*$in{'eventid'};

	if($in{'zip'}==1){
		if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
			require Compress::Zlib;
			import Compress::Zlib;

			$gz = gzopen($path."merkinnat_".$in{'eventid'}.".txt.gz", "rb");
			$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
			@merkinnat=split(/\n/,$data);

			$gz = gzopen($path."kilpailijat_".$in{'eventid'}.".txt.gz", "rb");
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
				@d=split(/\n/,$data);
			}
			if($prename eq $name){$status2=0;}
			}
		}
	}else{
		open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
		@merkinnat=<SISAAN>;
		close(SISAAN);

		open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt");
		@d=<SISAAN>;
		close(SISAAN);
	}

	## tarkistetan piirtäneet tähtimerkintää varten
	foreach $rec (@merkinnat) {
		chomp($rec);
		($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
		$tahti{$id}="*";
	}

	###
	#ñîðòèðóåì ïî âðåìåíè
	@d = sort by_splits_sort @d;
	sub by_splits_sort {
		my @a = split(':', (split(/\|/, $a))[7]);
		if (@a.length == 1) { push @a, 0; }
		my @b = split(':', (split(/\|/, $b))[7]);
		if (@b.length == 1) { push @b, 0; }
		($a[0] * 60 + $a[1]) <=> ($b[0] * 60 + $b[1]);
    }

	foreach $rec (@d) {
		chomp($rec);
		($id,$sarjanro,$sarja,$nimi,$laika,$aika,$sijahajonta,$tulos,$valiajat)=split(/\|/,$rec);

		if($sarjanro eq $in{'sarja'} || ($in{'sarja'} eq '99999' && $tahti{$id} eq '*')){
			#$runnerid=$id;if($id>50000){$runnerid=$id-50000+0.5;}
			if($in{'eventtype'} ne '3'){
				$out[$#out+1] = "{\"$id\":\"$tulos | $tahti{$id}$sijahajonta $nimi \"}";
			}else{
				$out[$#out+1] = "{\"$id\":\"$tulos | $tahti{$id} $nimi;$sijahajonta\"}";
			}
		}
	}

	# sort
	#if($GPSsort == 1){
	#	@out = sort { (split('\{', $a, 2))[0] <=> (split('\{', $b, 2))[0] } @out;
	#}
	##

	#foreach $rec (@out) {
	#	$rec='{'.(split '\{', $rec, 2)[1];
	#}

	$out= '['.join(',',@out)."]\n";
	$out=~ s/\r//g;
	utf8::decode($out);
	print $out;
	exit;
}
#####################
######################################### ñïèñîê ñïîðñòìåíîâ äëÿ ðèñîâàíèÿ ñâîåãî ïóòè
if($in{'act'} eq 'jskilppiirto'){
	require 'AthleteDrawInfo.pl';
	exit;
}

#####################################################################################
if($in{'act'} eq 'jsreitit'){

## tästä appletti lataa viivat
$in{'eventid'}=1*$in{'eventid'};
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

$gz = gzopen($path."ratapisteet_".$in{'eventid'}.".txt.gz", "rb");
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
	@d=split(/\n/,$data);
}
if($prename eq $name){$status2=0;}
}
}
}else{
open(SISAAN, "<".$path."kilpailijat_$in{'eventid'}.txt");
@kilpailijat=<SISAAN>;
close(SISAAN);

open(SISAAN, "<".$path."ratapisteet_$in{'eventid'}.txt");
@d=<SISAAN>;
close(SISAAN);

open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
@merkinnat=<SISAAN>;
close(SISAAN);
}


$gpsid=',';
@temp=split(/\,/,$in{'kilp'});
foreach $rec (@temp){

if($rec > 50000){
$rec=$rec-50000;
$gpsid.=$rec.',';
}
}
$kilp=','.join(',',@temp).',';

$in{'kilp'}=','.$in{'kilp'}.',';



foreach $rec (@kilpailijat){
	chomp($rec);
	($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$haj,$tulos,$valiajat,$GPSa)=split(/\|/,$rec);
$s=','.${id}.',';

if($kilp=~ /${s}/){
$valiajat=~ s/\r//g;
$valiajat=~ s/\n//g;
$valiajat{''.$id}=$valiajat;
$valiajat{''.($id+50000)}=$valiajat;
$hajonta{''.$id}=$haj;

}
if($in{'kilp'}=~ /${s}/){
$GPSa{''.$id}=$GPSa;
}
}



foreach $rec (@d){
chomp($rec);
($id,$rastit)=split(/\|/,$rec,2); 
$rpisteet{''.$id}=$rastit;
}


  
{
$i=0;$loytyi=0;
foreach $rec (@merkinnat) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
	$i++;
$s=','.$id.',';
if ($in{'kilp'} =~ /${s}/){

$i++;    
$viivat =~ s/R//g;
$viivat =~ s/#//g;
$viivat=~ s/N//;

if($id < 50000){
if($in{'eventtype'} == 3){
foreach $rasti (split(/N/,$rpisteet{''.$hajonta{''.$id}})){
$viivat =~s/N${rasti}N/N${rasti}C${rasti}N/;
}
}else{
foreach $rasti (split(/N/,$rpisteet{$idkilp})){
$viivat =~s/N${rasti}N/N${rasti}C${rasti}N/;
}
}
$out{$id}= "\{\"$id\":\"".$valiajat{''.$id}."S".$viivat."\"}";
}else{ # gps leg splitting
@temp=split(/\;/,$valiajat{''.$id});
@ani=split(/N/,$GPSa{''.$id});
$vout='';

foreach $sp (@temp){

$i=0;
while($i>-1 && $i<20){
$C=$ani[floor($sp/3)+$i];
$i++;
($C,$pois)=split(/\,/,$C);

if($viivat =~ /N${C}N/){
($a,$b)=split(/N${C}N/,$viivat,2);
$vout.=$a.'N'.$C.'C'.$C.'N';
$viivat =$b;
$i=-1;
}
}
#$viivat =~s/N${C}N/N${C}C${C}N/;
}
if($vout eq ''){
$out{$id}= "\{\"$id\":\"".$valiajat{''.$id}."S".$viivat."\"}";
}else{
$out{$id}= "\{\"$id\":\"".$valiajat{''.$id}."S".$vout.$b."\"}";
}
}

}
}
} 
print "[";
$count=0;
foreach   $id (reverse(split(/\,/,$in{'kilp'}))){
if($out{$id} ne ''){
if($count>0){print ",";}
$out{$id}=~ s/\r//g;
print $out{$id};
$count++;
}
}

print "]\n";
exit;
}

#####################################3
if($in{'act'} eq 'jsradat'){
	require 'CourseInfo.pl';
	exit;
}
###############################
if($in{'act'} eq 'jsanim'){

$in{'eventid'}=1*$in{'eventid'};
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

$gz = gzopen($path."ratapisteet_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@ratap=split(/\n/,$data);


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
	@ratap=split(/\n/,$data);
}
if($prename eq $name){$status2=0;}
}
}
}else{
open(SISAAN, "<".$path."ratapisteet_$in{'eventid'}.txt");
@ratap=<SISAAN>;
close(SISAAN);

open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
@merkinnat=<SISAAN>;
close(SISAAN);

open (SISAAN,"<".$path."kilpailijat_$in{'eventid'}.txt");
@kilpailijat=<SISAAN>;
close(SISAAN); 

}
####


open (SISAAN,"<".$path."kisat.txt");
@kisat=<SISAAN>;
close(SISAAN);  


foreach $rec (@ratap){
chomp($rec);

($id,$rastit)=split(/\|/,$rec,2); 
$rpisteet{$id}=$rastit;
}

# Tästä apletti pyytää animaatiopisteet
$raika=3; ## step - aika sekunteina 
 

$viesti=0;
foreach $rec (@kisat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec);

if($id==$in{'eventid'} && $tyyppi ==3){
	$viesti=1;
	}
}

## haetaan suora reitti
foreach $rec (@ratap){ 
	chomp($rec);
($id,$data)=split(/\|/,$rec,2);
@temp=split(/N/,$data);
$data="";
 foreach $recb (@temp){ 
	chomp($recb);
 ($x,$y)=split(/\;/,$recb,2);
$data=$data.($x).";".($y)."N";
	}

$suorareitti{$id}=$data;
($pis,$data)=split(/N/,$data,2);
$suorarastit{$id}=$data;
}
## suora reitti ok


$gpsid=',';
@temp=split(/\,/,$in{'kilp'});
foreach $rec (@temp){

if($rec > 50000){
$rec=$rec-50000;
$gpsid.=$rec.',';
}
}

$in{'kilp'}=','.$in{'kilp'}.',';

## haetaan valiajat
$kilp=1;$laikaMin=99999999;

$ok=0;
foreach $rec (@kilpailijat){
	chomp($rec);
	($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$sija,$tulos,$valiajat,$GPSa)=split(/\|/,$rec);
$s=','.$id.',';
if($in{'kilp'} =~ /${s}/){
$kilp=$id;
if($lahtoaika[$kilp] eq ''){
$lahtoaika[$kilp]=$laika;
}else{
$laika=$lahtoaika[$kilp];
}
$lahtoaika[$kilp]=$laika; 
if($laika<$laikaMin && $laika eq $laika+0){
$laikaMin=$laika;
}
if($vajat[$kilp] eq ''){
	$vajat[$kilp]=$valiajat;
}
$gpsani[$kilp]=$GPSa;
$srj{$kilp}=$sarjanro; 

if($viesti ==1){
$srj{$kilp}=$sija; 
}

$ok=1;
}
if($gpsid =~ /${s}/){
$vajat[$id+50000]=$valiajat;
$lahtoaika[$id+50000]=$laika; 
}
}

if($ok==0){exit;}


# valiajat nyt muuttujassa $vajat[] 

$kilp=1;
{

$ok=0;
foreach $rec (@merkinnat){
	chomp($rec);

	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);

$s=','.$id.',';
if($in{'kilp'} =~ /${s}/){
$kilp=$id;
$viiva[$kilp]=$viivat; 
$rast[$kilp]=$rastit;
$ok=1;
} 
}

} 

## nyt on valiajat, reittipiirros ja rastipisteet selvillä
## nyt lasketaan animaatioille pisteet
## tämä pitäisi tehdä clientissä serveriä säästääksemme, mutta
## ei nyt jaksa javalla väsätä, ehkä sitten joskus

$kilp=1;
#while($in{"k".$kilp} ne''){
@kilp=split(/\,/,$in{'kilp'});
foreach $kilp (@kilp){ 
if($kilp ne ''){
if($viiva[$kilp] eq ''){ # ei ollut piirtänyt, tilalle suora reitti
$viiva[$kilp]="N".$suorareitti{$srj{$kilp}};
$rast[$kilp]="N".$suorarastit{$srj{$kilp}};
#exit;
}
$aikasiirto=0;  
if($kilp<50000){  
$out= ''.$lahtoaika[$kilp].';'.($lahtoaika[$kilp]-$laikaMin).'H';
@reitti=split(/N/,$viiva[$kilp]);
@valiajat=split(/\;/,$vajat[$kilp]);
@rastit=split(/N/,$rast[$kilp]);

$i=0;
$viiva[$kilp]=$viiva[$kilp]."N"; 

$viivatemp="";
foreach $rec (@rastit){

$i++;
if($rec ne ""){
$j="NC".$i."N";$k="N".$rec."N";           
($temp,$viiva[$kilp])=split(/${k}/,$viiva[$kilp],2);  
$viiva[$kilp]="N".$viiva[$kilp];
$viivatemp=$viivatemp.$temp.$j;
}
}      
$viiva[$kilp]=$viivatemp;
$i=0;
foreach $rec (@rastit){ 
$i++;$j="NC".$i."N";$k="N".$rec.'|'.$rec."N";
$viiva[$kilp]=~ s/${j}/${k}/;
}

$viiva[$kilp]=~ s/^\|//;
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 

@rastivalit=split(/\|/,$viiva[$kilp]);
$ulos=join("\n",@rastivalit);

$i=0;

$matkasiirto=0;
foreach $rec (@rastivalit){
$rec=~ s/^N//;
$matkasiirto=0;
$i++;
}

$i_rastit=0;
$i_reitti=0;
$i_valiajat=0;
$i_piste=0;
$aika=0;
$matka=0;

while ($valiajat[$i_rastit] ne '' && ($i_rastit==0 || $valiajat[$i_rastit]>$valiajat[$i_rastit-1])){

$rastivalit[$i_rastit]=~ s/^N//; 

@viivab=split(/N/,$rastivalit[$i_rastit]);
# lasketaan pituus
$x0=0;
$y0=0;    
$pituus=0;
$i=0;

$lisaaika=0;
foreach $rec (@viivab){
($x1,$y1)=split(/\;/,$rec);
if($i>0){            
$pituus=$pituus+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1));
if($x0 == $x1 && $y0 == $y1){
## 2 peräkkäistä klikkausta = pysähdys 3 sec
 $lisaaika=$lisaaika+3;
}
}
$x0=$x1;$y0=$y1;           
$i++;
}
                  
$valiaika=$valiajat[$i_rastit]-$valiajat[$i_rastit-1];
if($i_rastit==0){
$valiaika=$valiajat[$i_rastit];
}
## hyomioidaan pysähdykset
$valiaika=$valiaika-$lisaaika;
if($valiaika ==0 || $valiaika<0 ){
 $valiaika=0.00001;
}
$step=($pituus/($valiaika/$raika));

$matkasiirto=$aikasiirto*$step;
# pisteet polylinen varrelle 
$i=0;$seis=0;
foreach $rec (@viivab){
($x1,$y1)=split(/\;/,$rec);
if($i>0){   
if($x0 == $x1 && $y0 == $y1){
$seis++;
## ei kahta peräkkäistä klikkausta samaan pisteeseen
}else{
$plkm=1;
while($matka+$step*$plkm-$matkasiirto < $matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))){
$i_piste++; 
#lasketaan animaatioreittipiste
$ax=floor((($step*$plkm-$matkasiirto)*$x1+$x0*(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($step*$plkm-$matkasiirto)))/(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))));
$ay=floor((($step*$plkm-$matkasiirto)*$y1+$y0*(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($step*$plkm-$matkasiirto)))/(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))));
$info="";
$out.= "$ax;".$ay.",".$info."N";

if($seis > 0){
for($ii=0;$ii<$seis;$ii++){
$out.= "$ax;$ay,".$info."N";
}
$seis=0;
}
$plkm++;
} 
$matkasiirto=$matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($matka+$step*($plkm-1)-$matkasiirto);
$matka=$matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1));
$aikasiirto=$matkasiirto/$step*1;
} 
}
$x0=$x1;$y0=$y1;   
$i++;
}
$i_rastit++;
} 
}else{
## gps animaatip
#$out.= "0;0;0,0N";
$out= ''.$lahtoaika[$kilp].';'.($lahtoaika[$kilp]-$laikaMin).'H';
if($out =~/\</ ||$out =~/\// ){
$out='0;0;H';
}
$out.= $gpsani[$kilp];
}

$out=~ s/\r//g;
$out=~ s/\n/N/g;

#foreach $rasti (split(/N/,$rpisteet{$kilp})){
#$out =~ s/N${rasti}\,N/N${rasti},N${rasti}\,NCN/;
#}
if($out =~/\</ ||$out =~/\// ){
# crap
}else{
$out{$kilp}=  "{\"$kilp\":\"$vajat[$kilp]H$out\"}";
}
}
}

print "[";
$count=0;
foreach   $id ((split(/\,/,$in{'kilp'}))){

if($out{$id} ne ''){

if($count>0){print ",";}
$out{$id} =~ s/\r//g;
print $out{$id};
$count++;
}
}

print "]\n";
exit;
}
if($in{'act'} eq 'jskommentit'){
$in{'eventid'}=1*$in{'eventid'};

$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" || -e $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){

if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
 require Compress::Zlib;
 import Compress::Zlib;
$archived=1;

$gz = gzopen($path."kommentit_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@kommentit=split(/\n/,$data);
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
 
for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
{
$prename=$name; $name = $u->getHeaderInfo()->{Name};
	
if($name eq "kommentit_$in{'eventid'}.txt"){
$archived=1;
$data='';
while (($status = $u->read($buff)) > 0) {
$data.=$buff;
}
@kommentit=split(/\n/,$data);
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
if($archived==0){
open (SISAAN,"<$path"."kommentit_$in{'eventid'}.txt");
@kommentit=<SISAAN>;
close(SISAAN);  
}

$in{'kilp'}=','.$in{'kilp'}.',';


$i=0;
foreach $rec (@kommentit) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$rec);
	$i++;
$s=','.${id}.',';
if($in{'kilp'}=~ /${s}/){
$kommentit =~ s/#nl#/\\n/g;
$kommentit =~ s/#cr#//g;
$out{$id}= "{\"$#out\":\"\\n\\n<b>$nimi</b>:\\n".$kommentit."<br>\"}";
}
}


###
print "[";
$count=0;
foreach   $id ((split(/\,/,$in{'kilp'}))){
if($out{$id} ne ''){

if($count>0){print ",";}
$out{$id} =~ s/\r//g;
utf8::decode($out{$id});
print $out{$id};
$count++;
}
}

print "]\n";
exit;
}
###################################################
if ($in{"act"} eq "splitsbrowserjs"){   


open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);  
$viesti=0;
foreach $rec (@kartat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi,$paiva,$org,$level,$info,$compression)=split(/\|/,$rec);

if($id==$in{'id'}){
	$eventname='Ãðàôèê ñïëèòîâ - '.$nimi;
	}
}

open (SISAAN,"<$path/../splitsbrowser/splits-graph-template.html");
@page=<SISAAN>;
close(SISAAN);  

$page=join('',@page);

$dataurl='reitti.'.$extension.'?act=splitsbrowsercsv&id='.$in{'id'};
$s='url/to/some/event/data';
$page=~ s/${s}/${dataurl}/gi;

$page=~ s/Page title/${eventname}/i;
$page=~ s/#httppath#/${httppath}/gi;

print $page;

exit;
}
################ ratapisteet ####################
if ($in{"act"} eq "jsratapisteet"){
	require 'CourseDrawInfo.pl';
	exit;
}
###############################
if($in{'act'} eq 'jsvaliajat') {
	require 'SplitTable.pl';
	exit;
}

sub uniq {
    my %seen = ();
    my @r = ();
    foreach my $a (@_) {
        unless ($seen{$a}) {
            push @r, $a;
            $seen{$a} = 1;
        }
    }
    return @r;
}

# ImageSize.pl
#
# This code is Copyright 2003,2007 Tony Lewis <tlewis@exelana.com>.
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#   more details.
#
#   You should have received a copy of the GNU General Public License along with
#   this program.  If not, see http://www.gnu.org/licenses/.
#
################################################################################
# Return the size of an image (width, height)
#
# my ($width, $height, $format) = ImageSize($filePath)
#
# If the return values are negative, an error occurred. Each combination of
# values indicates a specific error.
#
# The first number indicates an open error or which image type failed:
# -1 open or read header of image file failed 
# -2 GIF failure 
# -3 JPG failure 
# -4 BMP failure 
# -5 PNG failure 
#
# The second number indicates the specific error that occurred. (See the code
# for the meanings of the various combinations.
#
################################################################################

sub ImageSize {
  my ($path) = @_;
  my ($w, $h, $w1, $w2, $w3, $w4, $h1, $h2, $h3, $h4, $header, $marker, $skip, $len, $len1, $len2);

  # Guess the format from the file extension
  my ($format) = $path =~ m/\.(...)$/;
  $format = lc($format);

  open IMGSIZEF, "$path" or return (-1,-1,$format);

  # Override the guessed format if header indicates the type of file
  return ImageSizeCloseF(-1,-2,$format) if read(IMGSIZEF, $header, 8) < 8;
  $format = "gif" if substr($header,0,6) eq "GIF87a" || substr($header,0,6) eq "GIF89a";
  $format = "jpg" if substr($header,0,2) eq "\xff\xd8";
  $format = "bmp" if substr($header,0,2) eq "BM";
  $format = "png" if substr($header,0,8) eq "\x89PNG\r\n\x1A\n";
  seek(IMGSIZEF,0,0);

  ############ GIF
  if ($format eq "gif") {
    return ImageSizeCloseF(-2,-1,$format) if read(IMGSIZEF, $header, 6) < 6;
    return ImageSizeCloseF(-2,-2,$format) if $header ne "GIF87a" && $header ne "GIF89a";
    return ImageSizeCloseF(-2,-3,$format) if read(IMGSIZEF, $w1, 1) < 1;
    return ImageSizeCloseF(-2,-4,$format) if read(IMGSIZEF, $w2, 1) < 1;
    return ImageSizeCloseF(-2,-5,$format) if read(IMGSIZEF, $h1, 1) < 1;
    return ImageSizeCloseF(-2,-6,$format) if read(IMGSIZEF, $h2, 1) < 1;
    return ImageSizeCloseF(ord($w2) * 256 + ord($w1), ord($h2) * 256 + ord($h1),$format);

  ############ JPG
  } elsif ($format eq "jpg") {
    return ImageSizeCloseF(-3,-1,$format) if read(IMGSIZEF, $header, 2) < 2;
    return ImageSizeCloseF(-3,-2,$format) if $header ne "\xff\xd8"; # SOI marker
    while (1) {
      return ImageSizeCloseF(-3,-3,$format) if read(IMGSIZEF, $header, 1) < 1 || ord($header) != 0xFF;
      return ImageSizeCloseF(-3,-4,$format) if read(IMGSIZEF, $marker, 1) < 1;
      return ImageSizeCloseF(-3,-5,$format) if read(IMGSIZEF, $len1, 1) < 1;
      return ImageSizeCloseF(-3,-6,$format) if read(IMGSIZEF, $len2, 1) < 1;
      $len = ord($len1) * 256 + ord($len2) - 2;

      if (ord($marker) < 0xC0 || ord($marker) > 0xCA || ord($marker) == 0xC4 || ord($marker) == 0xC8 || ord($marker) == 0xCC) {
        return ImageSizeCloseF(-3,-7,$format) if read(IMGSIZEF, $skip, $len) < $len;
      } else {
        return ImageSizeCloseF(-3,-8,$format) if read(IMGSIZEF, $skip, 1) < 1; # precision
        return ImageSizeCloseF(-3,-9,$format) if read(IMGSIZEF, $h1, 1) < 1;
        return ImageSizeCloseF(-3,-10,$format) if read(IMGSIZEF, $h2, 1) < 1;
        return ImageSizeCloseF(-3,-11,$format) if read(IMGSIZEF, $w1, 1) < 1;
        return ImageSizeCloseF(-3,-12,$format) if read(IMGSIZEF, $w2, 1) < 1;
        return ImageSizeCloseF(ord($w1) * 256 + ord($w2), ord($h1) * 256 + ord($h2),$format);
      }
    }

  ############ BMP
  } elsif ($format eq "bmp") {
    return ImageSizeCloseF(-4,-1,$format) if read(IMGSIZEF, $header, 2) < 2;
    return ImageSizeCloseF(-4,-2,$format) if $header ne "BM";
    return ImageSizeCloseF(-4,-3,$format) if read(IMGSIZEF, $skip, 12) < 12; # rest of the BMP file header

    return ImageSizeCloseF(-4,-4,$format) if read(IMGSIZEF, $skip, 4) < 4; # Bitmap Header: length
    return ImageSizeCloseF(-4,-5,$format) if read(IMGSIZEF, $w1, 1) < 1;
    return ImageSizeCloseF(-4,-6,$format) if read(IMGSIZEF, $w2, 1) < 1;
    return ImageSizeCloseF(-4,-7,$format) if read(IMGSIZEF, $w3, 1) < 1;
    return ImageSizeCloseF(-4,-8,$format) if read(IMGSIZEF, $w4, 1) < 1;
    return ImageSizeCloseF(-4,-9,$format) if read(IMGSIZEF, $h1, 1) < 1;
    return ImageSizeCloseF(-4,-10,$format) if read(IMGSIZEF, $h2, 1) < 1;
    return ImageSizeCloseF(-4,-11,$format) if read(IMGSIZEF, $h3, 1) < 1;
    return ImageSizeCloseF(-4,-12,$format) if read(IMGSIZEF, $h4, 1) < 1;
    return ImageSizeCloseF(ord($w4) * (256**3) + ord($w3) * (256**2) + ord($w2) * 256 + ord($w1),
                  ord($h4) * (256**3) + ord($h3) * (256**2) + ord($h2) * 256 + ord($h1),$format);

  ############ PNG
  } elsif ($format eq "png") {
    return ImageSizeCloseF(-5,-1,$format) if read(IMGSIZEF, $header, 8) < 8;
    return ImageSizeCloseF(-5,-2,$format) if $header ne "\x89PNG\r\n\x1A\n";

    return ImageSizeCloseF(-5,-3,$format) if read(IMGSIZEF, $skip, 4) < 4; # length of the IHDR chunk
    return ImageSizeCloseF(-5,-4,$format) if read(IMGSIZEF, $skip, 4) < 4; # chunk type
    return ImageSizeCloseF(-5,-5,$format) if $skip ne "IHDR";

    return ImageSizeCloseF(-5,-6,$format) if read(IMGSIZEF, $w1, 1) < 1;
    return ImageSizeCloseF(-5,-7,$format) if read(IMGSIZEF, $w2, 1) < 1;
    return ImageSizeCloseF(-5,-8,$format) if read(IMGSIZEF, $w3, 1) < 1;
    return ImageSizeCloseF(-5,-9,$format) if read(IMGSIZEF, $w4, 1) < 1;
    return ImageSizeCloseF(-5,-10,$format) if read(IMGSIZEF, $h1, 1) < 1;
    return ImageSizeCloseF(-5,-11,$format) if read(IMGSIZEF, $h2, 1) < 1;
    return ImageSizeCloseF(-5,-12,$format) if read(IMGSIZEF, $h3, 1) < 1;
    return ImageSizeCloseF(-5,-13,$format) if read(IMGSIZEF, $h4, 1) < 1;
    return ImageSizeCloseF(ord($w1) * (256**3) + ord($w2) * (256**2) + ord($w3) * 256 + ord($w4),
                  ord($h1) * (256**3) + ord($h2) * (256**2) + ord($h3) * 256 + ord($h4),$format);
  }

  return ImageSizeCloseF(-1, -3,$format);
}

sub ImageSizeCloseF
{
  close IMGSIZEF;
  return @_;
}


#################################
if($in{'act'} eq "jsstrk"){

open (HANDLE,"<".$path."kilpailijat_$in{'eventid'}.txt");
@d=<HANDLE>;
close HANDLE;  


if($in{'etype'} eq '2'){ ## if add mode   
## get ID

foreach $rec (@d){
($id,$rest)=split(/\|/,$rec,2);
if($id>50000){$id=$id-50000;}
if($in{'id'} < $id){$in{'id'}=$id;}
}
$in{'id'}=(1*$in{'id'})+1;
}else{

## read original version of name, to avoid some charset trouble

foreach $rec (@d){
@r=split(/\|/,$rec);
if($in{'id'} == $r[0] && $r[3] ne ''){$in{'suunnistaja'}=$r[3];}
}

}

## input

$in{'suunnistaja'}=~ s/#chsmcl#/\;/g;
$in{'suunnistaja'}=~ s/#chnd#/\&/g;

#$success = utf8::downgrade($in{'komm'}, FAIL_OK);
	$in{'komm'} = decode('utf8', $in{'komm'}); #èç utf8 â íóæíûé ôîðìàò

$in{'komm'}=~ s/#chsmcl#/\;/g;
$in{'komm'}=~ s/#chnd#/\&/g;
	$in{'komm'} = encode('windows-1251', $in{'komm'}); #ïðåîáðàçóåì êîììåíòàðèé â íóæíóþ êîäèðîâêó

## gps 
if($in{'GPS'}==1){
$in{'suunnistaja'}=' GPS '.$in{'suunnistaja'};
$in{'id'}=50000+$in{'id'};
}
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
@merkinnat=<SISAAN>;
close(SISAAN);  

$ok=1;

foreach $rec (@merkinnat) {
	chomp($rec);
	($idkilp,$id,$nimi,$hajonta,$viivat,$rastit)=split(/\|/,$rec);
	
if($id	eq $in{'id'}){
$ok=0; ## eli piirros oli jo olemassa, ei tallenneta
}
}



$in{'track'} =~ s/\n//g;
$in{'track'} =~ s/\r//g;
($reitti,$rastit)=split(/\|/,$in{'track'});


if($ok  == 1){

if($in{'GPS'}!=1){

@tmp=split(/N/,$reitti);
foreach $p (@tmp){
if($p ne ''){
($a,$b)=split(/\;/,$p,2);
$a=floor($a*100)/100;
$b=floor($b*100)/100;
$p=''.$a.';'.$b;
}
}
$reitti=join('N',@tmp);

open (HANDLE,">>".$path."merkinnat_$in{'eventid'}.txt");
$out=''.$in{'rataid'}."|".$in{'id'}."| $in{'suunnistaja'}|$in{'hajonta'}|$reitti|$rastit";
$out =~ s/\n//g;
$out =~ s/\r//g;

&lock_file;
print HANDLE $out."\n";
&unlock_file;
close HANDLE;

}else{

@GPSD=split(/N/,$reitti);
$reitti='';

foreach $gd (@GPSD){
chomp($gd);
if($gd ne ''){
($Gx,$Gy,$Gt)=split(/\;/,$gd);
if($Gx ne $GxOLD || $Gy ne $GyOLD){
$reitti.='N'.$Gx.';'.$Gy;
$GxOLD=$Gx;
$GyOLD=$Gy;
}
}
}
$reitti.='|';

## gps animaatio
$GAIKA=0;$ani='';$i=0;
foreach $gd (@GPSD){
chomp($gd);
if($gd ne ''){
($Gx,$Gy,$Gt)=split(/\;/,$gd);
if($i%3==1){
$ani.=$Gx.';'.$Gy.',0N';
}
$i++;
}
}

open (HANDLE,">>".$path."merkinnat_$in{'eventid'}.txt");

$myout = $in{'rataid'}."|".$in{'id'}."| $in{'suunnistaja'}|$in{'hajonta'}|$reitti|$rastit\n";
if(length($myout) < 100000*5){
&lock_file;
print HANDLE $myout;
&unlock_file;
}

close HANDLE;



}

$in{'komm'}=~ s/\n/#nl#/g;
$in{'komm'}=~ s/\r/#cr#/g;
if(length($in{'komm'}) > 50000){
$in{'komm'}='';
}
$out=$in{'rataid'}."|".$in{'id'}."|$in{'suunnistaja'}||$in{'komm'}";
$out =~ s/\n//g;
$out =~ s/\r//g;
$out =~ s/\<//g;
$out =~ s/\>//g;
open (HANDLE,">>".$path."kommentit_$in{'eventid'}.txt");
&lock_file;
print HANDLE $out."\n";
&unlock_file;
close HANDLE;  
         
if($in{'etype'} eq '2' || $in{'GPS'}==1){ ## if add mode   

if($in{'GPS'}!=1){
## leg lengths
($pois,$lahto,$muut)=split(/N/,$reitti,3);

$sLength=0;
@aControls=split(/N/,($lahto.$rastit));
$ai=0;
foreach $aControl (@aControls){
$ai++;
if($ai>1){
($ax1,$ay1)=split(/\;/,$aControls[$ai-2]);
($ax2,$ay2)=split(/\;/,$aControls[$ai-1]);
$aleg[$ai-1]=sqrt(($ax1-$ax2)*($ax1-$ax2)+($ay1-$ay2)*($ay1-$ay2)); # Pythagoras 
}
}

##

$usersplits='';
$splitnro=0;$splitmissing=0;
@splits=split(/m/,$in{'usersplits'});
foreach $split (@splits){
$splitnro++;
($min,$sec)=split(/s/,$split);

if(floor(60*$min+(1*$sec))>0 && $splitmissing==0){
$usersplits.=floor(60*$min+(1*$sec)).';';
$lastsplit=floor(60*$min+(1*$sec));
}

if(floor(60*$min+(1*$sec))==0){# a split is missing
	if($splitmissing==0){
		$splitmissing=$splitnro;
	}
}

if(floor(60*$min+(1*$sec))>0 && $splitmissing>0){ # there has been missing split before this split
$sLength=0;
for($j=$splitmissing;$j<$splitnro+1;$j++){
$sLength=$sLength+$aleg[$j];
}

$averagespeed=(floor(60*$min+(1*$sec))-$lastsplit)/$sLength;

$sLength=0;
for($j=$splitmissing;$j<$splitnro+1;$j++){
$sLength=$sLength+$aleg[$j];
$usersplits.=floor($lastsplit+$sLength*$averagespeed).';';
}
$splitmissing=0;
$lastsplit=floor(60*$min+(1*$sec));
}
}


$result=$min.':'.$sec;

}# if gps!=1

if($in{'GPS'}==1){
$GPSani=$ani;
}

$out=$in{'id'}."|".$in{'rataid'}."||$in{'suunnistaja'}|0||$in{'hajonta'}|$result|$usersplits|$GPSani";
open (HANDLE,">>".$path."kilpailijat_$in{'eventid'}.txt");


$out =~ s/\n//g;
$out =~ s/\r//g;



if(length($out) < 100000*5)	{
&lock_file;
print HANDLE $out."\n";
&unlock_file;
}
close HANDLE;

}                        
}
print "\n";
exit;
}


#################### rgjs section ends#############################


##################### Version #############################3
if($in{'act'} eq 'version'){ 
print $RG_version;
exit;
}

##################### OGraphAppletJar #############################3
if($in{'act'} eq 'OGraphAppletJar'){  

open(SISAAN, "<".$path."EmitGraph3.jar");
binmode SISAAN;
@data=<SISAAN>;
close(SISAAN);
binmode STDOUT;
print @data;
exit;
}
##################### OGraphApplet #############################3
if($in{'act'} eq 'OGraphApplet'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">
<html>
<head>
	<title>OGraphApplet on RouteGadget</title>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
</head>
<body  BGCOLOR=\"#A0A0A0\">

<table border=2 bordercolor=#005578   WIDTH=\"100%\"  HEIGHT=\"100%\"  cellpadding=0 cellspacing=0><tr><td>
<APPLET
  CODEBASE = \".\"
  Code     = \"OGraphApplet.class\"  
  Archive  = \"reitti.".$extension."?act=OGraphAppletJar\"
  WIDTH    = \"100%\"
  HEIGHT   = \"100%\"
  Credits  = \"OGraphApplet by Pekka Varis\"
>
";

#EmitGraph3.jar       

open(SISAAN, "<".$path."kisat.txt");
@kilpailut=<SISAAN>;
close(SISAAN);

$i=0;
foreach $rec (@kilpailut){
chomp($rec);
@field=split(/\|/,$rec);

if($field[2] != 3){
$i++;
print "<PARAM NAME = \"comp".$i."name\" VALUE = \"$field[3]\">
<PARAM NAME = \"comp".$i."file\" VALUE = \"reitti.".$extension."?act=ographsplits&id=$field[0]\">\n";
}
}

print"<PARAM NAME = \"Color\" VALUE=\"232,232,240\">
</APPLET></td></tr></table>
</body>
</html>";
exit;
}       


##################### OGraphAppletSplits #############################3
if($in{'act'} eq 'ographsplits'){       
$in{'id'}=1*$in{'id'};
open(SISAAN, "<".$path."kilpailijat_$in{'id'}.txt");
@data=<SISAAN>;
close(SISAAN);

@data = sort {
    (split '\|', $a, 9)[1] <=>
    (split '\|', $b, 9)[1]
  } @data;
            
  $sarja='';
  
foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 
if($sarja ne $field[2]){
$sarja=$field[2];
 print "#Sarja $sarja\n";
}
 # $field[8] =~ s/\;/\|/g;
  if($field[8] ne '' && $field[5]>0){
  @row=split(/\;/,$field[8]);
print " $field[3]|";
foreach $sp (@row){
$sec=floor(60*($sp/60-floor($sp/60)));
if($sec<10){$sec='0'.$sec;}

$hou='';
$min=floor($sp/60);
if($min>59){
$hou=floor($min/60);
$min=$min-$hou*60;
if($hou<10){$hou='0'.$hou;}
if($min<10){$min='0'.$min;}
}

print ''.$hou.$min.$sec.'|';
}
print "\n";
}
}
}


##################### splitsbrowserjar #############################3
if($in{'act'} eq 'splitsbrowserJar'){  

open(SISAAN, "<".$path."splitsbrowser.jar");
binmode SISAAN;
@data=<SISAAN>;
close(SISAAN);
binmode STDOUT;
print @data;
exit;
}

##################### splitalyzerjar #############################3
if($in{'act'} eq 'splitalyzerjar'){  

open(SISAAN, "<".$path."splitalyzer.jar");
binmode SISAAN;
@data=<SISAAN>;
close(SISAAN);
binmode STDOUT;
print @data;
exit;
}

##################### splistalyzer #############################3
if($in{'act'} eq 'splitalyzer'){    
$eventid=1*$in{'id'};


open(SISAAN, "<".$path."kisat.txt");
@kilpailut=<SISAAN>;
close(SISAAN);

$i=0;
foreach $rec (@kilpailut){
chomp($rec);
@field=split(/\|/,$rec);
$i++;
if($field[0] == $eventid){
$ename=$field[3];
}
}

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">
<HTML><HEAD><TITLE>$ename</TITLE>
<BODY leftMargin=\"0\" topMargin=\"0\" scroll=\"no\" marginheight=\"0\" marginwidth=\"0\">
<APPLET name=splitalyzer code=Splitalyzer.class align=center width=100% height=100% archive=reitti.".$extension."?act=splitalyzerjar>
<PARAM NAME=\"src\" VALUE=\"reitti.".$extension."?act=splitalyzersplits&eventid=$eventid\">
<PARAM NAME=\"srcstarttimes\" VALUE=\"reitti.".$extension."?act=splitalyzerstarttimes&eventid=$eventid#\">
<PARAM NAME=\"eventname\" VALUE=\"$ename\">
	    A Java enabled browser is required to view this page&nbsp;
</APPLET>
</BODY>
</HTML>";
exit;
}
###############################
if($in{'act'} eq 'gettime'){    
$servertime=time;
print "<div>$servertime</div>\n";
exit;
}
##################### splitsbrowser #############################3
if($in{'act'} eq 'splitsbrowser'){    
$eventid=1*$in{'id'};


open(SISAAN, "<".$path."kisat.txt");
@kilpailut=<SISAAN>;
close(SISAAN);

$i=0;
foreach $rec (@kilpailut){
chomp($rec);
@field=split(/\|/,$rec);
$i++;
if($field[0] == $eventid){
$ename=$field[3];
}
}


print  "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">

<HTML><HEAD><TITLE>$ename</TITLE>
<BODY onload=resize() onresize=resize() leftMargin=0 topMargin=0 scroll=no marginheight=\"0\" marginwidth=\"0\">

<SCRIPT language=JavaScript>

    // Find if we have ns4 or not
    var agt=navigator.userAgent.toLowerCase();
    var appVer = navigator.appVersion.toLowerCase();
    var is_minor = parseFloat(appVer);
    var is_major = parseInt(is_minor);
    
    var is_ns  =( (agt.indexOf('mozilla')!=-1) &&
                   (agt.indexOf('spoofer')==-1) &&
                   (agt.indexOf('compatible') == -1) &&
                   (agt.indexOf('opera')==-1) &&
                   (agt.indexOf('webtv')==-1) );

   var is_ns4  = ( is_ns &&
                   (is_major == 4) );

   function resize() {
     // Make resizing work in netscape browsers

       var w_newWidth,w_newHeight;
       var w_maxWidth=1600, w_maxHeight=1200;

       var netscape4ScrollWidth;

      if (is_ns4) {
         netscape4ScrollWidth = 15
      } else {
         netscape4ScrollWidth = 0
      }

       w_newWidth=window.innerWidth-netscape4ScrollWidth;
       w_newHeight=window.innerHeight-netscape4ScrollWidth;

       if (w_newWidth>w_maxWidth) w_newWidth=w_maxWidth;
       if (w_newHeight>w_maxHeight) w_newHeight=w_maxHeight;
       document.splitsbrowser.setSize(w_newWidth, w_newHeight);
       window.scroll(0,0);
   }

if (is_ns4) {
  document.write(\"<APPLET name=splitsbrowser code=SplitsBrowser.class align=center width=1600 height=1200 ARCHIVE=reitti.".$extension."?act=splitsbrowserJar>\");
} else {
  document.write(\"<APPLET name=splitsbrowser code=SplitsBrowser.class align=center width=100% height=100% ARCHIVE=reitti.".$extension."?act=splitsbrowserJar>\");
}
</SCRIPT>

    <PARAM NAME=\"color1\" VALUE=\"CBF5FF\">
    <PARAM NAME=\"color2\" VALUE=\"D8DCFF\">
    <PARAM NAME=\"graphbackground\" VALUE=\"99CCFF\">
    <PARAM NAME=\"background\" VALUE=\"3399FF\">
    <PARAM NAME=\"dataformat\" VALUE=0>
    <PARAM NAME=\"zipped\" VALUE=\"false\">
    <PARAM NAME=\"inputdata\" VALUE=reitti.".$extension."?act=splitsbrowsercsv&id=".$eventid.">
    A Java enabled browser is required to view this page&nbsp
</APPLET>

<SCRIPT>
   // Force a resize event
if (is_ns) {
  document.resizeBy(1,1)
}
</SCRIPT>

</BODY>
</HTML>";
}


#####################
if($in{'act'} eq 'jsGPS'){

open(HANDLE,"<".$path.'GPS.txt');
@d=<HANDLE>;
close(HANDLE);

@d = sort {
    (split /\,/, $a, 2)[0] <=>
    (split /\,/, $b, 2)[0]
  } @d;

$d=join(';',@d);
$d=~ s/\r//g;
$d=~ s/\n//g;
print '[{"data":"'.$d.'"}]';
exit;
}
if($in{'act'} eq 'jsGPSLAST'){
open(HANDLE,"<".$path.'GPSLAST.txt');
@d=<HANDLE>;
close(HANDLE);
$d=join(';',@d);
$d=~ s/\r//g;
$d=~ s/\n//g;
print '[{"data":"'.$d.'"}]';
exit;
}
################# gps point saver ##################
if($in{'act'} eq 's'){

if($livepasswd ne ''){
if($livepasswd ne $in{'p'}){
exit;
}
}


open(HANDLE,"<".$path.'trackedrunners.txt');
@d=<HANDLE>;
close(HANDLE);
$next=1;
foreach $rec (@d){
chomp($rec);
@r=split(/\|/,$rec);
$newid{1*$r[0]}=$r[1];
$next=1*$r[1]+1;
}

$competitor=1*$in{'c'};

## temporaty fix for overlapping ID's using IP address
#if($competitor==15 && $ENV{REMOTE_ADDR} eq 'IP_HERE'){
#$in{'c'}=73; # set an other id for this ip 
#$competitor=1*$in{'c'};
#}

if($newid{$competitor} eq ''){
open(HANDLE,">>".$path.'trackedrunners.txt');
print HANDLE $competitor.'|'.$next."\n";
close(HANDLE);
$newid{$competitor}=$next;
}

### transformation
$competitor=$newid{1*$in{'c'}};

$o=''.$in{'c'}.'|'.$in{'d'}."\n";

## all data to log file for back up
open(ULOS,">>".$path."GPS_ALL.txt");
print ULOS $o;
close ULOS;

open(HANDLE,"<".$path.'coord.txt');
@f=<HANDLE>;
close(HANDLE);

$compmax=0;
foreach $rec (@f){
chomp($rec);
if($rec =~/\|/){
@r=split(/\|/,$rec);
$rname{1*$r[0]}=$r[1];
if($compmax < 1*$r[0]){$compmax = 1*$r[0];}
}
if($rname{1*$in{'c'}} eq ''){
$rname{1*$in{'c'}}='Vacant '.(1*$in{'c'});
}
}

($o1x,$o1y)=split(/\,/,$f[0]);
($o2x,$o2y)=split(/\,/,$f[1]);
($o3x,$o3y)=split(/\,/,$f[2]);
($s1x,$s1y)=split(/\,/,$f[3]);
($s2x,$s2y)=split(/\,/,$f[4]);
($s3x,$s3y)=split(/\,/,$f[5]);

$s1y=-$s1y;
$s2y=-$s2y;
$s3y=-$s3y;

$lat0=$o1y;
$lon0=$o1x;
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


@d=split(/x/,$in{'d'});
$out='';$timemax=0;
$i=0;
foreach $rec (@d){
@pt=split(/\,/,$rec);
$ts=1*$pt[0];
$lon=1*$pt[1];
$lat=1*$pt[2];
$sat=$pt[3];
$sat=~ s/\n//g;
$sat=~ s/\r//g;

$i++;
if($i==1){

$servertime=time;
$ts_=$ts-floor($ts/3600)*3600;
$ts_=floor(($servertime-$ts_)/3600+.5)*3600+$ts_;
$ts=$ts_;
$lon_=$lon;
$lat_=$lat;

$lon=$lon/1000000;
$lat=$lat/1000000;

}else{
$ts=$ts+$ts_;
$lon=($lon+$lon_)/1000000;
$lat=($lat+$lat_)/1000000;

}

if($lon != 0 && $lat != 0 ){
$north= (($lat-$lat0)/360*2*$pi*$r);
$east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
$easting = floor($s1x+ ((($Ga*($east-$xnolla1) + $Gb*($north-$ynolla1)))));
$northing= floor($s1y+ ((($Gc*($north-$ynolla1) + $Gd*($east-$xnolla1)))));
$out.=''.$ts.','.$competitor.','.(1*$easting).','.(1*$northing).','.$rname{1*$in{'c'}}.' ('.$sat.")\n";
if($timemax<$ts){$timemax=$ts;}
}
}

open(HANDLE,">>".$path."GPS.txt");
print HANDLE $out;
close HANDLE;


$old='';

open(HANDLE,"<".$path."GPS.txt");
@old=<HANDLE>;
close HANDLE;

foreach $rec (@old){
chomp($rec);
($ts,$c,$east,$north)=split(/\,/,$rec);
if($ts +210 > $timemax && $ts < $timemax){
$old.=$rec."\n";
}
}
$out=$old.$out;

@out=split(/\n/,$out);

@out = sort {
    (split /\,/, $a, 4)[1] <=>
    (split /\,/, $b, 4)[1]
|| 
    (split /\,/, $a, 4)[0] <=>
    (split /\,/, $b, 4)[0]
  } @out;
  
$out=join("\n",@out);

open(HANDLE,">".$path."GPSLAST.txt");
print HANDLE $out;
close HANDLE;

print "OK";
exit;
}


##################### splitalyzer starts #############################3
if($in{'act'} eq 'splitalyzerstarttimes'){       
$in{'id'}=1*$in{'eventid'};

open(SISAAN, "<".$path."kilpailijat_$in{'id'}.txt");
@data=<SISAAN>;
close(SISAAN);

#@data = sort {
#    (split '\|', $a, 9)[1] <=>
#    (split '\|', $b, 9)[1]
#  } @data;

foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 

if($field[0] <50000){

if($field[1] ne $edsarja){
print "$field[2]\n";
$edsarja=$field[1];
}
$start=''.floor($field[4]/60).':'.($field[4]-60*floor($field[4]/60));
print " $field[0] v $start \n";
}
}
}


##################### splitalyzer splits #############################3
if($in{'act'} eq 'splitalyzersplits'){       
$in{'id'}=1*$in{'eventid'};

## rastimaarat sarjoittain

open(SISAAN, "<".$path."ratapisteet_$in{'id'}.txt");
@d=<SISAAN>;
close(SISAAN);

foreach $rec (@d){
chomp($rec);
@field=split(/\|/,$rec); 
@f=split(/N/,$field[1]); 
$rmaara{$field[0]}=$#f;
}


open(SISAAN, "<".$path."kilpailijat_$in{'id'}.txt");
@data=<SISAAN>;
close(SISAAN);


@data = sort {
    (split '\|', $a, 9)[1] <=>
    (split '\|', $b, 9)[1]
  } @data;

## lasketaan väliaikojen määrä



foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 
@splits=split(/\;/,$field[8]);
if(abs($#splits - $rmaara{$field[1]}) < 3){
$rmaara2{$field[1]}+=$#splits;
$rmaara2count{$field[1]}++;
}
} # laskettu

foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 

if($rmaara{$field[1]} >2 && $field[0] <50000){

if($field[1] ne $edsarja){
# rastimaara kohdalleen
if($rmaara2count{$field[1]}>0){
$rmaara{$field[1]}=floor(0.5+ $rmaara2{$field[1]}/$rmaara2count{$field[1]})+1;
}
print "$field[1] $field[2] () ".($rmaara{$field[1]}-1)." P \n";
$edsarja=$field[1];
for($i=0;$i<$rmaara{$field[1]}-1;$i++){
print ' '.($i+1)."()";
}
print " Z\n";
$pos=0;
}
$pos++;
print ' '.$pos.' '.$field[0].' '.$field[3];

@splits=split(/\;/,$field[8]);

print ' '.floor($splits[$rmaara{$field[1]}-1]/60).':'.($splits[$rmaara{$field[1]}-1]-60*floor($splits[$rmaara{$field[1]}-1]/60));

for($i=0;$i<$rmaara{$field[1]};$i++){
$out= ' '.floor($splits[$i]/60).':'.($splits[$i]-60*floor($splits[$i]/60));

if($out eq ' 0:0'){
print ' ---';
}else{
print $out;
}

}

print " \n v \n";
}
}
}


##################### splitsbrowser splits #############################3
if($in{'act'} eq 'splitsbrowsercsv'){       
$in{'id'}=1*$in{'id'};
$in{'eventid'}=$in{'id'};

$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" || -e $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){

if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
 require Compress::Zlib;
 import Compress::Zlib;
$archived=1;

$gz = gzopen($path."kilpailijat_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@data=split(/\n/,$data);

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
 
    for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
    {
		$prename=$name; $name = $u->getHeaderInfo()->{Name};
		if($name eq "kilpailijat_$in{'id'}.txt"){
		$archived=1;
			$data='';
    while (($status = $u->read($buff)) > 0) {
		$data.=$buff;
    }
	@data=split(/\n/,$data);
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

if($archived==0){
open(SISAAN, "<".$path."kilpailijat_$in{'id'}.txt");
@data=<SISAAN>;
close(SISAAN);
}

@data = sort {
    (split '\|', $a, 9)[1] <=>
    (split '\|', $b, 9)[1]
  } @data;
            




foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 
$field[2]=~ s/\,/ /g;
$field[2]=''.$field[1].' '.$field[2];
if($sarja ne $field[2]){
$srjccuont{$sarja}=$lkmmax;
$sarja=$field[2];
$lkmmax=0;
}

@row=split(/\;/,$field[8]);
if($lkmmax<$#row+1){$lkmmax=$#row+1;}

}


$srjccuont{$sarja}=$lkmmax;


 $sarja='';
 $lkm=0;
 $tmp='';

$firsclass=1;
foreach $rec (@data){
chomp($rec);
@field=split(/\|/,$rec); 
$field[2]=''.$field[1].' '.$field[2];
$field[2]=~ s/\,/ /g;

if($sarja ne $field[2]){




if($srjccuont{$sarja}>1 &&  $sarja ne ''){

if($firsclass==0){
print "\n";
}

$firsclass=0;

$sarjout=$sarja;
$sarjout =~ s/\:/ /g;
$sarjout =~ s/\,/ /g;

print "$sarjout,".($srjccuont{$sarja}-1)."\n";
print $tmp;
}
 $lkm=0;
 $tmp='';


$sarja=$field[2];

$sarja =~s/\,/ /g;
}

$min=floor($field[4]/60);
$sec=$field[4]-60*$min;
$hour=floor($min/60);
$min=$min-$hour*60;
if($hour<10 && $hour>-1){$hour='0'.(1*$hour);}
if($min<10 && $min>-1){$min='0'.(1*$min);}
if($sec<10 && $sec>-1){$sec='0'.(1*$sec);}


$stime=$hour.':'.$min.':'.$sec;
#$stime=1*$field[4];
#$stime=$hour.':'.$min.'';
#$stime="08:12:37";

 # $field[8] =~ s/\;/\|/g;
  if($field[8] ne '' ){
  @row=split(/\;/,$field[8]);
  
$field[3] =~s/\,/ /g;

$tmp2= "$field[3], , ,$stime";

$lkm=0;

$sp_prev=0;
foreach $spcum (@row){

$sp=$spcum-$sp_prev;
$sp_prev=$spcum;
$newrow=0;
if($sp>0){
$newrow=1;
$sec=floor($sp-60*floor($sp/60));
if($sec<10 && $sec>-1){$sec='0'.(1*$sec);}

$min=floor($sp/60);

if($min<10 && $min>-1){$min='0'.(1*$min);}

$lkm++;

if($lkm-1<$srjccuont{$sarja}){
$tmp2.=  ','.$min.':'.$sec;
}
}
}

while($lkm<$srjccuont{$sarja}){
$lkm++;
$tmp2.=  ',15:00';
}


$tmp2.= "\n";


$tmp.=$tmp2;


}
}

if( $tmp ne '' && $srjccuont{$sarja}>1 && $sarja ne ''){

if($firsclass==0){
print "\n";
}

$sarjout=$sarja;
$sarjout =~ s/\:/ /g;
$sarjout =~ s/\,/ /g;
print "$sarjout,".($srjccuont{$sarja}-1)."\n";
print $tmp;
}
print "\n";
}



##################### viimeiset #############################
if($in{'act'} eq 'viimeiset5'){ 

$page_url = 'http';
#if ($ENV{HTTPS} = "on") {
#    $page_url .= "s";
#}

$page_url .= "://";
if ($ENV{SERVER_PORT} != "80") {
    $page_url .= $ENV{SERVER_NAME}.":".$ENV{SERVER_PORT}.$ENV{REQUEST_URI};
} else {
    $page_url .= $ENV{SERVER_NAME}.$ENV{REQUEST_URI};
}
($page_url,$rest)=split(/\?/,$page_url);

$in{'eventid'}=$in{'eventid'};

$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" || -e $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){

if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
 require Compress::Zlib;
 import Compress::Zlib;
$archived=1;

$gz = gzopen($path."kommentit_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@kommentit=split(/\n/,$data);
$gz = gzopen($path."sarjat_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@class=split(/\n/,$data);
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
 
    for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
    {
		$prename=$name; $name = $u->getHeaderInfo()->{Name};
		if($name eq "sarjat_$in{'eventid'}.txt"){
		$archived=1;
			$data='';
    while (($status = $u->read($buff)) > 0) {
		$data.=$buff;
    }
	@class=split(/\n/,$data);
		}
		
				if($name eq "kommentit_$in{'eventid'}.txt"){
		$archived=1;
			$data='';
    while (($status = $u->read($buff)) > 0) {
		$data.=$buff;
    }
	@kommentit=split(/\n/,$data);
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
if($archived==0){
open (SISAAN,"<$path"."sarjat_$in{'eventid'}.txt");
@class=<SISAAN>;
close(SISAAN);  
open (SISAAN,"<$path"."kommentit_$in{'eventid'}.txt");
@kommentit=<SISAAN>;
close(SISAAN);  
}


foreach $rec (@class){
chomp($rec); 
($id,$name)=split(/\|/,$rec,2);
$classname{$id}=$name;
}



print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
.{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>
<center>
<table border=0 cellpadding=0 cellspacing=0 width=755 bgcolor=#E8E8F0>
<tr><td colspan=3 bgcolor=#005578><a href=$page_url><img src=$logo height=19 width=200 border=0></a></td></tr>
<tr><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td><td>";

print "<table cellspacing=10 bgcolor= #E8E8F0><tr><td width=100% bgcolor=#E8E8F0><p><b>Ñïèñîê ïîñëåäíèõ ïóòåé (êîëè÷åñòâî: ".(1+$#kommentit).")</b><p><ul>";
      $i=0; 
while(($i<20 || $in{'all'}== 1) && $#kommentit >= $i){
	($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$kommentit[$#kommentit-$i]);
	utf8::decode($nimi);
	#print "<br><table><tr><td style=\"vertical-align: top;\"><a href=\"https://twitter.com/share\" class=\"twitter-share-button\"  data-dnt=\"true\"  data-count=\"none\" data-url=\"$page_url?act=map&id=$in{'eventid'}&cID=$idkilp&kieli=&pID=$id\">Tweet</a></td><td style=\"vertical-align: top;\"> </td><td style=\"vertical-align: top;\"><div id=\"fbshare\" class=\"fb-share-button\" data-layout=\"button\" data-href=\"$page_url?act=map&id=$in{'eventid'}&cID=$idkilp&kieli=&pID=$id\"></div></div></td><td>(<a href=reitti.".$extension."?act=map&id=$in{'eventid'}&cID=$idkilp&kieli=>$classname{$idkilp}</a>) <a href=reitti.".$extension."?act=map&id=$in{'eventid'}&cID=$idkilp&kieli=&pID=$id>$nimi</a></td></tr></table>";
	print "<li>[<a href=reitti.".$extension."?act=map&id=$in{'eventid'}&cID=$idkilp&kieli=>$classname{$idkilp}</a>] [<a href=reitti.".$extension."?act=map&id=$in{'eventid'}&cID=$idkilp&pID=$id>Ïóòü</a>]&nbsp;[<a href=reitti.".$extension."?act=map&afrom=0&atype=0&atime=0&aspeed=1&zoom=20&dim=1&id=$in{'eventid'}&cID=$idkilp&aID=$id>Àíèìàöèÿ</a>]&nbsp;$nimi\n";
	$i++;
	}
if($#kommentit >= 20 && $in{'all'} != 1){
print "</ul></p><p><a href=reitti.".$extension."?act=viimeiset5&eventid=$in{'eventid'}&kieli=&all=1>Ïîñìîòðåòü âñå</a></p>";
}
print "</td></tr></table></td><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td></tr>
<tr><td width bgcolor=#005578 colspan=3><img src=$piste height=5 width=1 border=0></td></tr>
</table><div id=\"fb-root\"></div></body></html>";

exit;  	
} 
##################### menu #############################3
if($in{'act'} eq 'mobile'){  

open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

$out= "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title>mRouteGadget</title>
</head>
<BODY>
Events:<br>";
foreach $rec (@data){
chomp($rec);
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);
$out=$out."<br><a href=reitti.".$extension."?act=valitsesarja&eventid=$id&kartta=$karttaid>$nimi</a>\n";
}
$out=$out."</body></html>";
$out =~s/ä/\&auml\;/g;
$out =~s/ö/\&ouml\;/g;
$out =~s/å/\&aring\;/g;
$out =~s/Ä/\&Auml\;/g;
$out =~s/Ö/\&Ouml\;/g;
$out =~s/Å/\&Aring\;/g;
  print $out;
exit;  
}
if($in{'act'} eq 'valitsesarja'){  
$out="<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title>mRouteGadget</title>
</head>
<BODY>
Select Class:<br>";

open (SISAAN,"<$path"."sarjat_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$nimi)=split(/\|/,$rec);
$out=$out."<br><a href=reitti.".$extension."?act=valitsereitit&eventid=$in{'eventid'}&sarja=$id&kartta=$in{'kartta'}>$nimi</a>\n";
}
close(SISAAN); 
$out =~s/ä/\&auml\;/g;
$out =~s/ö/\&ouml\;/g;
$out =~s/å/\&aring\;/g;
$out =~s/Ä/\&Auml\;/g;
$out =~s/Ö/\&Ouml\;/g;
$out =~s/Å/\&Aring\;/g;
  print $out;
exit;  
exit;
}
   if($in{'act'} eq 'valitsereitit'){
$out= "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title>mRouteGadget</title>
</head>
<BODY>
<form action=reitti.php method=post>
<input type=hidden name=eventid value=$in{'eventid'}>
<input type=hidden name=sarja value=$in{'sarja'}>
<input type=hidden name=kartta value=$in{'kartta'}>
Select map part:
<br><input type=radio name=part value=koko checked>Whole map
<br><input type=radio name=part value=ne>NE
<br><input type=radio name=part value=se>SE
<br><input type=radio name=part value=sw>SW
<br><input type=radio name=part value=nw>NW
<br>
Select routes: (max 3)<br>";
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt"); 
$j=0;
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
	
$i++;
if($idkilp eq $in{"sarja"}){ ## eli on tässä sarjassa
$j++;
@ulos[$j]="$id,<input type=checkbox name=kilp_$j value=$id>$nimi<br><input type=hidden name=kilpnimi_$j value=\"$nimi\">\n"; 
}   
}                          
close(SISAAN);

@ulos = sort {
    (split '\,', $a, 2)[0] <=>
    (split '\,', $b, 2)[0]
  } @ulos;
$out= $out.join('',@ulos)."<input type=hidden name=lkm value=$j><input type=submit value=\"Load map\"></form><p>";

$out =~s/ä/\&auml\;/g;
$out =~s/ö/\&ouml\;/g;
$out =~s/å/\&aring\;/g;
$out =~s/Ä/\&Auml\;/g;
$out =~s/Ö/\&Ouml\;/g;
$out =~s/Å/\&Aring\;/g;
  print $out;

exit;
}
##################### menu #############################3
if($in{'get'} eq 'table'){  
open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

@data = sort {
    (split /\|/, $a, 6)[4] cmp
    (split /\|/, $b, 6)[4]
  } @data;

print @data;

exit;

}

##################### RG index interface ############################
if($in{'info'} eq 'csv'){  
open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

@data = sort {
    (split /\|/, $a, 6)[4] cmp
    (split /\|/, $b, 6)[4]
  } @data;

if($in{'first'}!=1){
@data = reverse @data;
}

foreach $rec (@data){
chomp($rec);
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);

open(SISAAN, "<".$path."kommentit_".$id.".txt");
@d=<SISAAN>;
close(SISAAN);
$count=1+$#d;
print "$id|$tyyppi|$nimi|$paiva|$seura|$taso|$count\n";
}
exit;
}
##################### menu #############################3
if($in{'act'} eq 'menu' || $in{'act'} eq ''){  

if($menuStyle eq 'list'){

open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

$out= "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
.{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
</STYLE>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>
<center>
<table border=0 cellpadding=0 cellspacing=0 bgcolor=#E8E8F0 width=795>
<tr><td colspan=3 bgcolor=#005578><a href='http://www.routegadget.net/' target=_blank><img src=$logo height=19 border=0 width=200 title='www.routegadget.net'></a></td></tr>
<tr><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td><td>";
if($default_lang ne 'fi'){
$out=$out."<table cellspacing=10 bgcolor=#E8E8F0 width=100%><tr><td width=100% bgcolor=#E8E8F0><p><b>$events</b><br><br>";
}else{
$out=$out."<table cellspacing=10 bgcolor=#E8E8F0 width=100%><tr><td width=100% bgcolor=#E8E8F0><p><b>Tapahtumat:</b><br><br>";
}

$out=$out."<table cellpadding=3 cellspacing=0 width=100%>";

$count=0;


@data = sort {
    (split /\|/, $a, 6)[4] cmp
    (split /\|/, $b, 6)[4]
  } @data;

if($in{'first'}!=1){
@data = reverse @data;
}

foreach $rec (@data){
$count++;
chomp($rec);
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);

if($in{'count'}<$count && $in{'count'}+30>=$count ){

$out=$out."<tr>";

$bcolor="#f8f8ff";
if($count % 2 == 0){$bcolor="#E8E8F0";}

$out=$out."<td align=left width=20% bgcolor=$bcolor>$paiva</td><td align=left bgcolor=$bcolor width=48%><a href=reitti.".$extension."?act=map&width=980&height=550&id=$id>$nimi</a></td><td align=left width=20% bgcolor=$bcolor>$seura</td><td align=left width=10% bgcolor=$bcolor>$eLevel{$taso}</td><td align=right bgcolor=$bcolor width=5%>[<a href=reitti.".$extension."?act=viimeiset5&eventid=$id>$latestRoutes</a>]</td>";

if($Splitsbrowser==1 && $tyyppi != 3){
$out=$out. "<td bgcolor=$bcolor width=5%>[<a href=reitti.".$extension."?act=splitsbrowser&id=$id target=_blank>Ãðàôèê ñïëèòîâ</a>]</td></tr>\n";
}else{
$out=$out. "<td bgcolor=$bcolor width=5%>&nbsp;</td></tr>\n";
}
if($splitalyzer==1 && $tyyppi != 3){
$out=$out. "<td bgcolor=$bcolor width=5%>[<a href=reitti.".$extension."?act=splitalyzer&id=$id target=_blank>Splitalyzer</a>]</td></tr>\n";
}else{
$out=$out. "<td bgcolor=$bcolor width=5%>&nbsp;</td></tr>\n";
}
}
}
$out=$out. "</table>\n";
if($OGraphApplet ==1  && $tyyppi != 3){
$out=$out."<p>Split graphics: <a href=reitti.".$extension."?act=OGraphApplet>OGraphApplet</a></p>";
}

$out=$out."<br>";
if($in{'count'}>0){
$out=$out."<a href=reitti.".$extension."?act=menu&count=".($in{'count'}-30).">&lt;&lt;&lt;</a>";
}

if($in{'count'}+30 < $count){
$out=$out." <a href=reitti.".$extension."?act=menu&count=".($in{'count'}+30).">&gt;&gt;&gt;</a>";
}

$out=$out."</ul></p></td></tr></table></td><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td></tr>
<tr><td width bgcolor=#005578 colspan=3><img src=$piste height=5 width=1 border=0></td></tr>
</table></body></html>";
$out =~s/ä/\&auml\;/g;
$out =~s/ö/\&ouml\;/g;
$out =~s/å/\&aring\;/g;
$out =~s/Ä/\&Auml\;/g;
$out =~s/Ö/\&Ouml\;/g;
$out =~s/Å/\&Aring\;/g;


  print $out;

}else{

$plusgif="<img src=\\'".$httppath."plus.gif\\' border=0><img src=\\'".$httppath."empty.gif\\' border=0 height=5 width=10>";
$minusgif="<img src=\\'".$httppath."minus.gif\\' border=0><img src=\\'".$httppath."empty.gif\\' border=0 height=5 width=10>";
$perloadimages="<img src=\'".$httppath."plus.gif\' border=0 height=1 width=1><img src=\'".$httppath."minus.gif\' border=0 height=1 width=1><img src=\'".$httppath."empty.gif\' border=0 height=1 width=1>";
$igif="<img src=\\'".$httppath."i.gif\\' border=0 height=11 width=11>";

## event tree menu ####


open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);

$out= "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
.{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
</STYLE>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>
<center>
<table border=0 cellpadding=0 cellspacing=0 bgcolor=#E8E8F0 width=795>
<tr><td colspan=3 bgcolor=#005578><a href='http://www.routegadget.net/' target=_blank><img src=$logo height=19 border=0 width=200 title='www.routegadget.net'></a></td></tr>
<tr><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td><td><table cellspacing=10 bgcolor=#E8E8F0 width=100%><tr><td width=100% bgcolor=#E8E8F0>";
#if($default_lang ne 'fi'){
#$out.="<p><b>$events</b>";
#}else{
#$out.="<p><b>Tapahtumat:</b>";
#}


if ((-e "".$path."coord.txt") eq "1") {

#$out.="<br><b>Live tracking</b>";
open(SISAAN, "<".$path."radat_0.txt");
@trradat=<SISAAN>;
close(SISAAN);

foreach $tr (@trradat){
@r=split(/\|/,$tr);
$out.="<br><br><a href=reitti.".$extension."?act=map&id=0&cID=".$r[0]."&kieli=>$r[2]</a>";
}

	#$out.="<br><a href=reitti.".$extension."?act=map&id=0&kieli=>Live GPS tracking with background map</a>";
	$out.="<p align=\"center\"><big><a href=\"../help/manual.html\">Êàê ïîëüçîâàòüñÿ RouteGadget!</a></big></p>";
}

$out.="<br><div name=eventdiv id=eventdiv></div>
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

<script language=javascript>

	var events = new Array();
	var orgs = new Array();
	var orgyears = new Array();
	var orgopen = new Array();
	var orgyearopen = new Array();
	var eventinfoopen = new Array();
	var eventbydate=0;
	

function go(){}

function update(){
 sTree= getEventTree();
document.getElementById('eventdiv').innerHTML=sTree;
}
		
function getEventTree(){
        var ret='';
        var prevYear=' ';
        var prevOrg=' ';
	var temp=eventbase.split('===');
	var sOrder=sdateorder.split('|');
	var count

	if(eventbydate >-1){
	ret=ret+'[<a href=javascript:go(); onclick=\"eventbydate=-1;makeCookie();update();\">$eventsByOrg</a>] [<b>$eventsByDate</b>]<br><br><center><table cellpadding=2 cellspacing=0>';
	for (var i=eventbydate; i<temp.length-1 && i<eventbydate+$display_in_index; i++) {  
		var field=temp[sOrder[i]].split('|');
		
		var bcolor='#f8f8ff';
		if((i+1)%2 == 0){bcolor='#E8E8F0';}
		
		ret=ret+'<tr><td bgcolor='+bcolor+'>'+field[3]+'</td>';
		
		if(field[6] !=''){
		if(eventinfoopen[field[0]]!=1){
		ret=ret+'<td bgcolor='+bcolor+'><a href=javascript:go(); onclick=\"eventinfoopen[\\''+field[0]+'\\']=1;update();\">$igif</a></td>';
		}else{
		ret=ret+'<td bgcolor='+bcolor+'><a href=javascript:go(); onclick=\"eventinfoopen[\\''+field[0]+'\\']=0;update();\">$igif</a></td>';
		}
		}else{
		ret=ret+'<td bgcolor='+bcolor+'></td>';
		}

		ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.$extension?act=map&id='+field[0]+'>'+field[1]+'</td><td bgcolor='+bcolor+'>'+field[4]+'</td><td bgcolor='+bcolor+'>'+field[5]+'</td>';
";

$out=$out."ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=viimeiset5&eventid='+field[0]+'>$latestRoutes</a></td>';\n";
if($Splitsbrowser==1){
$out.="ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=splitsbrowserjs&id='+field[0]+' target=_blank>Ãðàôèê ñïëèòîâ</a></td>';\n";
}
if($splitalyzer==1){
$out.="ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=splitalyzer&id='+field[0]+' target=_blank>Splitalyzer</a></td>';\n";
}		
$out.=";


		ret=ret+'</tr>';
		if(field[6] !=''){
			if(eventinfoopen[field[0]]==1){		
			ret=ret+'<tr><td colspan=6><table cellpadding=6 align=center width=70% bgcolor=#D8D8E0><tr><td>'+field[6]+'</td></tr></table></td></tr>';
			}
		}
	}
	 ret=ret+'</table>';
	 ret=ret+'</center><br><br>';
	 if(eventbydate >0){
	 	ret=ret+'&nbsp;&nbsp;[<a href=javascript:go(); onclick=\"eventbydate=eventbydate-$display_in_index;update();\">&lt;&lt;&lt;&lt;</a>]';
	 }else{
	 ret=ret+'&nbsp;&nbsp;[&lt;&lt;&lt;&lt;]'
	 }
	 if(temp.length-1 > eventbydate+$display_in_index){
	 	ret=ret+'&nbsp;&nbsp;[<a href=javascript:go(); onclick=\"eventbydate=eventbydate+$display_in_index;update();\">&gt;&gt;&gt;&gt;</a>]';
	 }else{
	 ret=ret+'&nbsp;&nbsp;[&gt;&gt;&gt;&gt;]'
	 }
	 
	}else{
	var sTable=0;
	ret=ret+'[<b>$eventsByOrg</b>] [<a href=javascript:go(); onclick=\"eventbydate=0;makeCookie();update();\">$eventsByDate</a>] <br><br>';
	var bcolor='#f8f8ff';
	for (var i=0; i<temp.length-1; i++) {  
		var field=temp[i].split('|');
		
		if(prevOrg != field[4]){
		if(sTable == 1){sTable=0;ret=ret+'</table>';}
		if(orgopen[field[4]]==1){
		ret=ret+'<br><br>&nbsp;&nbsp;&nbsp;&nbsp;<a href=javascript:go(); onclick=\"orgopen[\\''+field[4]+'\\']=0;makeCookie();update();\">$minusgif'+field[4]+'</a>';
		}else{
		ret=ret+'<br><br>&nbsp;&nbsp;&nbsp;&nbsp;<a href=javascript:go(); onclick=\"orgopen[\\''+field[4]+'\\']=1;makeCookie();update();\">$plusgif'+field[4]+'</a>';
		}
		prevOrg = field[4];
		prevYear=' ';
		}
		if(prevYear != field[2] && orgopen[field[4]]==1){
				if(sTable == 1){sTable=0;ret=ret+'</table>';}
		if(orgyearopen[field[4]+'_'+field[2]]==1){
		ret=ret+'<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href=javascript:go(); onclick=\"orgyearopen[\\''+field[4]+'_'+field[2]+'\\']=0;makeCookie();update();\">$minusgif'+field[2]+'</a><br><table cellpadding=2 cellspacing=0>';
		sTable=1;
		}else{
		ret=ret+'<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href=javascript:go(); onclick=\"orgyearopen[\\''+field[4]+'_'+field[2]+'\\']=1;makeCookie();update();\">$plusgif'+field[2]+'</a>';
		}
		prevYear = field[2];
		}
		if(orgyearopen[field[4]+'_'+field[2]]==1 && orgopen[field[4]]==1){
		
			bcolor='#f8f8ff';
			if((i+1)%2 == 0){bcolor='#E8E8F0';}

		ret=ret+'<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td bgcolor='+bcolor+'>'+field[3]+'</td>';
		
		if(field[6] !=''){
		if(eventinfoopen[field[0]]!=1){
		ret=ret+'<td bgcolor='+bcolor+'><a href=javascript:go(); onclick=\"eventinfoopen[\\''+field[0]+'\\']=1;update();\">$igif</a></td>';
		}else{
		ret=ret+'<td bgcolor='+bcolor+'><a href=javascript:go(); onclick=\"eventinfoopen[\\''+field[0]+'\\']=0;update();\">$igif</a></td>';
		}
		}else{
		ret=ret+'<td bgcolor='+bcolor+'></td>';
		}
		
		ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.$extension?act=map&id='+field[0]+'&kieli=> '+field[1]+'</a></td><td bgcolor='+bcolor+'>'+field[5]+'</td>';
";	
	

if($default_lang ne 'fi'){
$out=$out."ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=viimeiset5&eventid='+field[0]+'>$latestRoutes</a></td>';\n";
}else{
$out=$out."ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=viimeiset5&eventid='+field[0]+'>Uusimmat&nbsp;piirrokset</a></td>';\n";
}
if($Splitsbrowser==1){
$out.="		ret=ret+'<td bgcolor='+bcolor+'><a href=reitti.".$extension."?act=splitsbrowser&id='+field[0]+' target=_blank>Ãðàôèê ñïëèòîâ</a></td>';\n";
}		
$out.="			ret=ret+'</tr>';
		if(field[6] !=''){
		if(eventinfoopen[field[0]]==1){
		ret=ret+'<tr><td colspan=6><table cellpadding=6 align=center width=70% bgcolor=#D8D8E0><tr><td>'+field[6]+'</td></tr></table></td></tr>';		
		}
	}
	}
	}
	}
return ret;
}

function makeCookie(){


sValue='';
 for ( s in orgopen ){
 if(orgopen[s] ==1){
 sValue=sValue+'|'+s;
 }
 }

	var expr = \"\";
	document.cookie =\"RGorgopen=\"+sValue+expr+\"; path=/\";
	
sValue='';
 for ( s in orgyearopen ){
 if(orgyearopen[s] ==1){
 sValue=sValue+'|'+s;
 }
 }
	var expr = \"\";
	document.cookie =\"RGorgyearopen=\"+sValue+expr+\"; path=/\";
	var expr = \"\";
	
	document.cookie =\"RGeventbydate=\"+eventbydate+\"; path=/\";
}

function readCookie(nimi){
	var name = nimi+'=';
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++){
		var j = ca[i];
		while (j.charAt(0)==' ') j = j.substring(1,j.length);
		if (j.indexOf(name) == 0) return j.substring(name.length,j.length);
	}
	return null;
}



var eventbase=''";

$count=0;


@data = sort {
    (split /\|/, $b, 7)[5] cmp
    (split /\|/, $a, 7)[5] ||
     (split /\|/, $a, 7)[4] cmp
    (split /\|/, $b, 7)[4] 
  } @data;

if($in{'first'}!=1){
@data = reverse @data;
}
$preOpenYear='';

$stemp='';

foreach $rec (@data){
$count++;
chomp($rec);
$rec =~ s/\=\=\=//g;
$rec =~ s/\\//g;
$rec =~ s/\'/\\'/g;
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);
($year,$rest)=split(/-/,$paiva);
$out.=" +'$id|$nimi|$year|$paiva|$seura|".$eLevel{$taso}."|$notes==='\n";
$stemp.=($count-1).'|'.$paiva."\n";
if($preOpenYear eq '' && $seura eq $defaultClub){
$preOpenYear=$year;
}

}  

@data = split(/\n/,$stemp);

$out.="var sdateorder='";
@data = sort {
    (split /\|/, $b, 2)[1] cmp
    (split /\|/, $a, 2)[1] 
  } @data;

foreach $rec (@data){
($id,$rest)=split(/\|/,$rec);
$out.="$id|";
}
$out.="';\n";

$out.="

orgyearopen['$defaultClub"."_"."$preOpenYear']=1;
//orgopen['$defaultClub']=1;

var sTempCookie='|'+readCookie('RGorgopen');
	var ss = sTempCookie.split('|');
	for(var i=0;i < ss.length;i++){
	orgopen[''+ss[i]]=1;
	}
var sTempCookie='|'+readCookie('RGorgyearopen');
	var ss = sTempCookie.split('|');
	for(var i=0;i < ss.length;i++){
	orgyearopen[''+ss[i]]=1;
	}	
 eventbydate= 1*readCookie('RGeventbydate');


var sTree= getEventTree();
document.getElementById('eventdiv').innerHTML=sTree;

</script>";

$out.="</ul></p>
";

if($OGraphApplet ==1  && $tyyppi != 3){
if($default_lang eq 'fi'){
$out.="<p>Väliaika-graafit: <a href=reitti.".$extension."?act=OGraphApplet>OGraphApplet</a></p>";
}else{
$out.="<p>Split graphics: <a href=reitti.".$extension."?act=OGraphApplet>OGraphApplet</a></p>";
}
}

$out.="
</td></tr></table></td><td width=1 bgcolor=#005578><img src=$piste height=1 width=1 border=0></td></tr>
<tr><td width bgcolor=#005578 colspan=3><img src=$piste height=5 width=1 border=0>$perloadimages</td></tr>
</table></body></html>";
print $out;
}
exit;  
}

################# sarjat ####################
if ($in{"act"} eq "sarjat"){

## lasketaan montako piirrosta on missäkin sarjassa

$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" || -e $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){

if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
 require Compress::Zlib;
 import Compress::Zlib;
$archived=1;

$gz = gzopen($path."kommentit_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@kommentit=split(/\n/,$data);
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
 
for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
{
$prename=$name; $name = $u->getHeaderInfo()->{Name};
		
if($name eq "kommentit_$in{'eventid'}.txt"){
$archived=1;
$data='';
while (($status = $u->read($buff)) > 0) {
$data.=$buff;
}
@kommentit=split(/\n/,$data);
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
if($archived==0){
open (SISAAN,"<$path"."kommentit_$in{'eventid'}.txt");
@kommentit=<SISAAN>;
close(SISAAN);  
}

foreach $rec (@kommentit) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$rec);
	$i++;

$lkm{$idkilp}++;
}

## luetaan saarjat
open (SISAAN,"<$path"."sarjat_$in{'eventid'}.txt");
if($in{'kohdistus'}eq "1"){
print "1;Koko rastikanta\n";
}else{
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$nimi)=split(/\|/,$rec);
print "$id;$nimi (".(1*$lkm{$id}).")\n";
}
close(SISAAN);
print "99999;kaikki\n";
 
}
}

################# kilpailijat/sarja##############
if ($in{"act"} eq "kilpailijat"){

if($in{'sarja'} ne "99999"){
open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt");

if($in{'viesti'} ne '1'){
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$sarjanro,$sarja,$nimi,$laika,$aika,$sija,$tulos,$valiajat)=split(/\|/,$rec);

if($sarjanro eq $in{'sarja'}){	
print "$id;$sija $nimi $tulos\n";
}
}
}else{
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$sarjanro,$sarja,$nimi,$laika,$osuus,$hajonta,$tulos,$valiajat)=split(/\|/,$rec);

if($sarjanro eq $in{'sarja'}){	
print "$id;$hajonta;$sija $nimi $tulos\n";
}
}


}
close(SISAAN); 
 
}else{

$j=0;$i=0;

open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt"); 
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
	
$i++;

print $id.";$nimi\n"; 
  $j++;
  }

close(SISAAN); 

}

}
################# piirtaneetkilpailijat/sarja##############

############# kilpailijalista ##############
if ($in{"act"} eq "piirtaneetkilpailijat"){
## Tästä appletti kysyy piirtaneetkilpailijat

if($in{'kaikki'} eq "1" && $in{"rata"} ne "99999"){
## tarkistetan piirtäneet tähtimerkintää varten
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt"); 
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
        $tahti{$id}="*";
 }
close(SISAAN); 
###

open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$sarjanro,$sarja,$nimi,$laika,$aika,$sijahajonta,$tulos,$valiajat)=split(/\|/,$rec);

if($sarjanro eq $in{'rata'}){	
if($in{'viesti'} ne '1'){
print "$tahti{$id}$sijahajonta $nimi $tulos ;$id\n";
}else{
print "$tahti{$id} $nimi $tulos;$sijahajonta;$id\n";
}
}
}
close(SISAAN); 

}else{

$j=0;$i=0;

if($in{'viesti'} ne '1'){
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt"); 
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
	
$i++;
if($idkilp eq $in{"rata"} || $in{"rata"} eq "99999"){ ## eli on tässä sarjassa

@ulos[$j]=$nimi.";".$id."\n"; 
  $j++;
  }
 }
close(SISAAN); 
@ulos = sort {
    (split '\;', $a, 2)[1] <=>
    (split '\;', $b, 2)[1]
  } @ulos;
  print @ulos;
  
  }else{ # viesti
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt"); 
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($idkilp,$id,$nimi,$hajonta,$viivat,$rastit)=split(/\|/,$rec);
	
$i++;
if($idkilp eq $in{"rata"} || $in{"rata"} eq "99999"){ ## eli on tässä sarjassa

@ulos[$j]=$nimi.';'.$hajonta.';'.$id."\n"; 
  $j++;
  }
 }
close(SISAAN); 
@ulos = sort {
    (split '\;', $a, 3)[2] <=>
    (split '\;', $b, 3)[2]
  } @ulos;
  print @ulos;
    
  }
}


}  

################# rastit kohdistukseen ##############
if ($in{"act"} eq "rastisto"){
open (SISAAN,"<$path"."sarjojenkoodit_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($sarjaid,$koodit)=split(/\|/,$rec,2);
$codes=$codes."|".$koodit;
}
@dat=split(/\|/,$codes);

$ulos="";

$rastilkm=1;
foreach $rec (@dat){
if($rec ne ''){
if($koodi{$rec}!=1){
$koodi{$rec}=1;
$ulos=$ulos.$rec."\n";
}                     
}
}
print $ulos;
}
################# fotot #############
if ($in{"act"} eq "valokuvat"){
open (SISAAN,"<$path"."valokuvat_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($x,$y,$url)=split(/\|/,$rec,3);

if($x ne '' && $y ne '' && $url ne '' ){	
$x=floor($x);
$y=floor($y);
print "$x;$y;$url\n";
}
}
}
################# valiajat ##############
if ($in{"act"} eq "valiajat"){

$nro=1;$otsikko="-------------------";


open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt");

while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$sija,$tulos,$valiajat)=split(/\|/,$rec);

if($id eq $in{'k'.$nro} && $id < 50000){
@splits=split(/\;/,$valiajat);

$old=0;$i=1;

$ulos=' '.substr($nimi."                   ",0,19);
foreach $rec (@splits){
	chomp($rec);
if($nro==1){
$otsikko=$otsikko.substr("--".$i."----",0,6);
$i++;
}
	$min=floor(($rec-$old)/60);
	$sec=($rec-$old)-60*floor(($rec-$old)/60);
	if ($sec <10){$sec='0'.$sec;}
	$old=$rec;
$ulos=$ulos.substr("$min.$sec     ",0,6);
}
if($nro==1){
print "$otsikko\n";
}
print "$ulos  $nimi\n";
$nro++;
}

}



close(SISAAN); 
print "$otsikko\n"; 


print "\n Route lengths (in pixels) \n";
print "$otsikko------\n";
###


# Tästä apletti saa reittipituuded
# 2|gadget_060225.zip|RouteGadget 25.2.2006 (latest)<p> Now you can make direct links to route drawings. Take a look at latest routes page. Route choice lengths are viewed under split times. A bug in SI csv parser fixed (non english SI files).<br><br>
 
 
open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);  
$viesti=0;
foreach $rec (@kartat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec,4);

if($id==$in{'eventid'} && $tyyppi ==3){
	$viesti=1;
	}
}


$kilp=1;
while($in{"k".$kilp} ne ''){
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");

$ok=0;
while (defined ($rec = <SISAAN>)) {
	chomp($rec);

	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);

if ($in{"k".$kilp} eq $id){
$viiva[$kilp]=$viivat; 
$rast[$kilp]=$rastit;
$nim[$kilp]=$nimi;
$kilp++;$ok=1;
} 
}
close(SISAAN);
if($ok==0){$kilp++;}
} 

## nyt onreittipiirros ja rastipisteet selvillä

$kilp=1;
while($in{"k".$kilp} ne''){ 
if($viiva[$kilp] ne ''){
print substr($nim[$kilp]."                   ",0,20);

if($in{"k".$kilp}<100000){  
@reitti=split(/N/,$viiva[$kilp]);
@rastit=split(/N/,$rast[$kilp]);

$i=0;
$viiva[$kilp]=$viiva[$kilp]."N"; 

$viivatemp="";
foreach $rec (@rastit){

$i++;
if($rec ne ""){
$j="NC".$i."N";$k="N".$rec."N";           
($temp,$viiva[$kilp])=split(/${k}/,$viiva[$kilp],2);  
$viiva[$kilp]="N".$viiva[$kilp];
$viivatemp.=$temp.$j;
}
}      
$viiva[$kilp]=$viivatemp;
$i=0;
foreach $rec (@rastit){ 
$i++;$j="NC".$i."N";$k="N".$rec.'|'.$rec."N";
$viiva[$kilp]=~ s/${j}/${k}/;
}

$viiva[$kilp]=~ s/^\|//;
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 

@rastivalit=split(/\|/,$viiva[$kilp]);
$ulos=join("\n",@rastivalit);

$i=0;

foreach $rec (@rastivalit){
$rec=~ s/^N//;
}

$i_rastit=0;
$i_reitti=0;
$i_piste=0;
$aika=0;
$matka=0;
$totpit=0;

foreach $rc (@rastivalit){

$rastivalit[$i_rastit]=~ s/^N//; 

@viivab=split(/N/,$rastivalit[$i_rastit]);
# lasketaan pituus
$x0=0;
$y0=0;    
$pituus=0;
$i=0;

foreach $rec (@viivab){
($x1,$y1)=split(/\;/,$rec);
if($i>0){            
$pituus=$pituus+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1));
}else{
$alkux=$x1;$alkuy=$y1;
}
$x0=$x1;$y0=$y1;           
$i++;
}
if($alkux !=$x1 && $alkuy !=$y1){
#print substr((floor($pituus/sqrt(($alkux-$x1)*($alkux-$x1)+($alkuy-$y1)*($alkuy-$y1))*1000)/10).'     ',0,5).' ';
#print substr((($pituus-sqrt(($alkux-$x1)*($alkux-$x1)+($alkuy-$y1)*($alkuy-$y1)))).'     ',0,5).' ';
print substr(floor($pituus).'     ',0,5).' ';
$totpit+=$pituus;
}else{
print ' ';
}
$i_rastit++;
}                   
}
print ' '.floor($totpit).'  '.$nim[$kilp]."\n";
}else{
print "\n";
}
$kilp++;
}

###

}

#############################################
if ($in{'act'} eq 'help' ){

# tsekataan kieli
$kieli=$default_lang;  

foreach $rec (@languages){
if($in{'kieli'} eq $rec){$kieli=$rec;}
}


open (SISAAN,"<".$path."../lang_".$kieli.".txt");
@lang=<SISAAN>;
close(SISAAN); 
$lang=join('',@lang);
($lang, $langkiitos)=split(/####/,join('',@lang));

open (SISAAN,"<".$path."../map.txt");
@sivu=<SISAAN>;
close(SISAAN); 

$sivu= join('',@sivu);
($head,$applet,$end)=split(/applet/i,$sivu);
$head=$head.'table  width=100% height=94% cellpadding=25 cellspacing=1><tr><td bgcolor=#E8E8F0>'.$lang.'</td></tr></table'.$end;
$head =~ s/##nimi##/Help/g;
$head =~ s/##httppath##/${httppath}/g;
$head =~ s/##extension##//g;
$head =~ s/##logo##/${logo}/g;
$head =~ s/##icon##/${gadgeticon}/g;
$head =~ s/##piste##/ /g;
$head =~ s/##kieli##/$kieli/g;
$head =~ s/##nimi##/ /g;
$head =~ s/##status##/ /;
$head =~ s/##id##/ /;
$head =~ s/##karttaid##/ /;
$head =~ s/##ratapiirto##/ }/;
$head =~ s/##muu##/ /;   
$head =~ s/##ohjeet##/ /;   
$head =~ s/##width##/ /g;  
$head =~ s/##height##/ /g;
$head=~ s/##languages##/ /;     

print $head;

}
#####################################
if ($in{'act'} eq 'map' ){

if($in{'gps'} ==1){ ## gps asemointi
$pi=3.1415926535897932384626433832795;
$q = $in{CGI};

$file = $q->param('tracklog');
binmode $file;
@d =<$file>;
close($file); 

open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);  


foreach $rec (@kartat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);
if($in{'id'} eq $id){
$mapid=$karttaid;
}
}

open(HANDLE, "<".$path."kartat.txt")|| die;
@kdata=<HANDLE>;
close(HANDLE);
$coord[0]='';
$coord[4]='';

foreach $rec (@kdata){ 
chomp($rec);
	($id,$nimi)=split(/\|/,$rec);
if($id eq $mapid){
	($id,$nimi,$copyright,$s1x,$o1x,$s1y,$o1y,$s2x,$o2x,$s2y,$o2y,$s3x,$o3x,$s3y,$o3y)=split(/\|/,$rec);

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

if($in{'regtest'} eq '1'){ # reg test gpx


open(HANDLE,"<".$path.'coord.txt');
@f=<HANDLE>;
close(HANDLE);

$compmax=0;
foreach $rec (@f){
chomp($rec);
if($rec =~/\|/){
@r=split(/\|/,$rec,2);
$rname{1*$r[0]}=$r[1];
if($compmax < 1*$r[0]){$compmax = 1*$r[0];}
}
}

($o1x,$o1y)=split(/\,/,$f[0]);
($o2x,$o2y)=split(/\,/,$f[1]);
($o3x,$o3y)=split(/\,/,$f[2]);
($s1x,$s1y)=split(/\,/,$f[3]);
($s2x,$s2y)=split(/\,/,$f[4]);
($s3x,$s3y)=split(/\,/,$f[5]);

$s1y=-$s1y;
$s2y=-$s2y;
$s3y=-$s3y;

$lat0=$o1y;
$lon0=$o1x;
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

### 

$splitter="<trkpt";


$d= join('',@d);

($pois, $d)=split(/<trkpt/,$d,2);
@trackpoints=split(/<trkpt/,$d);


foreach $point (@trackpoints){


$p1=index($point,"lat=\"");
$p2=index($point,"\"",$p1+5);
if($p1>-1 && $p2>-1){
$lat=substr($point,$p1+5,$p2-$p1-5);
$lat =~ s/ //g;
$lat =~ s/\"//g;
}

$p1=index($point,"lon=\"");
$p2=index($point,"\"",$p1+5);
if($p1>-1 && $p2>-1){
$lon=substr($point,$p1+5,$p2-$p1-5);
$lon =~ s/ //g;
$lon =~ s/\"//g;
}
($lon,$lat)=($lat,$lon);
$north= (($lat-$lat0)/360*2*$pi*$r);
$east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
$easting = floor($s1x+ ((($Ga*($east-$xnolla1) + $Gb*($north-$ynolla1)))));
$northing= -floor($s1y+ ((($Gc*($north-$ynolla1) + $Gd*($east-$xnolla1)))));

$GPSparam.="1,$easting,$northing;";
}
} # reg test gpx


if($in{'gpstype'} eq 'HST'){
$GPSparam='';
$pi=3.1415926535897932384626433832795;
$splitter="Run";
$start='<'.$splitter;
$end='</'.$splitter.'>';

$sea=$start.'>';
$rep=$start.' >';

$d= join('',@d);
$d=~ s/${sea}/${rep}/g;
$start=$start.' ';

@routes=split(/${start}/,$d);


$routecount=0;
$rec= $routes[1];
$routecount++;

($rec,$del)=split(/${end}/,$rec);

$starttime="Start time unknown";

$p1=index($rec,'StartTime=');
$p2=index($rec,"\"",$p1+12);

if($p1>-1 && $p2>$p1){
$starttime=substr($rec,$p1+10,$p2-$p1-10);
$starttime =~ s/ //g;
$starttime =~ s/\"//g;
$starttime =~ s/t/ /gi;
$starttime =~ s/z/ /gi;
}



@trackpoints=split(/<Trackpoint>/,$rec);
$lat0=-987654;
foreach $point (@trackpoints){

$lat=-9999999;
$lon=-9999999;
$alt=-9999999;

$p1=index($point,'<Time>');
$p2=index($point,'</Time>');
if($p1>-1 && $p2>-1){
#<Time>2006-04-01T05:00:05Z</Time>
$tim=substr($point,$p1+6,$p2-$p1-6);
$tim=~ s/Z//g;
$tim=~ s/\-/\:/g;
$tim=~ s/T/\:/g;
($tyear,$tmon,$tday,$thour,$tmin,$tsec)=split(/\:/,$tim);
$tim=floor(3600*$thour+60*$tmin+$tsec);
$day=$tyear.'_'.$tmon.'_'.$tday;

}

$p1=index($point,'<LatitudeDegrees>');
$p2=index($point,'</LatitudeDegrees>');
if($p1>-1 && $p2>-1){
$lat=substr($point,$p1+17,$p2-$p1-17);
$lat =~ s/ //g;
}

$p1=index($point,'<LongitudeDegrees>');
$p2=index($point,'</LongitudeDegrees>');
if($p1>-1 && $p2>-1){
$lon=substr($point,$p1+18,$p2-$p1-18);
$lon =~ s/ //g;
}
$p1=index($point,'<AltitudeMeters>');
$p2=index($point,'</AltitudeMeters>');
if($p1>-1 && $p2>-1){
$alt=substr($point,$p1+16,$p2-$p1-16);
$alt =~ s/ //g;
}

if($lat!=-9999999 && $lon !=-9999999){

$count++;
if($lat0==-987654){
$lat0=$lat;
$lon0=$lon;
$daycount=0;

$tim0=$tim;
$day0=$day;
$gpsstarttime=$tim0;

}

## this not very scientific, byt must do for now ...
$r=6370000;
$northing=-floor(($lat-$lat0)/360*2*$pi*$r);
$easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi));

if($day0 ne $day){
$day0 = $day;
$daycount++;
}
$tim=$tim+$daycount*60*60*24-$tim0;
$GPSparam.="$tim,$easting,$northing;";
}
}
# add points if too big gaps

@ad=split(/\;/,$GPSparam);
$GPSparam='';

foreach $pt (@ad){
@r=split(/\,/,$pt);
if($edtim ne '' && $ed +3 < $r[0]){

for($i=$edtim+1;$i<$r[0];$i++){

$tim=$i;
$easting=floor(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast);
$northing=floor(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth);

$GPSparam.="$tim,$easting,$northing;";
}
}
$GPSparam.=join(',',@r).";";

$edtim=$r[0];
$edeast=$r[1];
$ednorth=$r[2];
}
} # HST


if($in{'gpstype'} eq 'TCX'){
    $GPSparam='';
    $pi=3.1415926535897932384626433832795;
    $splitter="Activity";
    $start='<'.$splitter;
    $end='</'.$splitter.'>';
    
    $sea=$start.'>';
    $rep=$start.' >';
    
    $d= join('',@d);
    $d=~ s/${sea}/${rep}/g;
    $start=$start.' ';
    
    @routes=split(/${start}/,$d);
    
    
    $routecount=0;
    $rec= $routes[1];
    $routecount++;
    
    ($rec,$del)=split(/${end}/,$rec);
    
    $starttime="Start time unknown";
    
    $p1=index($rec,'StartTime=');
    $p2=index($rec,"\"",$p1+12);
    
    if($p1>-1 && $p2>$p1){
    $starttime=substr($rec,$p1+10,$p2-$p1-10);
    $starttime =~ s/ //g;
    $starttime =~ s/\"//g;
    $starttime =~ s/t/ /gi;
    $starttime =~ s/z/ /gi;
    }
    
    
    
    @trackpoints=split(/<Trackpoint>/,$rec);
    $lat0=-987654;
    foreach $point (@trackpoints){
    
    $lat=-9999999;
    $lon=-9999999;
    $alt=-9999999;
    
    $p1=index($point,'<Time>');
    $p2=index($point,'</Time>');
    if($p1>-1 && $p2>-1){
    #<Time>2006-04-01T05:00:05Z</Time>
    $tim=substr($point,$p1+6,$p2-$p1-6);
    $tim=~ s/Z//g;
    $tim=~ s/\-/\:/g;
    $tim=~ s/T/\:/g;
    ($tyear,$tmon,$tday,$thour,$tmin,$tsec)=split(/\:/,$tim);
    $tim=3600*$thour+60*$tmin+$tsec;
    $day=$tyear.'_'.$tmon.'_'.$tday;
    
    }
    
    $p1=index($point,'<LatitudeDegrees>');
    $p2=index($point,'</LatitudeDegrees>');
    if($p1>-1 && $p2>-1){
    $lat=substr($point,$p1+17,$p2-$p1-17);
    $lat =~ s/ //g;
    }
    
    $p1=index($point,'<LongitudeDegrees>');
    $p2=index($point,'</LongitudeDegrees>');
    if($p1>-1 && $p2>-1){
    $lon=substr($point,$p1+18,$p2-$p1-18);
    $lon =~ s/ //g;
    }
    $p1=index($point,'<AltitudeMeters>');
    $p2=index($point,'</AltitudeMeters>');
    if($p1>-1 && $p2>-1){
    $alt=substr($point,$p1+16,$p2-$p1-16);
    $alt =~ s/ //g;
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
    $northing=-floor(($lat-$lat0)/360*2*$pi*$r);
    $easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi));
    
    if($day0 ne $day){
    $day0 = $day;
    $daycount++;
    }
    $tim=$tim+$daycount*60*60*24-$tim0;
    $GPSparam.="$tim,$easting,$northing;";
    }
    }
    
} # TCX

if($in{'gpstype'} eq 'GPX' || $in{'calib'} eq '1'){
$GPSparam='';
$pi=3.1415926535897932384626433832795;
$splitter="<trkpt";

$gpsxmin=999999;$gpsymin=999999;$gpsxmax=-999999;$gpsymax=-999999;

$d= join('',@d);

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
#<time>2007-02-11T12:21:40.00-05:00</time>

$tim=substr($point,$p1+6,$p2-$p1-6);
$tim=~ s/Z//g;
$tim=~ s/\-/\:/g;
$tim=~ s/T/\:/g;
($tyear,$tmon,$tday,$thour,$tmin,$tsec)=split(/\:/,$tim);
$tim=floor(3600*$thour+60*$tmin+$tsec);
$day=$tyear.'_'.$tmon.'_'.$tday;

}

$p1=index($point,"lat=\"");
$p2=index($point,"\"",$p1+1);
if($p1>-1 && $p2>-1){
$lat=substr($point,$p1+5,$p2-$p1-5);
$lat =~ s/ //g;
$lat =~ s/\"//g;
}

$p1=index($point,"lon=\"");
$p2=index($point,"\"",$p1+1);
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
}

if($lat!=-9999999 && $lon !=-9999999){

$count++;
if($lat0==-987654){
$lat0=$lat;
$lon0=$lon;
$daycount=0;

$tim0=$tim;
$day0=$day;
$gpsstarttime=$tim0;
}

## this not very scientific, byt must do for now ...
$r=6370000;
$northing=-floor(($lat-$lat0)/360*2*$pi*$r);
$easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi));

###
if($Ga ne '' && $in{'calib'} ne '1'){
#($lon,$lat)=($lat,$lon);
$lat0=$kaavao1y;
$lon0=$kaavao1x;

$north= (($lat-$lat0)/360*2*$pi*$r);
$east= (($lon-$lon0)/360*2*$r*$pi *cos($lat0/180*$pi));
$easting = floor($s1x+ ((($Ga*($east-$xnolla1) + $Gb*($north-$ynolla1)))));
$northing= -floor($s1y+ ((($Gc*($north-$ynolla1) + $Gd*($east-$xnolla1)))));
}

##


if($day0 ne $day){
$day0 = $day;
$daycount++;
}
$tim=$tim+$daycount*60*60*24-$tim0;
$GPSparam.="$tim,$easting,$northing;";

   	if($easting>$gpsxmax){$gpsxmax=$easting;$gpsxmaxe=1*$lon;$gpsxmaxn=1*$lat;}
   	if($northing>$gpsymax){$gpsymax=$northing;$gpsymaxn=1*$lat;$gpsymaxe=1*$lon;}
   	if($easting<$gpsxmin){$gpsxmin=$easting;$gpsxmine=1*$lon;$gpsxminn=1*$lat;}
   	if($northing<$gpsymin){$gpsymin=$northing;$gpsyminn=1*$lat;$gpsymine=1*$lon;}

}
}

# add points if too big gaps

@ad=split(/\;/,$GPSparam);
$GPSparam='';

foreach $pt (@ad){
@r=split(/\,/,$pt);
if($edtim ne '' && $ed +3 < $r[0]){

for($i=$edtim+1;$i<$r[0];$i++){

$tim=$i;
$easting=floor(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast);
$northing=floor(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth);

$GPSparam.="$tim,$easting,$northing;";
}
}
$GPSparam.=join(',',@r).";";

$edtim=$r[0];
$edeast=$r[1];
$ednorth=$r[2];
}

} # GPX



#KML (FRWD Google Earth Export)
if ($in{'gpstype'} eq 'KML')
{
$gpsstarttime=0; # unknown

	$GPSparam = '';
	$pi = 3.1415926535897932384626433832795;

	$d = join('', @d);

	($pois, $d) = split(/<coordinates>/i, $d, 2);
	($d, $pois) = split(/<\/coordinates>/i, $d, 2);

	$d =~ s/\t/ /; 
	$d =~ s/\n/ /; 
	$d =~ s/ +/ /;

	@trackpoints = split(/ /, $d);

	$PMKparam = '';
	$e = join('', @d);
	@placemarks = split(/<Placemark>/, $e);
	$kesto = 0;
	$placemarkcount = 0;

	foreach $placemark (@placemarks)
	{
		$placemarkcount++;

		$placemark =~ s/\t/ /; 
		$placemark =~ s/\n/ /; 
		$placemark =~ s/ +/ /;

		$description = $placemark;
		($pois, $description) = split(/<description>/, $description, 2);	
		($description, $pois) = split(/<\/description>/, $description, 2);
		$timeindex = index($description, ':mm:ss): ');

		if ($timeindex > -1)
		{
			$time = $description;
			($pois, $time) = split(/\:mm\:ss\)\: /, $time, 2);
			($time, $pois) = split(/<\/p>/, $time, 2);
			($tunnit, $minuutit, $sekunnit) = split(/\:/, $time, 3);
			$kesto = $tunnit * 60 * 60 + $minuutit * 60 + $sekunnit;	
			
			$coordinates = $placemark;
			($pois, $coordinates) = split(/<coordinates>/, $coordinates, 2);	
			($coordinates, $pois) = split(/<\/coordinates>/, $coordinates, 2);
			($lon, $lat, $alt) = split(/\,/, $coordinates, 3);
			$PMKparam .= "$kesto,$lon,$lat;";
		}
	}

	$trackpointcount = @trackpoints;
	$interval = int($kesto / $trackpointcount + .5);

	@placemarks = split(/\;/, $PMKparam);
	$currentplacemark = 0;

	$lat0 = -987654;
	$tim = 0;
	$runningtim = $interval * -1;

	foreach $point (@trackpoints)
	{
		if ($point)
		{
			$lat = -9999999;
			$lon = -9999999;

			$pmktim = 0;
			$pmklat = -9999999;
			$pmklon = -9999999;

			($pmktim, $pmklon, $pmklat) = split(/\,/, @placemarks[$currentplacemark]);
			($lon, $lat) = split(/\,/, $point);

			if ($lon == $pmklon && $lat == $pmklat)
			{
				$tim = $pmktim;
				$currentplacemark++;

				if ($runningtim + $interval == $tim)
				{
					$runningtim = $tim;
				}
			}
			else
			{
				$tim = $runningtim + $interval;
				$runningtim = $tim;
			}

			if ($lat != -9999999 && $lon != -9999999 && $lat != 0 && $lon != 0)
			{
				$count++;
				if ($lat0 == -987654)
				{
					$lat0 = $lat;
					$lon0 = $lon;
				}
	
				## this not very scientific, byt must do for now ...
				$r = 6370000;
				$northing = -floor(($lat - $lat0) / 360 * 2 * $pi * $r);
				$easting = floor(($lon - $lon0) / 360 * 2 * $r * $pi * cos(abs($lat0) / 180 * $pi));

				$GPSparam .= "$tim,$easting,$northing;";
			}
		}
	}
} # KML (FRWD Google Earth Export)

if($in{'gpstype'} eq 'FRWD'){

$route=join('',@d);
$route =~ s/\r//g;
($head,$route)=split(/Route data\:\n/,$route,2);
($route,$rest)=split(/\n\n/,$route,2);
@d=split(/\n/,$route);

@cols=split(/\t/,$d[0]);

$i=0;
foreach $rec (@cols){
$coli{$rec}=$i;
$i++;
}

$GPSparam='';
$lat0=-987654;
$i=0;
foreach $rec (@d){
if($i>0){
$rec =~ s/\,/\./g;
@cols=split(/\t/,$d[$i]);

$lat=&trim($cols[$coli{'N/S latitude (ddmm.mmmm)'}]);
$lon=&trim($cols[$coli{'E/W longitude (dddmm.mmmm)'}]);

if($lat ne '' && $lon ne '' ){

$lat=substr($lat,0,2)+substr($lat,2,10)/60;
$lon=substr($lon,0,2)+substr($lon,2,10)/60;

if($lat0==-987654){
$lat0=$lat;
$lon0=$lon;
$tim0=1*$cols[$coli{'Time'}];
$gpsstarttime=$tim0;
}

## this not very scientific, byt must do for now ...
$r=6370000;

$N=-floor(($lat-$lat0)/360*2*$pi*$r);
$E=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi));
$tim=1*$cols[$coli{'Time'}]-$tim0;

$GPSparam.="$tim,$E,$N;";
}
}
$i++;
}

# add points if too big gaps

@ad=split(/\;/,$GPSparam);
$GPSparam='';

foreach $pt (@ad){
@r=split(/\,/,$pt);
if($edtim ne '' && $ed +3 < $r[0]){

for($i=$edtim+1;$i<$r[0];$i++){

$tim=$i;
$easting=floor(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast);
$northing=floor(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth);

$GPSparam.="$tim,$easting,$northing;";
}
}
$GPSparam.=join(',',@r).";";

$edtim=$r[0];
$edeast=$r[1];
$ednorth=$r[2];
}
} # FRWD

if($in{'gpstype'} eq 'SDF'){

$route=join('',@d);
$route =~ s/\r//g;
($head,$route)=split(/\[POINTS\]\n/,$route,2);
($route,$rest)=split(/\[/,$route,2);
@d=split(/\n/,$route);

$GPSparam='';
$lat0=-987654;
$i=0;
foreach $rec (@d){
if($i>0){

@cols=split(/\,/,$rec);

# "TP",06.03.2005,16:54.51,60.2565145,24.9067569,6,4.06,159.6,3061.6449732686

$lat=&trim($cols[3]);
$lon=&trim($cols[4]);


$tim=$cols[1].':'.$cols[2];
$tim=~s/\./\:/g;
($tday,$tmon,$tyear,$thour,$tmin,$tsec)=split(/\:/,$tim);
$tim=3600*$thour+60*$tmin+$tsec;
$day=$tyear.'_'.$tmon.'_'.$tday;

if($lat0==-987654){
$lat0=$lat;
$lon0=$lon;
$daycount=0;

$tim0=$tim;
$day0=$day;
$gpsstarttime=$tim0;
}

## this not very scientific, byt must do for now ...
$r=6370000;
$northing=-floor(($lat-$lat0)/360*2*$pi*$r);
$easting=floor(($lon-$lon0)/360*2*$r*$pi *cos(abs($lat0)/180*$pi));

if($day0 ne $day){
$day0 = $day;
$daycount++;
}
$tim=$tim+$daycount*60*60*24-$tim0;

$GPSparam.="$tim,$easting,$northing;";
}
$i++;
}

# add points if too big gaps

@ad=split(/\;/,$GPSparam);
$GPSparam='';

foreach $pt (@ad){
@r=split(/\,/,$pt);
if($edtim ne '' && $ed +3 < $r[0]){

for($i=$edtim+1;$i<$r[0];$i++){

$tim=$i;
$easting=floor(($i-$edtim)/($r[0]-$edtim)*$r[1]+($r[0]-$i)/($r[0]-$edtim)*$edeast);
$northing=floor(($i-$edtim)/($r[0]-$edtim)*$r[2]+($r[0]-$i)/($r[0]-$edtim)*$ednorth);

$GPSparam.="$tim,$easting,$northing;";
}
}
$GPSparam.=join(',',@r).";";

$edtim=$r[0];
$edeast=$r[1];
$ednorth=$r[2];
}
} # SDF
}
## 

# tsekataan kieli
$kieli=$default_lang;  

foreach $rec (@languages){
if($in{'kieli'} eq $rec){$kieli=$rec;}
}


open (SISAAN,"<".$path."../lang_".$kieli.".txt");
@lang=<SISAAN>;
close(SISAAN); 
$lang=join('',@lang);
($lang, $langkiitos)=split(/####/,join('',@lang));
if($in{'kohdistus'}eq "1"){
$muu="<param name=kohdistus value=1>\n<param name=keksi value=$in{'keksi'}>\n";
} 
if($in{'piirrarastit'}eq "1"){
$muu=$muu."<param name=piirrarastit value=1>\n<param name=keksi value=$in{'keksi'}>\n";
}

if($in{'eipiirtaneet'} eq "1" || $norouteanim==1){
$muu=$muu.="<param name=eipiirtaneet value=1>\n";
}     

$muu=$muu."<param name=eventtype value=\"$in{'eventtype'}\">\n";

$muu=$muu."<param name=charset value=\"".$charset_default."\">\n";

$muu=$muu."<param name=preSarja value=\"".$in{'cID'}."\">\n";
$muu=$muu."<param name=preKilp value=\"".$in{'pID'}."\">\n";
$muu=$muu."<param name=GPSTRACK value=\"".$GPSparam."\">\n";
$muu=$muu."<param name=gpsstarttime value=\"".$gpsstarttime."\">\n";

if($in{'calib'} eq '1'){
$muu=$muu."<param name=gpsxmaxe value=\"$gpsxmaxe\">\n";
$muu=$muu."<param name=gpsxmaxn value=\"$gpsxmaxn\">\n";
$muu=$muu."<param name=gpsymaxe value=\"$gpsymaxe\">\n";
$muu=$muu."<param name=gpsymaxn value=\"$gpsymaxn\">\n";

$muu=$muu."<param name=gpsxmine value=\"$gpsxmine\">\n";
$muu=$muu."<param name=gpsxminn value=\"$gpsxminn\">\n";
$muu=$muu."<param name=gpsymine value=\"$gpsymine\">\n";
$muu=$muu."<param name=gpsyminn value=\"$gpsyminn\">\n<param name=keksi value=$in{'keksi'}>\n ";

}

if($in{'calib'} ne '1' &&  $in{'regtest'} ne '1' && ($in{'tracking'} ==1 || $in{'id'} eq '0' ) && ! ($in{'piirrarastit'} eq '1')){
$muu=$muu."<param name=onlinetracking value=\"yes\">\n";
}


if($in{'width'} eq''){$in{'width'}=775; }
if($in{'height'} eq''){$in{'height'}=500; }
$in{'width'}=1*$in{'width'};
$in{'height'}=1*$in{'height'};

open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);  
if($in{'id'} eq '0'){
undef @kartat;
$kartat[0]="0|0|2| | | | |";
}
foreach $rec (@kartat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec,8);
	$nimi=$paiva.' '.$nimi;
if($id eq $in{'id'}){
$muu=$muu."<param name=kisatyyppi value=\"$tyyppi\">\n";
open (SISAAN,"<".$path."../map.txt");
@sivu=<SISAAN>;
close(SISAAN); 
if($id==0 && $in{'mapid'} ne ''){
$karttaid=1*$in{'mapid'};
}
$sivu= join('',@sivu);
$sivu =~ s/##httppath##/${httppath}/g;
$sivu =~ s/##extension##/${extension}/g;
$sivu =~ s/##logo##/${logo}/g;
$sivu =~ s/##icon##/${gadgeticon}/g;
$sivu =~ s/##piste##/${piste}/g;
$sivu =~ s/##kieli##/${kieli}/g;
$sivu =~ s/##nimi##/${nimi}/g;
$sivu =~ s/##status##/2/;
$sivu =~ s/##id##/${in{'id'}}/;
$sivu =~ s/##karttaid##/${karttaid}/;
$sivu =~ s/##ratapiirto##/${in{'ratapiirto'}}/;
$sivu =~ s/##muu##/${muu}/;   
$sivu =~ s/##ohjeet##/${lang}/;   
$sivu =~ s/##width##/${in{'width'}}/g;  
$sivu =~ s/##height##/${in{'height'}}/g;    

$temp='';
foreach $rec (@languages){
$temp=$temp."|<a href=javascript:document.location=document.URL.substring(0,document.URL.indexOf(\"&kieli=\"))+\"&kieli=$rec\">$rec</a>";
}    

$temp=$temp." &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href=reitti.".$extension."?id=$in{'id'}&act=gpsu>GPS</a>";

$temp=~ s/\|//; 
$sivu =~ s/##languages##/${temp}/; 

print $sivu;
exit;
}}
}
################# gps upload ####################
if ($in{"act"} eq "gpsu"){
print"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
.{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
</STYLE>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>
<br>
<b>  GPS track log file upload</b> [<a href='http://www.routegadget.net/grgpshelp/' target='_blank'>Help</a>]<br><br>
<form action='reitti.".$extension."?kieli=' method=post enctype='multipart/form-data'>
<select name=gpstype>
<option value=\" \">Select format</option>
<option value=\"GPX\">GPX</option>
<option value=\"KML\">FRWD KML export</option>
<option value=\"HST\">Garmin HST</option>
<option value=\"TCX\">Garmin TCX</option>
<option value=\"FRWD\">FRWD text export</option>
<option value=\"SDF\">Suunto sdf</option>
</select>
<br>
<br>
<input type=hidden name=id value=$in{'id'}>
<input type=hidden name=act value=map>
<input type=hidden name=gps value=1>
<input type=hidden name=keksi value=-1>
<input type=file name=tracklog>
<input type=submit value=' OK '>
</form>
</center></body></html>
";
#### If KML, saving interval (in seconds):<input type=text name=interval size=4 value=2><br><br>
}

################# animaatio ####################
if ($in{"act"} eq "anim"){
# Tästä apletti pyytää animaatiopisteet
$raika=3; ## step - aika sekunteina 
 
open (SISAAN,"<".$path."kisat.txt");
@kartat=<SISAAN>;
close(SISAAN);  
$viesti=0;
foreach $rec (@kartat) {
	chomp($rec);
	($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec,4);

if($id==$in{'eventid'} && $tyyppi ==3){
	$viesti=1;
	}
}

## haetaan suora reitti
open (SISAAN,"<".$path."ratapisteet_$in{'eventid'}.txt");
@ratap=<SISAAN>;
close(SISAAN); 

foreach $rec (@ratap){ 
	chomp($rec);
($id,$data)=split(/\|/,$rec,2);
@temp=split(/N/,$data);
$data="";
 foreach $recb (@temp){ 
	chomp($recb);
 ($x,$y)=split(/\;/,$recb,2);
$data=$data.($x).";".($y)."N";
	}

$suorareitti{$id}=$data;
($pis,$data)=split(/N/,$data,2);
$suorarastit{$id}=$data;
}
## suora reitti ok

## haetaan valiajat
$kilp=1;$laikaMin=99999999;
#while($in{"k".$kilp} ne''){ 
open (SISAAN,"<$path"."kilpailijat_$in{'eventid'}.txt"); 

$ok=0;
while (defined ($rec = <SISAAN>) && $in{"k".$kilp} ne'') {
	chomp($rec);
	($id,$sarjanro,$sarjanimi,$nimi,$laika,$aika,$sija,$tulos,$valiajat,$GPSa)=split(/\|/,$rec);

if($id eq $in{'k'.$kilp}){
$lahtoaika[$kilp]=$laika; 
if($laika<$laikaMin){
$laikaMin=$laika;
}
$vajat[$kilp]=$valiajat;
$gpsani[$kilp]=$GPSa;
$srj{$kilp}=$sarjanro; 

if($viesti ==1){
$srj{$kilp}=$sija; 
}

$kilp++;$ok=1;
seek(SISAAN, 0, 0);
}
}

if($ok==0){exit;}
#}
close(SISAAN); 
# valiajat nyt muuttujassa $vajat[] 

$kilp=1;
while($in{"k".$kilp} ne''){
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");

$ok=0;
while (defined ($rec = <SISAAN>)) {
	chomp($rec);

	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);

if ($in{"k".$kilp} eq $id){
$viiva[$kilp]=$viivat; 
$rast[$kilp]=$rastit;
$kilp++;$ok=1;
} 
}
if($ok==0){ # ei ollut piirtänyt, tilalle suora reitti
$viiva[$kilp]="N".$suorareitti{$srj{$kilp}};
$rast[$kilp]="N".$suorarastit{$srj{$kilp}};
$kilp++;
#exit;
}
} 
close(SISAAN);
## nyt on valiajat, reittipiirros ja rastipisteet selvillä
## nyt lasketaan animaatioille pisteet
## tämä pitäisi tehdä clientissä serveriä säästääksemme, mutta
## ei nyt jaksa javalla väsätä, ehkä sitten joskus

$kilp=1;
while($in{"k".$kilp} ne''){ 
$aikasiirto=0;  
if($in{"k".$kilp}<50000){  
print ''.($lahtoaika[$kilp]-$laikaMin).';';
@reitti=split(/N/,$viiva[$kilp]);
@valiajat=split(/\;/,$vajat[$kilp]);
@rastit=split(/N/,$rast[$kilp]);

$i=0;
$viiva[$kilp]=$viiva[$kilp]."N"; 

$viivatemp="";
foreach $rec (@rastit){

$i++;
if($rec ne ""){
$j="NC".$i."N";$k="N".$rec."N";           
($temp,$viiva[$kilp])=split(/${k}/,$viiva[$kilp],2);  
$viiva[$kilp]="N".$viiva[$kilp];
$viivatemp=$viivatemp.$temp.$j;
}
}      
$viiva[$kilp]=$viivatemp;
$i=0;
foreach $rec (@rastit){ 
$i++;$j="NC".$i."N";$k="N".$rec.'|'.$rec."N";
$viiva[$kilp]=~ s/${j}/${k}/;
}

$viiva[$kilp]=~ s/^\|//;
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 
$viiva[$kilp]=~ s/NN/N/g; 

@rastivalit=split(/\|/,$viiva[$kilp]);
$ulos=join("\n",@rastivalit);

$i=0;

$matkasiirto=0;
foreach $rec (@rastivalit){
$rec=~ s/^N//;
$matkasiirto=0;
$i++;
}

$i_rastit=0;
$i_reitti=0;
$i_valiajat=0;
$i_piste=0;
$aika=0;
$matka=0;
$eka=1;
while ($valiajat[$i_rastit] ne '' && ($i_rastit==0 || $valiajat[$i_rastit]>$valiajat[$i_rastit-1])){

$rastivalit[$i_rastit]=~ s/^N//; 

@viivab=split(/N/,$rastivalit[$i_rastit]);
# lasketaan pituus
$x0=0;
$y0=0;    
$pituus=0;
$i=0;

$lisaaika=0;
foreach $rec (@viivab){
($x1,$y1)=split(/\;/,$rec);
if($i>0){            
$pituus=$pituus+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1));
if($x0 == $x1 && $y0 == $y1){
## 2 peräkkäistä klikkausta = pysähdys 3 sec
 $lisaaika=$lisaaika+3;
}
}
$x0=$x1;$y0=$y1;           
$i++;
}
                  
$valiaika=$valiajat[$i_rastit]-$valiajat[$i_rastit-1];
if($i_rastit==0){
$valiaika=$valiajat[$i_rastit];
}
## hyomioidaan pysähdykset
$valiaika=$valiaika-$lisaaika;
if($valiaika ==0 || $valiaika<0 ){
 $valiaika=0.00001;
}
$step=($pituus/($valiaika/$raika));

$matkasiirto=$aikasiirto*$step;
# pisteet polylinen varrelle 
$i=0;$seis=0;
foreach $rec (@viivab){
($x1,$y1)=split(/\;/,$rec);
if($i>0){   
if($x0 == $x1 && $y0 == $y1){
$seis++;
## ei kahta peräkkäistä klikkausta samaan pisteeseen
}else{
$plkm=1;
while($matka+$step*$plkm-$matkasiirto < $matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))){
$i_piste++; 
#lasketaan animaatioreittipiste
$ax=floor((($step*$plkm-$matkasiirto)*$x1+$x0*(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($step*$plkm-$matkasiirto)))/(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))));
$ay=floor((($step*$plkm-$matkasiirto)*$y1+$y0*(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($step*$plkm-$matkasiirto)))/(sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))));
$info="";
if($eka==1){
$eka=0;
$info='C';
}
print "$ax;".$ay.",".$info."N";
$info="";
if($seis > 0){
for($ii=0;$ii<$seis;$ii++){
print "$ax;$ay,".$info."N";
}
$seis=0;
}
$plkm++;
} 
$matkasiirto=$matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1))-($matka+$step*($plkm-1)-$matkasiirto);
$matka=$matka+sqrt(($x0-$x1)*($x0-$x1)+($y0-$y1)*($y0-$y1));
$aikasiirto=$matkasiirto/$step*1;
} 
}
$x0=$x1;$y0=$y1;   
$i++;
}
$i_rastit++;
$eka=1;
} 
}else{
## gps animaatip
#print "0;0;0,0N";
print ''.($lahtoaika[$kilp]-$laikaMin).';';
print $gpsani[$kilp];
}
$kilp++;
print "\n";
}

}
################# viivat ####################
if ($in{"act"} eq "viivat"){
## tästä appletti lataa viivat

open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
@merkinnat=<SISAAN>;
close(SISAAN);
  

$kilp=1;
while($in{"k".$kilp} ne''){
$in{"id"}=$in{"k".$kilp};

$i=0;$loytyi=0;
foreach $rec (@merkinnat) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
	$i++;

if ($in{"id"} eq $id){
$i++;        $loytyi=1;
$viivat =~ s/N/\n/g;
$viivat =~ s/R/\r/g;
$viivat =~ s/#/g/;
print "\n1".$viivat;
}
}


if($i==0){
print " ";
}
if($loytyi==0){
print "\n1\n0;0";
}
print "\n";
$kilp++;   
} 

}

################# kommentit ####################
if ($in{"act"} eq "kommentit"){
## Tästä apletti pyytää kommentit

$archived=0;
if($in{'eventid'}!=0 && (-e $path."archive.zip" || -e $path."archive_".$in{'eventid'}.".zip" || -e $path."sarjat_$in{'eventid'}.txt.gz") && !(-e $path."sarjat_$in{'eventid'}.txt")){

if(-e $path."sarjat_$in{'eventid'}.txt.gz"){
require Compress::Zlib;
import Compress::Zlib;
$archived=1;

$gz = gzopen($path."kommentit_".$in{'eventid'}.".txt.gz", "rb");
$data='';while ($gz->gzreadline($_) > 0) {$data.=$_;}; $gz->gzclose();
@kommentit=split(/\n/,$data);
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
 
for ($status = 1; $status > 0 && $status2 == 1; $status = $u->nextStream())
{
$prename=$name; $name = $u->getHeaderInfo()->{Name};
		
if($name eq "kommentit_$in{'eventid'}.txt"){
$archived=1;
$data='';
while (($status = $u->read($buff)) > 0) {
$data.=$buff;
}
@kommentit=split(/\n/,$data);
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
if($archived==0){
open (SISAAN,"<$path"."kommentit_$in{'eventid'}.txt");
@kommentit=<SISAAN>;
close(SISAAN);  
}

$kilp=1;
while($in{"k".$kilp} ne''){
$in{"id"}=$in{"k".$kilp};

$i=0;
foreach $rec (@kommentit) {
	chomp($rec);
	($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$rec);
	$i++;

if ($in{"id"} eq $id){
$kommentit =~ s/#nl#/\n/g;
$kommentit =~ s/#cr#/\r/g;  
#$kommentit=~ s/\;/#chsmcl#/g;
print "\n\n$nimi:\n".$kommentit;
}
}
$kilp++;
} 
}
#
####### TALLENNUKSET##########################################

############# Reittipiirroksen tallennus ######################
if($in{'act'} eq "tallennapiirros"){

open (HANDLE,"<".$path."kilpailijat_$in{'eventid'}.txt");
@d=<HANDLE>;
close HANDLE;  


if($in{'lisaa'} eq '1'){ ## if add mode   
## get ID

foreach $rec (@d){
($id,$rest)=split(/\|/,$rec,2);
if($id>50000){$id=$id-50000;}
if($in{'id'} < $id){$in{'id'}=$id;}
}
$in{'id'}=(1*$in{'id'})+1;
}else{

## read original version of name, to avoid some charset trouble

foreach $rec (@d){
@r=split(/\|/,$rec);
if($in{'id'} == $r[0] && $r[3] ne ''){$in{'suunnistaja'}=$r[3];}
}

}

## input

$in{'suunnistaja'}=~ s/#chsmcl#/\;/g;
$in{'suunnistaja'}=~ s/#chnd#/\&/g;

$in{'kommentit'}=~ s/#chsmcl#/\;/g;
$in{'kommentit'}=~ s/#chnd#/\&/g;


## gps 
if($in{'GPS'}==1){
$lahtoaika=-1;
foreach $rec (@d){
($id_t,$sarjanro_t,$sarjanimi_t,$nimi_t,$laika_t,$aika_t,$sija_t,$tulos_t,$valiajat_t,$GPSa_t)=split(/\|/,$rec);
if($id_t == $in{'id'}){
$lahtoaika=$laika_t;
}
}

$in{'suunnistaja'}=' GPS '.$in{'suunnistaja'};
$in{'id'}=50000+$in{'id'};
}
open (SISAAN,"<$path"."merkinnat_$in{'eventid'}.txt");
@merkinnat=<SISAAN>;
close(SISAAN);  

$ok=1;

foreach $rec (@merkinnat) {
	chomp($rec);
	($idkilp,$id,$nimi,$hajonta,$viivat,$rastit)=split(/\|/,$rec);
	
if($id	eq $in{'id'}){
$ok=0; ## eli piirros oli jo olemassa, ei tallenneta
}
}

$in{'rdata'}=~ s/\,/\;/g;
($reitti,$rastit)=split(/\|/,$in{'rdata'});

if($ok  == 1){

if($in{'GPS'}!=1){
open (HANDLE,">>".$path."merkinnat_$in{'eventid'}.txt");
&lock_file;
print HANDLE $in{'rataid'}."|".$in{'id'}."| $in{'suunnistaja'}|$in{'hajonta'}|$reitti|$rastit\n";
&unlock_file;
close HANDLE;
}else{

@GPSD=split(/N/,$reitti);
$reitti='';

foreach $gd (@GPSD){
chomp($gd);
if($gd ne ''){
($Gx,$Gy,$Gt)=split(/\;/,$gd);
if($Gx ne $GxOLD && $Gy ne $GyOLD){
$reitti.='N'.$Gx.';'.$Gy;
$GxOLD=$Gx;
$GyOLD=$Gy;
}
}
}
$reitti.='|';

## gps animaatio
$GAIKA=0;$ani='';
foreach $gd (@GPSD){
chomp($gd);
if($gd ne ''){
($Gx,$Gy,$Gt)=split(/\;/,$gd);

while($Gt > $GAIKA){
$ani.=$Gx.';'.$Gy.',0N';
$GAIKA=$GAIKA+3;
}

}
}

open (HANDLE,">>".$path."merkinnat_$in{'eventid'}.txt");
&lock_file;
print HANDLE $in{'rataid'}."|".$in{'id'}."| $in{'suunnistaja'}|$in{'hajonta'}|$reitti|$rastit\n";
&unlock_file;
close HANDLE;



}

$in{'kommentit'}=~ s/\n/#nl#/g;
$in{'kommentit'}=~ s/\r/#cr#/g;

$in{'kommentit'} =~ s/\<//g;
$in{'kommentit'} =~ s/\>//g;
open (HANDLE,">>".$path."kommentit_$in{'eventid'}.txt");
&lock_file;
print HANDLE $in{'rataid'}."|".$in{'id'}."|$in{'suunnistaja'}||$in{'kommentit'}\n";
&unlock_file;
close HANDLE;  
         
if($in{'lisaa'} eq '1'  || $in{'GPS'}==1){ ## if add mode   

if($in{'GPS'}!=1){
## leg lengths
($pois,$lahto,$muut)=split(/N/,$reitti,3);

$sLength=0;
@aControls=split(/N/,($lahto.$rastit));
$ai=0;
foreach $aControl (@aControls){
$ai++;
if($ai>1){
($ax1,$ay1)=split(/\;/,$aControls[$ai-2]);
($ax2,$ay2)=split(/\;/,$aControls[$ai-1]);
$aleg[$ai-1]=sqrt(($ax1-$ax2)*($ax1-$ax2)+($ay1-$ay2)*($ay1-$ay2)); # Pythagoras 
}
}


##



$usersplits='';
$splitnro=0;$splitmissing=0;
@splits=split(/m/,$in{'usersplits'});
foreach $split (@splits){
$splitnro++;
($min,$sec)=split(/s/,$split);

if(floor(60*$min+(1*$sec))>0 && $splitmissing==0){
$usersplits.=floor(60*$min+(1*$sec)).';';
$lastsplit=floor(60*$min+(1*$sec));
}

if(floor(60*$min+(1*$sec))==0){# a split is missing
	if($splitmissing==0){
		$splitmissing=$splitnro;
	}
}

if(floor(60*$min+(1*$sec))>0 && $splitmissing>0){ # there has been missing split before this split
$sLength=0;
for($j=$splitmissing;$j<$splitnro+1;$j++){
$sLength=$sLength+$aleg[$j];
}

$averagespeed=(floor(60*$min+(1*$sec))-$lastsplit)/$sLength;

$sLength=0;
for($j=$splitmissing;$j<$splitnro+1;$j++){
$sLength=$sLength+$aleg[$j];
$usersplits.=floor($lastsplit+$sLength*$averagespeed).';';
}
$splitmissing=0;
$lastsplit=floor(60*$min+(1*$sec));
}
}


$result=$min.':'.$sec;

}# if gps!=1

if($in{'GPS'}==1){
$GPSani=$ani;
}
open (HANDLE,">>".$path."kilpailijat_$in{'eventid'}.txt");
&lock_file;

if($in{'hajonta'} eq 'null'){
$in{'hajonta'}='';
}
$lahtoaika=floor(1*$lahtoaika);
if($lahtoaika ==-1){
$lahtoaika=floor(1*$in{'gpsstarttime'});
}

print HANDLE $in{'id'}."|".$in{'rataid'}."||$in{'suunnistaja'}|$lahtoaika||$in{'hajonta'}|$result|$usersplits|$GPSani\n";
&unlock_file;
close HANDLE; 

}                        
}
print "\n";
exit;
}
###################### tallennusonnistui-sivu #################
if ($in{"act"} eq "tallennettu"){

## language check
$kieli="fi";
foreach $rec (@languages){
if($rec eq $in{'kieli'}){
	$kieli=$rec;
}
}

open (SISAAN,"<".$path."../lang_".$kieli.".txt");
@lang=<SISAAN>;
close(SISAAN); 
$lang=join('',@lang);
($lang, $langkiitos)=split(/####/,join('',@lang));

print " 
<HTML>
<HEAD>
<TITLE>OK</TITLE>
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
th{font-family: Verdana, Arial, Helvetica, sans-serif; color: #FFFFFF; font-size: 13px; }
.{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight: bold; }
a{font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 10px; }
.credits{font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 8px; font-weight : bold; }
</STYLE>
<link rel=\"shortcut icon\" href=\"$gadgeticon\">
</HEAD>

<BODY BGCOLOR=#FFFFFF>
<center><br><br><br><br><br><br><br>

<a href='reitti.".$extension."?act=map&id=".$in{'eventid'}."&kieli=".$in{'kieli'}."'>$langkiitos</a>

</center>
</BODY>
</HTML>";
exit;
}


################# radat ####################
if ($in{"act"} eq "rata"){   
if($in{'kohdistus'} ne '1'){
## tästä appletti kysyy radan ratapiirrokset

## jos viestimoodi
if($in{"hajonnat"} ne''){

open (SISAAN,"<$path"."radat_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$status,$nimi,$viivat)=split(/\|/,$rec);


if ($in{"id"} eq $id || index($in{"hajonnat"},'s'.$id.'s')>-1){
$viivat =~ s/N/\n/g;
$viivat =~ s/R/\r/g;
$viivat =~ s/#//g;
print "$viivat\n";

} 
}
close(SISAAN); 
}else{#henk koht
open (SISAAN,"<$path"."radat_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$status,$nimi,$viivat)=split(/\|/,$rec);
if ($in{"id"} == $id || $in{"id"} eq '99999'){
$viivat =~ s/N/\n/g;
$viivat =~ s/R//g;
$viivat =~ s/#//g;
if($in{"id"} ne '99999'){
print "$viivat\n";
}else{
$count++;
$out.=$viivat."\n";
}
} 
}
close(SISAAN); 

if($in{"id"} eq '99999'){ ## vain ympyrät kaikkien ratojen systeemiin

if($count > 10){
@d=split(/\n/,$out);

$out='';
foreach $rec (@d){
($type,$rest)=split(/\;/,$rec,2);
if($e{$rec} eq'' && $type eq '1'){
$e{$rec}=1;
print "$rec\n";
}
}
}else{
print $out;
}
}
}# henkkoht moodi
}else{
open (SISAAN,"<$path"."rastikanta_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$x,$y)=split(/\|/,$rec);
       $x=floor($x*10); $y=floor($y*10);
print "1;$x;$y;0;0\n";

}
close(SISAAN); 
}
}  
################# ratapisteet ####################
if ($in{"act"} eq "ratapisteet"){   

## tästä appletti kysyy radan ratapiirrokset
open (SISAAN,"<$path"."ratapisteet_$in{'eventid'}.txt");
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
	($id,$pisteet)=split(/\|/,$rec);
if ($in{"id"} == $id ){
$pisteet =~ s/N/\n/g;
print "$pisteet\n";
} 
}
close(SISAAN); 
 
}
 
###############################################################
sub lock_file{
if($locking eq '1'){
$exit=15;  # max yritykset/sekunnit
$lock_i=0; 
if (!flock (HANDLE,LOCK_EX) ){
$released=FALSE;
until ($released eq TRUE || $lock_i>$exit) { 
$lock_i++;
sleep 1;
if (flock(HANDLE,2)) {
$released=TRUE;
}
} 
} 
if ($lock_i>$exit) {
print "Lock error. - Virhe lukituksessa. <br> If this is new insall: path is wrong, there is no enough permissios or locking should be turned of on this server.";
exit;
}
}
}
sub trim {
    my $string = shift;
    for ($string) {
        s/^\s+//;
        s/\s+$//;
    }
    return $string;
}
sub unlock_file {
if($locking eq '1'){
flock(HANDLE,LOCK_UN);
}
}
