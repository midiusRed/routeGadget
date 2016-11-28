#!/usr/bin/perl

###################################################################
#  reittimanager.pl  or reittimanager.pl                          #
###################################################################
# Reittihärveli   -      Sovellus suunnistuksen reittipiirrosten  #
# (RouteGadget)             keräykseen  ja esittämiseen tämiseen  #
#                                                                 #
# ================================================================#
# Copyright (c) 2003-2014 Jarkko Ryyppö - All Rights Reserved.    #
# Software by:        Jarkko Ryyppö                               #
# Sponsored by:       -                                           #
###################################################################
# The software is free for non-commercial use.  The software can  #
# be used only for purposes related to the sport orienteering.    #
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
# By installing and/or using our software, you agree with these   #
# terms of use.                                                   #
###################################################################

use Fcntl ":flock";
use POSIX;

use CGI qw(:cgi-lib); 
#use CGI::Carp qw{fatalsToBrowser};

$CGI::POST_MAX=1024 * 12000;  # max 12000K posts

#########################################################################################
$RG_version='RouteGadget reittimanager.cgi version: 20150203';
## Path to "kartat" -folder
##   1. Chmod
 $chmod='1'; # You can use chmod on your server (UNIX, Linux)
# $chmod='0'; # You cannot use chmod (windows)
##  
## 2. File locking (turn this off if you get lock errors or 500 errors no matter what you do)
##
#$locking=1; # locking is on
$locking=0; # locking is off
##                    
## 3. Path to 'kartat' -folder
$path='../../kartat/';
##
## For Windows:
#$path='c:/inetpub/wwwroot/gadget/kartat/';
##          
## 4. Manager language ('en' or 'fi')
$lang='en';
##
## Default charset:
$charset_default='WINDOWS-1251';
##
## Use text field ('field') or dropdown list ('list') for Club Name
## If using list, a text file called 'clubnames.txt' in the kartat folder
## holds the configured list of names, one per line
$clubnames_type='field';
#$clubnames_type='list';
##
## Allow ('1') or disallow ('0') Club Names list to be edited from the manager interface
$allow_clubname_edit='0';
##
## Default club name for text field input
## (Write here your club name, you'll not need to write it again every time):
$club_default='';

#########################################################################################


ReadParse();

if($in{'act'} ne 'routedxf'){ 
print "Content-Type: text/html; charset=$charset_default\n\n";
}

$in{'eventid'}=1*$in{'eventid'};

## Check extension
$apu=$0;
$apu=~ s/\\/\//g;
@apu = split (/\//,$apu);
($remove,$extension)= split(/\./,$apu[$#apu]);
    
($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year=$year+1900;
$mon++;
#########################################################################################
##################### Version #############################3
if($in{'act'} eq 'version'){ 
print $RG_version;
exit;
}

#########################################################################################
## tsekataan aluksi salasana & tunnus
# logout
if($in{'act'} eq 'logout'){ 
open(HANDLE, ">".$path."keksi.txt") || die;
print HANDLE "";
close(HANDLE);
print "Logout OK!"; 
print "<br><a href=reittimanager.".$extension.">Back to Manager</a>";
print "<br><a href=../reitti.".$extension.">Back to RouteGadget</a>";
exit;
}
## tsekataan salasana & tunnus
if ((-e "".$path."uspsw.txt") ne "1") {
if($in{'nlogin'} ne '' && $in{'npassword'}){
if(length($in{'nlogin'})<3 && length($in{'npassword'}) <3){
print "Too short password/login string (min 3 chars)";
exit;
}else{
open(HANDLE, ">".$path."uspsw.txt") || die;
$string=crypt($in{'nlogin'}, $in{'npassword'});
print HANDLE $string; 
close(HANDLE);  
if($chmod eq '1'){
system "chmod 711 ".$path."uspsw.txt";
}
print "Saving OK! <a href=reittimanager.".$extension.">Log in</a>";
exit;
}
}else{         
if($lang ne 'fi'){
print "<html>There is no password yet. Give a login and password and remember it.

<form action=reittimanager.".$extension." method=post>  
<input type=hidden name=keksi value=$in{'keksi'}> 
<table>
<tr><td>New Login:</td><td><input type=text name=nlogin></td></tr>
<tr><td>New Passwd:</td><td><input type=text name=npassword></td></tr></table>
<p><input type=submit value=\"   OK    \" size=20> </form><p>";       
}else{
print "<html>There is no password yet. Give a login and password and remember it.

<form action=reittimanager.".$extension." method=post>  
<input type=hidden name=keksi value=$in{'keksi'}> 
<table>
<tr><td>Uusi tunnus:</td><td><input type=text name=nlogin></td></tr>
<tr><td>Uusi salasana:</td><td><input type=text name=npassword></td></tr></table>
<p><input type=submit value=\"   OK    \" size=20> </form><p>";   

}

exit;
}
}else{
if($in{'login'} eq '' && $in{'password'}eq '' ){
if($in{'keksi'} eq''){    

if($lang ne 'fi'){
print "<html>RouteGadgetManager
<form action=reittimanager.".$extension." method=post>  
<input type=hidden name=keksi value=$in{'keksi'}>
<table>
<tr><td>Login:</td><td><input type=text name=login></td></tr>
<tr><td>Passwd:</td><td><input type=password name=password></td></tr></table>
<p><input type=submit value=\"   OK    \" size=20> </form><p></html>";
}else{
print "<html>RouteGadgetManager
<form action=reittimanager.".$extension." method=post>  
<input type=hidden name=keksi value=$in{'keksi'}>
<table>
<tr><td>Tunnus:</td><td><input type=text name=login></td></tr>
<tr><td>Salasana:</td><td><input type=password name=password></td></tr></table>
<p><input type=submit value=\"   OK    \" size=20> </form><p></html>";
}
exit;       
}else{
## tsekataan keksi
open(HANDLE, "<".$path."keksi.txt") || die;
@d=<HANDLE>;
close(HANDLE);
$d=join('',@d);
if($d eq $in{'keksi'} && length($d)>0){
## ok
}else{
print "Session expired<br><a href=reittimanager.".$extension.">Manager</a>";
exit;
}
}
}else{  
$string=crypt($in{'login'}, $in{'password'});
open(HANDLE, "<".$path."uspsw.txt") || exit;
@d=<HANDLE>;
close(HANDLE);
$d=join('',@d);
if($d eq $string) {
print "OK!";
srand;
$keksi=rand; 
open(HANDLE, ">".$path."keksi.txt") || die;
print HANDLE $keksi;
close(HANDLE);     
if($chmod eq '1'){
system "chmod 711 ".$path."keksi.txt";
}
$in{'keksi'}=$keksi;
}else{
print "password was not correct, sorry!";
exit;
}
}
}
          

###########################################
if($in{'act'} eq 'routedxf'){  

$in{'kisaid'}=1*$in{'kisaid'};

print "Content-Type:application/x-download\n";  
print "Content-Disposition:attachment;filename=routes.dxf\n\n"; 
## alku
print "  0
SECTION
  2
ENTITIES
  0\n";


open (SISAAN,"<".$path."merkinnat_".$in{'kisaid'}.".txt");
$i=0;
while (defined ($rec = <SISAAN>)) {
	chomp($rec);
($idkilp,$id,$nimi,$aika,$viivat)=split(/\|/,$rec);

$i++;

$nimi  =~ s/ /_/g;
$nimi =substr($nimi,0,15); ## ocad7 lukee 15 merkin layerinnimen
$korvaus="\n  0
VERTEX
  8
$nimi
 10\n";
$viivat =~ s/N/${korvaus}/g;
$korvaus="\n 20\n";
$viivat =~ s/\;/${korvaus}/g;

$data="POLYLINE
 66
1
  8
$nimi".$viivat."
0
SEQEND
  0\n";
$data=$data."TEXT
  8
603.1
 10
 0.0
 20
 ".(-$i*5)."
  1
$nimi
 50
0.00
  0\n";
print $data;
}
close(SISAAN); 

  
print "ENDSEC
  0
EOF\n";
exit;
}
###########################################
if($in{'act'} eq 'tallennaeditointi'){  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
print "<a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);
$out='';
foreach $rec (@data){ 
	chomp($rec);
	($idkilp,$map,$type,$name,$paiva,$seura,$taso,$notes)=split(/\|/,$rec);
if($idkilp eq $in{'kisaid'}){
$in{'eventname'}=~s/\|//g;
$in{'clubname'}=~s/\|//g;
$in{'notes'}=~s/\|//g;
$in{'notes'}=~s/\n/<br>/g;
$in{'notes'}=~s/\r//g;
$s='&#39;';
$in{'eventname'}=~s/\'/${s}/g;
$in{'clubname'}=~s/\'/${s}/g;
$in{'notes'}=~s/\'/${s}/g;
$s='&quot;';
$in{'eventname'}=~s/\"/${s}/g;
$in{'clubname'}=~s/\"/${s}/g;
$in{'notes'}=~s/\"/${s}/g;

$out.=$idkilp.'|'.$map.'|'.$type.'|'.$in{'eventname'}.'|'.$in{'year'}.'-'.$in{'month'}.'-'.$in{'day'}.'|'.$in{'clubname'}.'|'.$in{'eventlevel'}.'|'.$in{'notes'}."\n";
}else{
$out.=$rec."\n";
}
}
open(HANDLE, ">".$path."kisat.txt")|| die;
&lock_file;
print HANDLE $out;
&unlock_file;
close(HANDLE);
print "Saved!  Tallennettu!";
exit;
}
###########################################
if($in{'act'} eq 'editoitietoja'){  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
print "<a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";


open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

foreach $rec (@data){ 
	chomp($rec);
	($idkilp,$map,$type,$name,$paiva,$seura,$taso,$notes)=split(/\|/,$rec);
if($idkilp eq $in{'kisaid'}){
print "<form action=reittimanager.".$extension." method=post>     
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=kisaid value=$in{'kisaid'}>
<input type=hidden name=act value=tallennaeditointi>";



print "<p>Event name - Tapahtuman nimi:<br>
<input size=100 type=text name=eventname value=\"$name\">";
print "<p>Club name - seuran nimi:<br>";
if($clubnames_type eq 'field'){
print "<input size=100 type=text name=clubname value=\"$seura\">";
}
if($clubnames_type eq 'list'){
$sel{$seura}=' selected';
open (SISAAN,"<".$path."clubnames.txt");
@data=<SISAAN>;
close(SISAAN);
@data=sort {$a <=> $b} @data;
print "<select name=clubname>";
print "<option value='Unclassified'$sel{'Unclassified'}>Select a Club Name below</option>";
foreach $rec (@data){ 
chomp($rec);
($sortid,$clubname)=split(/\|/,$rec);
print "<option value='$clubname'$sel{$clubname}>$clubname</option>\n";
}
print "</select><p>";
}
$sel{$taso}=' selected';

print "<p>Event level<br>
<select name=eventlevel>
<option value=I$sel{'I'}>Ìåæäóíàðîäíûå</option>
<option value=N$sel{'N'}>Âñåðîññèéñêèå</option>
<option value=R$sel{'R'} selected>Îáëàñòíûå</option>
<option value=L$sel{'L'}>Ãîðîäñêèå</option>
<option value=T$sel{'T'}>Òðåíèðîâî÷íûå</option>
</select><p>";

print "<p>Event date - Tapahtuman pvm:<br><table><tr><td><select name=year>";
($yearold,$mon,$mday)=split(/-/,$paiva);
for($yy=$year-50;$yy<$year+2;$yy++){
if($yearold == $yy){
print "<option value=$yy selected>$yy</option>\n";
}else{
print "<option value=$yy>$yy</option>\n";
}
}
print "</select></td><td><select name=month>";

for($mm=1;$mm<13;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mon == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td><td><select name=day>";

for($mm=1;$mm<32;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mday == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td></tr></table>";

$in{'notes'}=~s/<br>/\n/g;

print "<p>Notes (optional) - Lisätietoja (ei pakollinen):<br>
<textarea name=notes rows=7 cols=30>$notes</textarea>\n";

print "<p><input type=submit value=\"  Save changes   \" size=20> </form><p>";
}
}

}



################# gps point saver ##################
if($in{'act'} eq 'initgpslast'){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$out='';

open(HANDLE,">".$path."GPSLAST.txt");
close(HANDLE);


open(HANDLE,">".$path."GPS.txt");
close(HANDLE);

open(HANDLE,">".$path."GPS_ALL.txt");
close(HANDLE);

open(HANDLE,">".$path.'trackedrunners.txt');
close(HANDLE);
print "Done";
}

################# ##################
if($in{'act'} eq 'deltrackingcourses'){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$out='';

open(HANDLE,">".$path."radat_0.txt");
close(HANDLE);


open(HANDLE,">".$path."ratapisteet_0.txt");
close(HANDLE);

open(HANDLE,">".$path."sarjat_0.txt");
close(HANDLE);

print "Done";
}
####################################
if($in{'act'} eq 'convertgpslivetorgevent'){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$in{'eventtype'}=1*$in{'eventtype'};
if($in{'eventtype'} == 0){$in{'eventtype'}=1;}

$in{'eventname'}=~s/\|//g;
$in{'clubname'}=~s/\|//g;
$in{'notes'}=~s/\|//g;
$in{'notes'}=~s/\n/<br>/g;
$in{'notes'}=~s/\r//g;

$ser='&#39;';
$in{'eventname'}=~s/\'/${ser}/g;
$in{'clubname'}=~s/\'/${ser}/g;
$in{'notes'}=~s/\'/${ser}/g;
$ser='&quot;';
$in{'eventname'}=~s/\"/${ser}/g;
$in{'clubname'}=~s/\"/${ser}/g;
$in{'notes'}=~s/\"/${ser}/g;


open(HANDLE, "<".$path."kartat.txt");
&lock_file;
@data=<HANDLE>; 
&unlock_file;
close(HANDLE);
$map_uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$nimi)=split(/\|/,$rec,2);
if($map_uusid < $id){$map_uusid=$id;}
}
$map_uusid++;

open (HANDLE, "<".$path."0.jpg");
binmode HANDLE;
@data =<HANDLE>;
close(HANDLE); 
$d=join('',@data);          

open (HANDLE, ">".$path.$map_uusid.".jpg");
binmode HANDLE;
print HANDLE $d;
close (HANDLE);                   
if($chmod eq '1'){
system "chmod 755 ".$path.$map_uusid.".jpg";
}

open(HANDLE, ">>".$path."kartat.txt");
&lock_file;
print HANDLE "$map_uusid|".$in{'eventname'}."\n";     
&unlock_file;
close(HANDLE);

open(HANDLE, "<".$path."kisat.txt");
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec);
if($uusid < $id){$uusid=$id;}
}
$uusid ++;


open(HANDLE, ">>".$path."kisat.txt");
&lock_file;
print HANDLE "$uusid|$map_uusid|".$in{'eventtype'}."|".$in{'eventname'}."|".$in{'year'}.'-'.$in{'month'}.'-'.$in{'day'}."|".$in{'clubname'}."|".$in{'eventlevel'}."|".$in{'notes'}."\n";     
&unlock_file;
close(HANDLE);



open (HANDLE, "<".$path."sarjat_0.txt");
@data =<HANDLE>;
close(HANDLE); 
$d=join('',@data);          

open (HANDLE, ">".$path."sarjat_".$uusid.".txt");
print HANDLE $d;
close (HANDLE);         

open (HANDLE, "<".$path."radat_0.txt");
@data =<HANDLE>;
close(HANDLE); 
$d=join('',@data);          

open (HANDLE, ">".$path."radat_".$uusid.".txt");
print HANDLE $d;
close (HANDLE); 

open (HANDLE, "<".$path."ratapisteet_0.txt");
@data =<HANDLE>;
close(HANDLE); 
$d=join('',@data);          

open (HANDLE, ">".$path."ratapisteet_".$uusid.".txt");
print HANDLE $d;
close (HANDLE); 

## vielä kilpailijat.txt
open (HANDLE, "<".$path."coord.txt");
@d =<HANDLE>;
close(HANDLE); 
open (HANDLE, "<".$path."GPS.txt");
@gps =<HANDLE>;
close(HANDLE); 

$out='';
$i=0;
$kilp='';
$merkin='';

foreach $rec (@d){
$i++;
if($i>6){
@r=split(/\|/,$rec);

$prev='';
$prevtime='';
$hop=0;
$start=0;
$out='';
$out2='';


foreach $reca (@gps){
chomp($reca);
@g=split(/\,/,$reca);

if($g[1]==$r[0]){
if($prevtime eq ''){
$prevtime=$g[0]-3;
$start=1*$g[0];
}

while($prevtime< $g[0]-3 && $hop < 1000){
$hop++;
$prevtime=$prevtime+3;
$out.='-500;500,N';
$out2.='N-500;500';
}
$out.=''.$g[2].';'.$g[3].',N';

if($g[2] != $xprev && $g[3] != $yprev){ 
$out2.='N'.$g[2].';'.$g[3];
$xprev =$g[2];
$yprev= $g[3];
}
$xprev =$g[2];
$yprev= $g[3];

$pre=''.$g[2].';'.$g[3].',N';
$prevtime=$g[0];
}# if competitor

}#competitor
if($out ne ''){
$kilp.=''.(50000+$r[0]).'|1||'.$r[1].'|'.$start.'|||||'.$out."\n";
$merkin.='1|'.(50000+$r[0]).'|'.$r[1].'||'.$out2."\n";

}
} # not coord < 7
}#coords

open (HANDLE, ">".$path."kilpailijat_".$uusid.".txt");
print HANDLE $kilp;
close (HANDLE); 

open (HANDLE, ">".$path."merkinnat_".$uusid.".txt");
print HANDLE $merkin;
close (HANDLE); 

print "done";

}
####################################
if($in{'act'} eq 'gpslivetorgevent'){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

##
print "<form action=reittimanager.".$extension." method=post>     
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=convertgpslivetorgevent>";
print "<p><B>Event name - Tapahtuman nimi:</B><br><input type=text name=eventname sixe=50 value=''>";
print "<p><B>Club name - Seuran nimi:</B><br>";
if($clubnames_type eq 'field'){
print "<input type=text name=clubname size=50 value='$club_default'>";
}
if($clubnames_type eq 'list'){
open (SISAAN,"<".$path."clubnames.txt");
@data=<SISAAN>;
close(SISAAN);
@data=sort {$a <=> $b} @data;
print "<select name=clubname>";
print "<option value='Unclassified' selected>Select a Club Name below</option>";
foreach $rec (@data){ 
chomp($rec);
($cnindex,$clubname)=split(/\|/,$rec);
print "<option value='$clubname'>$clubname</option>\n";
}
print "</select><p>";
}
print "<p><B>Event date - Tapahtuman pvm:</B><br><table><tr><td><select name=year>";
for($yy=$year-50;$yy<$year+2;$yy++){
if($year == $yy){
print "<option value=$yy selected>$yy</option>\n";
}else{
print "<option value=$yy>$yy</option>\n";
}
}
print "</select></td><td><select name=month>";
for($mm=1;$mm<13;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mon == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td><td><select name=day>";

for($mm=1;$mm<32;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mday == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td></tr></table>";

print "<p><b>Event level</b><br>
<select name=eventlevel>
<option value=I>Ìåæäóíàðîäíûå</option>
<option value=N>Âñåðîññèéñêèå</option>
<option value=R selected>Îáëàñòíûå</option>
<option value=L>Ãîðîäñêèå</option>
<option value=T>Òðåíèðîâî÷íûå</option>
</select><p>";

print "Notes (optional) - Lisätietoja (ei pakollinen):<br>
<textarea name=notes rows=7 cols=30></textarea>\n<p>
<input type=checkbox value=2 name=eventtype> Allow route drawing manually (so those who ran but were not tracked can draw their routes)
<p>
<input type=submit value=\"  OK   \" size=20> </form>
";
}
###########################################
if($in{'act'} eq 'saveedittracking'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$out='';

$in{'coord'} =~ s/\r//g;
$in{'coord'} =~ s/\n\n/\n/g;
$in{'coord'} =~ s/\n\n/\n/g;
$in{'coord'} =~ s/^\n//;

@coord = split(/\n/,$in{'coord'});
$out=$coord[0]."\n".$coord[1]."\n".$coord[2]."\n".$coord[3]."\n".$coord[4]."\n".$coord[5]."\n";

for($i=1;$i<21;$i++){
$out.=$i.'|'.$in{'name_'.$i}.'|'.$in{'starth_'.$i}.'|'.$in{'startm_'.$i}.'|'.$in{'starts_'.$i}."\n";
}

open(HANDLE, ">".$path."coord.txt")|| die;
&lock_file;
print HANDLE $out;
&unlock_file;
close(HANDLE);

print "<i>Tracking data saved!</i><br>";
$in{'act'} = 'edittracking';
}
###########################################
if($in{'act'} eq 'edittracking'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

open(HANDLE, "<".$path."coord.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$coor=$data[0].$data[1].$data[2].$data[3].$data[4].$data[5];
$coor=~s/\r//g;

print "<form action=reittimanager.".$extension." method=post>     
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=saveedittracking>
<p>Coordinates::<br><textarea name=coord rows=6 cols=45>$coor</textarea><p>
Format:<br>
<br>Point1_Northing,Point1_Easting
<br>Point2_Northing,Point2_Easting
<br>Point3_Northing,Point3_Easting
<br>Point1_x,Point1_y
<br>Point2_x,Point2_y
<br>Point3_x,Point3_y
<br>Example:<pre>
60.26028657160827,24.83180522918701
60.26713546604338,24.853649139404297
60.251791313090166,24.862425327301025
42,626
499,296
727,959</pre><br>
Values are WGS84 degree coordinates and pixel coordinates from left top of map image.
<p>
Runners and start times (Start times are obsolete with this version): <br>
";

print "<table><tr><td>Nr</td>
<td>Name</td>
<td>hour</td>
<td>min</td>
<td>sec</td></tr>";

for($i=1;$i<21;$i++){
($id,$name,$starth,$startm,$starts)=split(/\|/,$data[5+$i]);
print "<tr><td><b>$i</b></td><td><input name=name_$i value=\"$name\"></td>
<td><input size=4 name=starth_$i value=\"$starth\"></td>
<td><input size=4 name=startm_$i value=\"$startm\"></td>
<td><input size=4 name=starts_$i value=\"$starts\"></td></tr>";
}
print "</table>";

print "<p><input type=submit value=\"  OK   \" size=20> </form><p>";
}
###########################################
if($in{'act'} eq 'uploadsplits'){  
$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

foreach $rec (@data){ 
	($idkilp,$map,$type,$name,$paiva,$seura,$taso)=split(/\|/,$rec);
if($idkilp eq $in{'kisaid'}){
$eventname=$paiva.' '.$name;
}
}

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<p><br><b>Update splits times for event:</b> <i>$eventname</i><br><br><b>Select SI CSV file:</b><p>";

print "<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'>  
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=kisaid value=$in{'kisaid'}>
<input type=hidden name=act value=updatesplits>";

print "<br><input type=file name=tulosxml>  \n";


print "<p><input type=submit value=\"  UPLOAD   \" size=20> </form><p>";
}




###########################################
if($in{'act'} eq 'updatesplits'){  
$in{'kisaid'}=1*$in{'kisaid'};


$q = $in{CGI};

&SISPLITS;

unlink $path."emitajat_$s.xml";


open(HANDLE, "<".$path."kilpailijat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$out='';
$ucount=0;
$ncount=0;

foreach $rec (@data){ 
	chomp($rec);
	($id,$sarjanro,$sarja,$nimi,$laika,$updateid,$sija,$tulos,$valiajat)=split(/\|/,$rec);

if($UPD_START{$updateid} ne ''){
$out.=''.$id.'|'.$sarjanro.'|'.$sarja.'|'.$nimi.'|'.(1*$UPD_START{$updateid}).'|'.$updateid.'|'.$sija.$UPD_SPLITS{$updateid}."\n";
$ucount++;
}else{
$out.=$rec."\n";
$ncount++;
}
}

open(HANDLE, ">".$path."kilpailijat_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $out;
&unlock_file;
close HANDLE;
## done

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<p>Updated:$ucount<br>Not updated $ncount<p><br>DONE!</b><p>";

}


###########################################
if($in{'act'} eq 'valitsejpg'){  
$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."kartat.txt")|| die;
@data=<HANDLE>;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<h3>Âûáèðèòå êàðòó äëÿ ðåäàêòèðîâàíèÿ:</h3>";
print "<form action=reittimanager.".$extension." method=post>     
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=jpgedit>";

foreach $rec (@data){ 
	($id,$nimi)=split(/\|/,$rec);
    print "<input type=radio class=radi name=jpgid value=$id>$nimi<br>";
}

print "<p><input type=submit value=\"  OK    \" size=20> </form><p>";
}
###########################################
if ($in{'act'} eq 'jpgedit') {
    require 'MapEditForm.pl';
}

######################################
if($in{'act'} eq 'savenewjpgmap'){  

open(HANDLE, "<".$path."kartat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);
$nid=0;
$ulos="";
foreach $rec (@data){ 
		($id,$nimi)=split(/\|/,$rec);
if($id>$nid){
$nid=$id;
}

}
$nid++;

open(HANDLE,"<".$path.'coord.txt');
@f=<HANDLE>;
close(HANDLE);

foreach $rec (@f){
chomp($rec);
}
($o1x,$o1y)=split(/\,/,$f[0]);
($o2x,$o2y)=split(/\,/,$f[1]);
($o3x,$o3y)=split(/\,/,$f[2]);
($s1x,$s1y)=split(/\,/,$f[3]);
($s2x,$s2y)=split(/\,/,$f[4]);
($s3x,$s3y)=split(/\,/,$f[5]);

  
$ulos=$nid.'|'.$in{'jpgname'}.'| |'.$s1x.'|'.$o1y.'|'.$s1y.'|'.$o1x.'|'.$s2x.'|'.$o2y.'|'.$s2y.'|'.$o2x.'|'.$s3x.'|'.$o3y.'|'.$s3y.'|'.$o3x."\n";


open(HANDLE, ">>".$path."kartat.txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;   

open(HANDLE, "<".$path.'0.jpg')|| die;
binmode HANDLE;
@d=<HANDLE>;
close(HANDLE);


open(HANDLE, ">".$path.$nid.'.jpg')|| die;
binmode HANDLE;
print HANDLE @d;
close(HANDLE);

print "<a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "Saved!";
}


######################################
if($in{'act'} eq 'regmaptotracking'){  

$in{'jpgid'}=floor(1*$in{'jpgid'});


open(HANDLE, "<".$path."coord.txt");
@coord=<HANDLE>;
close(HANDLE);

open(HANDLE, "<".$path."kartat.txt")|| die;
@data=<HANDLE>;
close(HANDLE);
$coord[0]='';
$coord[4]='';

foreach $rec (@data){ 
chomp($rec);
	($id,$nimi,$copyright,$x1,$e1,$y1,$n1,$x2,$e2,$y2,$n2,$x3,$e3,$y3,$n3)=split(/\|/,$rec);
if($id eq $in{'jpgid'}){

$coord[0]="$n1,$e1\n";
$coord[1]="$n2,$e2\n";
$coord[2]="$n3,$e3\n";
$coord[3]="$x1,$y1\n";
$coord[4]="$x2,$y2\n";
$coord[5]="$x3,$y3\n";
 $name= "$id,$nimi";
}
}

if($coord[0] ne '' && $coord[4] ne ''){
open(HANDLE, ">".$path."coord.txt");
print HANDLE @coord;
close(HANDLE);

open(HANDLE, "<".$path.$in{'jpgid'}.'.jpg')|| die;
binmode HANDLE;
@d=<HANDLE>;
close(HANDLE);


open(HANDLE, ">".$path.'0.jpg')|| die;
binmode HANDLE;
print HANDLE @d;
close(HANDLE);

print "$name ready for tracing!";
}else{

print "Georeference was not ok. Map was not set for tracking!";
}

}

######################################
if($in{'act'} eq 'savejpgedit'){  
    require 'MapEditSave.pl';
}

###########################################
if($in{'act'} eq 'valitsejpgpois'){  
$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."kartat.txt")|| die;
@data=<HANDLE>;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a> | <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

if($lang ne 'fi'){
print "<p><br><b>Delete a raster map:</b><p>";
}else{
print "<p><br><b>Poista kartta palvelimelta:</b><p>";
}
print "<form action=reittimanager.".$extension." method=post>     
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=poistajpg>";

foreach $rec (@data){ 
	($id,$nimi)=split(/\|/,$rec);
print "<br><input type=radio class=radi name=jpgpois value=$id>$nimi \n";
}

print "<p><input type=submit value=\"  Delete    \" size=20> </form><p>";
}
######################################
if($in{'act'} eq 'poistajpg'){  
    require 'MapDelete.pl';
}

##########################################################
if($in{'act'} eq 'poistapiirros' && $in{'kisaid'} ne ''){  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";

## tarkistetaan kisan moodi
open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

foreach $rec (@data){ 
	($idkilp,$map,$type,$name,$paiva,$seura,$taso)=split(/\|/,$rec);
if($idkilp eq $in{'kisaid'}){
$eventtype=$type;
}
}

$in{'kisaid'}=1*$in{'kisaid'};
open(HANDLE, "<".$path."merkinnat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
if($id eq $in{'piirrospois'}){
 ## ei printata takaisin
 print "<html>Route $id  $nimi is deleted. / Reittipiirros $id $nimi on poistettu.<p>";
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."merkinnat_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;                          

######################################3
## poistettu reittipiirros, kommentit vielä jäi:
open(HANDLE, "<".$path."kommentit_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
	($idkilp,$id,$nimi,$aika,$kommentit)=split(/\|/,$rec);
if($id eq $in{'piirrospois'}){
 ## ei printata takaisin
 print "<html>Comment $id  $nimi deleted / poistettu<p>";
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."kommentit_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;

if($eventtype==2 || $in{'piirrospois'}> 50000){ ## jos piirtäjän nimi on kysytty tai gps

######################################3
## poistettu reittipiirros, kommentit vielä jäi:
open(HANDLE, "<".$path."kilpailijat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
	($id,$sarj,$sarjnimi,$nimi)=split(/\|/,$rec);
if($id eq $in{'piirrospois'}){
 ## ei printata takaisin
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."kilpailijat_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;
}

print "<p><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
exit;
}


if($in{'act'} eq 'valitsepiirrospois'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";

$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."merkinnat_".$in{'kisaid'}.".txt")|| die;
@data=<HANDLE>;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4> <a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
if($lang ne 'fi'){
print "<p><br><b>Delete a route drawing:</b><p>";
}else{
print "<p><br><b>Valitse poistettava reittipiirros:</b><p>";
}
print "<form action=reittimanager.".$extension." method=post>       
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=poistapiirros>
<input type=hidden name=kisaid value=$in{'kisaid'}>";

foreach $rec (@data){ 
	($idkilp,$id,$nimi,$aika,$viivat,$rastit)=split(/\|/,$rec);
print "<br><input type=radio class=radi name=piirrospois value=$id>$nimi\n";
}
##################################
print "<p><input type=submit value=\"   Delete    \" size=20> </form><p>";
}     

##########################################################
if($in{'act'} eq 'poistarata' && $in{'kisaid'} ne ''){  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";

$in{'kisaid'}=1*$in{'kisaid'};
open(HANDLE, "<".$path."sarjat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
	($id,$nimi)=split(/\|/,$rec);
if($id eq $in{'ratapois'}){
 ## ei printata takaisin
 print "<html>Class / course $id  $nimi is deleted. - Sarja/rata $id $nimi on poistettu.<p>";
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."sarjat_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $ulos;
close HANDLE;                          
&unlock_file;

open(HANDLE, "<".$path."radat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
close(HANDLE);
&unlock_file;   

$ulos="";
foreach $rec (@data){ 
	($id,$nimi)=split(/\|/,$rec);
if($id eq $in{'ratapois'}){
 ## ei printata takaisin
}else{
$ulos=$ulos.$rec;
}
}


open(HANDLE, ">".$path."radat_".$in{'kisaid'}.".txt");
print HANDLE $ulos;
close HANDLE;   


## piirrokset
open(HANDLE, "<".$path."merkinnat_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
close(HANDLE);
&unlock_file;
$ulos="";
foreach $rec (@data){ 
	($sarjaid,$nimi)=split(/\|/,$rec);
if($sarjaid eq $in{'ratapois'}){
 ## ei printata takaisin
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."merkinnat_".$in{'kisaid'}.".txt");
print HANDLE $ulos;
close(HANDLE);

## kommentit
open(HANDLE, "<".$path."kommentit_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);
$ulos="";
foreach $rec (@data){ 
	($sarjaid,$nimi)=split(/\|/,$rec);
if($sarjaid eq $in{'ratapois'}){
 ## ei printata takaisin
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."kommentit_".$in{'kisaid'}.".txt");
print HANDLE $ulos;
close(HANDLE);
print "<p><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
exit;
}

###################################
if($in{'act'} eq 'valitseratapois'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML><head><STYLE>";
&tyyli;
print "</STYLE></head><BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";

$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."sarjat_".$in{'kisaid'}.".txt")|| die;
@data=<HANDLE>;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML><head><STYLE>";
&tyyli;
print "</STYLE></head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4> <a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
if($lang ne 'fi'){
print "<p><br><b>Delete a class/course:</b><p>";
}else{
print "<p><br><b>Valitse poistettava rata/sarja:</b><p>";
}
print "<form action=reittimanager.".$extension." method=post>       
<input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=poistarata>
<input type=hidden name=kisaid value=$in{'kisaid'}>";

foreach $rec (@data){ 
	($id,$nimi)=split(/\|/,$rec);
print "<br><input type=radio class=radi name=ratapois value=$id>$nimi\n";
}

print "<p><input type=submit value=\"   Delete    \" size=20> </form><p>";
}

##########################3
if ($in{'act'} eq 'manager' || $in{'act'} eq '') {
    require 'Main.pl';
}      
###################### tallennusonnistui-sivu #################
if ($in{"act"} eq "lisaaratoja"){
open(SISAAN, "<".$path."kisat.txt");
@data=<SISAAN>;
close(SISAAN);           
print "<HTML>
<HEAD>
<TITLE>OK</TITLE>
<STYLE>";
&tyyli;
print "</STYLE>
</HEAD>

<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>
<b>Draw new courses, select event - Uusien ratojen piirto, valitse tapahtuma:</b><ul>";
foreach $rec (@data){ 
	chomp($rec);
chomp($rec);

($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso)=split(/\|/,$rec,7);
if($tyyppi == 2){
print "<li><a href=../reitti.".$extension."?piirrarastit=1&id=$id&eventtype=$tyyppi&act=map&keksi=$in{'keksi'}>$nimi _ Draw new courses - Piirrä uusia ratoja</a>";
}
}
print "</ul>";

}

###################### tallennusonnistui-sivu #################
if ($in{"act"} eq "tallennettu"){

print "<HTML><HEAD><TITLE>OK</TITLE><STYLE>";
&tyyli;
print "</STYLE></HEAD>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>

<center><br><br><br><br><br><br><br>
Course is saved! Go <a href='javascript:history.back()'>back and draw next course.</a>
<p>
Rata on tallennettu! <a href='javascript:history.back()'>Palaa takaisin piirtämään seuraava rata.</a>
</center>
</BODY>
</HTML>";
exit;
}

####################################################
if ($in{"act"} eq "calibsave"){

if($in{"karttaid"} == 0){
open(HANDLE, "<".$path."coord.txt");
@coord=<HANDLE>;
close(HANDLE);

	($x1,$y1,$x2,$y2,$x3,$y3,)=split(/\,/,$in{'coord2'});
	($e1,$n1,$e2,$n2,$e3,$n3,)=split(/\,/,$in{'coord1'});
$y1=-1*$y1;
$y2=-1*$y2;
$y3=-1*$y3;
$coord[0]="$n1,$e1\n";
$coord[1]="$n2,$e2\n";
$coord[2]="$n3,$e3\n";
$coord[3]="$x1,$y1\n";
$coord[4]="$x2,$y2\n";
$coord[5]="$x3,$y3\n";

open(HANDLE, ">".$path."coord.txt");
print HANDLE @coord;
close(HANDLE);

print " Saved! <p> <a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
exit;
}else{

	($x1,$y1,$x2,$y2,$x3,$y3,)=split(/\,/,$in{'coord2'});
	($e1,$n1,$e2,$n2,$e3,$n3,)=split(/\,/,$in{'coord1'});
$y1=-1*$y1;
$y2=-1*$y2;
$y3=-1*$y3;
$uloscoord=''.$x1.'|'.$e1.'|'.$y1.'|'.$n1.'|'.$x2.'|'.$e2.'|'.$y2.'|'.$n2.'|'.$x3.'|'.$e3.'|'.$y3.'|'.$n3;


open(HANDLE, "<".$path."kartat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
chomp($rec);
		($id,$nimi,$cp,$coord)=split(/\|/,$rec);
if($id eq $in{'karttaid'}){
 ## printataan takaisin uudet tiedot
  
$ulos=$ulos.$id.'|'.$nimi.'|'.$cp.'|'.$uloscoord."\n";

}else{
$ulos=$ulos.$rec."\n";
}
}

open(HANDLE, ">".$path."kartat.txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;   


print " Saved! <p> <a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
exit;

}

}

####################################################
if ($in{"act"} eq "vastinpistesave"){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
open (ULOS,">$path"."gpsvastinpisteet_$in{'id'}.txt");
print ULOS "".(1*$in{'o1x'}).'|'.(1*$in{'o1y'}).'|'.(1*$in{'o2x'}).'|'.(1*$in{'o2y'}).'|'.(1*$in{'o3x'}).'|'.(1*$in{'o3y'}).'|'.(1*$in{'s1x'}).'|'.(1*$in{'s1y'}).'|'.(1*$in{'s2x'}).'|'.(1*$in{'s2y'}).'|'.(1*$in{'s3x'}).'|'.(1*$in{'s3y'});
close ULOS;
print "Vastinpisteet on tallennettu tapahtumall ID: $in{'id'}<p> <a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manageriin</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
exit;
}
####################################################
if ($in{"act"} eq "vastinpisteedit"){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
print "<hr><b>Muokkaa gps sovitusta </b><p>Vastinpistepareissa on ensin gps koordinaatit, sitten vastaavan
pisteen pikselikoordinaatit gif / jpg -kuvassa. Voit poimia pikselikoordinaatit jollakin kuvaeditorilla. Pikselikoordinaatit kasvavat oikealle ja alas, GPS -koordinaatit kasvavat oikealle ja ylös. ";
print "<p><form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=vastinpistesave>
<input type=hidden name=id value=$in{'id'}>\n";               

open (SISAAN,"<$path"."gpsvastinpisteet_$in{'id'}.txt");
@d=<SISAAN>;
close(SISAAN);

$d=join('',@d);
$d =~ s/ //g;
$d =~ s/\n//g;
$d =~ s/\r//g;
## 3 pistetta ja niiden vastinpisteet
($o1x,$o1y,$o2x,$o2y,$o3x,$o3y,$s1x,$s1y,$s2x,$s2y,$s3x,$s3y)=split(/\|/,$d);

print "<table>";
print "<tr><td>Nro</td><td>GPS_itä</td><td>GPS_pohjoinen</td><td>Rasterikuva_vasenmmalle</td><td>Rasterikuva_alas</td><td></td>\n";
print "<tr><td>1.</td><td><input type=text name=o1x value=\"$o1x\"></td><td><input type=text name=o1y value=\"$o1y\"></td><td><input type=text name=s1x value=\"$s1x\"></td><td><input type=text name=s1y value=\"$s1y\"></td></tr>\n";
print "<tr><td>2.</td><td><input type=text name=o2x value=\"$o2x\"></td><td><input type=text name=o2y value=\"$o2y\"></td><td><input type=text name=s2x value=\"$s2x\"></td><td><input type=text name=s2y value=\"$s2y\"></td></tr>\n";
print "<tr><td>3.</td><td><input type=text name=o3x value=\"$o3x\"></td><td><input type=text name=o3y value=\"$o3y\"></td><td><input type=text name=s3x value=\"$s3x\"></td><td><input type=text name=s3y value=\"$s3y\"></td></tr>\n";
print "</table><input type=submit value=\"  Tallenna   \" size=20> </form><p><hr>";
}
###########################################
if($in{'act'} eq 'valitsegpspois'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
$in{'kisaid'}=1*$in{'kisaid'};

open(HANDLE, "<".$path."gps_".$in{'kisaid'}.".txt")|| die;
@data=<HANDLE>;
close(HANDLE);

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<p><br><b>Valitse poistettava GPS -tallenne:</b><p>
<form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=poistagps>
<input type=hidden name=kisaid value=$in{'kisaid'}>";

foreach $rec (@data){ 
	($id,$date,$datum,$nimi,$loput,$rastit)=split(/\|/,$rec);
print "<br><input type=radio class=radi name=gpspois value=$id>$nimi $date datum\n";
}

print "<p><input type=submit value=\"   OK    \" size=20> </form><p>";
}
######################################
if($in{'act'} eq 'poistagps' && $in{'kisaid'} ne ''){ 
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";
 
$in{'kisaid'}=1*$in{'kisaid'};
open(HANDLE, "<".$path."gps_".$in{'kisaid'}.".txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$ulos="";
foreach $rec (@data){ 
	($id,$date,$datum,$nimi,$loput,$rastit)=split(/\|/,$rec);
if($id eq $in{'gpspois'}){
 ## ei printata takaisin
 print "<html>Poistettu GPS $id  $nimi<p>";
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."gps_".$in{'kisaid'}.".txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;       
print "<a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
}
###########################################
if($in{'act'} eq 'valitsetapahtumalataus'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<p><br><b>Select event type - Valitse tapahtuman tyyppi:</b><p>
<br><a href=reittimanager.".$extension."?act=tapahtumalataus&type=1&keksi=$in{'keksi'}>Normal individual evet - Tavallinen henkilökohtainen kilpailu</a>
<br><br><a href=reittimanager.".$extension."?act=tapahtumalataus&type=2&keksi=$in{'keksi'}>Individual event without split times - Henkilökohtainen, jossa kysytään nimet ja väliajat </a>
<br><br><a href=reittimanager.".$extension."?act=tapahtumalataus&type=3&keksi=$in{'keksi'}>Relay - Viesti</a>
</htrml>
";

}

###########################################
if(($in{'act'} eq 'configclubnames')&&($allow_clubname_edit=='1')){ 
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0 marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "<p><br>To add a new Club Name to the dropdown list, enter a numeric Order Index and Club Name in the first row below.<br>";
print "Edit each Order Index and Club Name in the existing list if required.<br>";
print "Items in the Club Name list will always display in <b>ascending order</b> of the Order Index.<br>";
print "To Delete a name from the list, <b>clear both fields</b> before saving.<br><p>";
print "Then click <b>SAVE</b> to save the list.<br>";
print "<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}>
<input type=hidden name=act value=saveclubnames>";
$id=0;
print "<b>Add New Club Name:</b><p>";
print "Order Index: <input type=text name=cnid$id size=3 value=''> ";
print "Club Name: <input type=text name=clubname$id size=50 value=''><p>";
$id++;
print "<b>Existing Club Names List:</b><p>";
open (SISAAN,"<".$path."clubnames.txt");
@data=<SISAAN>;
close(SISAAN);
@data=sort {$a <=> $b} @data;
foreach $rec (@data){ 
chomp($rec);
($cnid,$clubname)=split(/\|/,$rec);
print "Order Index: <input type=text name=cnid$id size=3 value=\"$cnid\"> ";
print "Club Name: <input type=text name=clubname$id size=50 value=\"$clubname\"><br>";
$id++;
}
if($id==1){
print "Club Names List is empty!";
}
print "<input type=hidden name=\"lastid\" value=\"$id\">";
print "<p><input type=submit value=\" SAVE \" size=20> </form><p>";
}
###########################################
if(($in{'act'} eq 'saveclubnames')&&($allow_clubname_edit=='1')){ 
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0 marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "Writing Club Names data to file clubnames.txt...<p>";
@data=();
for($id=0;$id<$in{'lastid'};$id++){
if(length $in{'cnid'.$id}.$in{'clubname'.$id}){
push(@data,$in{'cnid'.$id}.'|'.$in{'clubname'.$id}."\n");
}
}
@data=sort {$a <=> $b} @data;
open(HANDLE, ">".$path."clubnames.txt");
&lock_file;
print HANDLE @data;
&unlock_file;
close(HANDLE);
print "<b>Success - File clubnames.txt has been saved!</b><p>";
print "<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}>";
print "<p><input type=submit value=\" OK \" size=20> </form><p>";
}
###########################################
if($in{'act'} eq 'tapahtumalataus'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }

H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}>";

print "<p>Event name:<br><input type=text name=eventname size=50 value=''>";
print "<p>Club name:<br>";
if($clubnames_type eq 'field'){
print "<input type=text name=clubname size=50 value='$club_default'>";
}
if($clubnames_type eq 'list'){
open (SISAAN,"<".$path."clubnames.txt");
@data=<SISAAN>;
close(SISAAN);
@data=sort {$a <=> $b} @data;
print "<select name=clubname>";
print "<option value='Unclassified' selected>Select a Club Name below</option>";
foreach $rec (@data){ 
chomp($rec);
($sortid,$clubname)=split(/\|/,$rec);
print "<option value='$clubname'>$clubname</option>\n";
}
print "</select><p>";
}
print "<p>Event date - Tapahtuman pvm:<br><table><tr><td><select name=year>";

for($yy=$year-50;$yy<$year+2;$yy++){
if($year == $yy){
print "<option value=$yy selected>$yy</option>\n";
}else{
print "<option value=$yy>$yy</option>\n";
}
}
print "</select></td><td><select name=month>";

for($mm=1;$mm<13;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mon == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td><td><select name=day>";

for($mm=1;$mm<32;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mday == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td></tr></table>";


print "<br>Event level<br>
<select name=eventlevel>
<option value=I>Ìåæäóíàðîäíûå</option>
<option value=N>Âñåðîññèéñêèå</option>
<option value=R selected>Îáëàñòíûå</option>
<option value=L>Ãîðîäñêèå</option>
<option value=T>Òðåíèðîâî÷íûå</option>
</select><p>";

print "Notes (optional) - Lisätietoja (ei pakollinen):<br>
<textarea name=notes rows=7 cols=30></textarea>\n";

print "<p>Select map image (gif or jpg)<br><input type=file name=karttakuva>";
print "<p>kilpailijat_XXX.txt<br><input type=file name=kilpailijat>";
print "<p>sarjat_XXX.txt<br><input type=file name=sarjat>";
print "<p>ratapisteet_XXX.txt<br><input type=file name=ratapisteet>";
print "<p>radat_XXX.txt<br><input type=file name=radat>";
print "<p>merkinnat_XXX.txt<br><input type=file name=merkinnat>";
print "<p>kommentit_XXX.txt<br><input type=file name=kommentit>";
print "<input type=hidden name=eventtype value=\"$in{'type'}\">";
print "<input type=hidden name=act value=\"lataatapahtuma\">";
print "<p><input type=submit value=\"   OK    \" size=20> </form><p>";
}


###########################################
if ($in{"act"} eq "uploadgpsmap"){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title><style>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$q = $in{CGI};
$map_uusid=0;

$file = $q->param("karttakuva");
binmode $file;
@data =<$file>;
close($file); 
$d=join('',@data);          

open (HANDLE, ">".$path.$map_uusid.".jpg");
binmode HANDLE;
print HANDLE $d;
close (HANDLE);                   
if($chmod eq '1'){
system "chmod 755 ".$path.$map_uusid.".jpg";
}

print "Image saved!";
}
###########################################
if ($in{"act"} eq "lataatapahtuma"){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title><style>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$q = $in{CGI};

open(HANDLE, "<".$path."kartat.txt");
&lock_file;
@data=<HANDLE>; 
&unlock_file;
close(HANDLE);
$map_uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$nimi)=split(/\|/,$rec,2);
if($map_uusid < $id){$map_uusid=$id;}
}
$map_uusid++;

$file = $q->param("karttakuva");
binmode $file;
@data =<$file>;
close($file); 
$d=join('',@data);          

open (HANDLE, ">".$path.$map_uusid.".jpg");
binmode HANDLE;
print HANDLE $d;
close (HANDLE);                   
if($chmod eq '1'){
system "chmod 755 ".$path.$map_uusid.".jpg";
}

open(HANDLE, ">>".$path."kartat.txt");
&lock_file;
print HANDLE "$map_uusid|".$in{'eventname'}."\n";     
&unlock_file;
close(HANDLE);


open(HANDLE, "<".$path."kisat.txt");
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$karttaid,$tyyppi,$nimi,$paiva,$seura,$taso,$notes)=split(/\|/,$rec);
if($uusid < $id){$uusid=$id;}
}
$uusid ++;

$in{'eventname'}=~s/\|//g;
$in{'clubname'}=~s/\|//g;
$in{'notes'}=~s/\|//g;
$in{'notes'}=~s/\n/<br>/g;
$in{'notes'}=~s/\r//g;

$ser='&#39;';
$in{'eventname'}=~s/\'/${ser}/g;
$in{'clubname'}=~s/\'/${ser}/g;
$in{'notes'}=~s/\'/${ser}/g;
$ser='&quot;';
$in{'eventname'}=~s/\"/${ser}/g;
$in{'clubname'}=~s/\"/${ser}/g;
$in{'notes'}=~s/\"/${ser}/g;

open(HANDLE, ">>".$path."kisat.txt");
&lock_file;
print HANDLE "$uusid|$map_uusid|".$in{'eventtype'}."|".$in{'eventname'}."|".$in{'year'}.'-'.$in{'month'}.'-'.$in{'day'}."|".$in{'clubname'}."|".$in{'eventlevel'}."|".$in{'notes'}."\n";     
&unlock_file;
close(HANDLE);

$file = $q->param("kilpailijat");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;
open (HANDLE, ">".$path.'kilpailijat_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);                   

$file = $q->param("sarjat");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;
open (HANDLE, ">".$path.'sarjat_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);             

$file = $q->param("ratapisteet");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;
open (HANDLE, ">".$path.'ratapisteet_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);      

$file = $q->param("radat");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;
open (HANDLE, ">".$path.'radat_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);   

$file = $q->param("merkinnat");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;
open (HANDLE, ">".$path.'merkinnat_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);  

$file = $q->param("kommentit");
@data =<$file>;
close($file); 
$d=join('',@data);          
$d=~s/\r//g;

open (HANDLE, ">".$path.'kommentit_'.$uusid.".txt");
print HANDLE $d;
close (HANDLE);  
print "Event loaded - Tapahtuma on ladattu";

}



################# tallenna sovitus ja yhdistä sarjat-radat ####################
if ($in{"act"} eq "tallennasovitus"){
if($in{'eventtype'} != 3 && $in{'eventtype'} != 4){
## ei tallenne talteen, kierrätätään tiedot formissa
#open (HANDLE,">$path"."sovitus.txt");
#print HANDLE $in{'skaalaus'}."|".$in{'siirtox'}."|".$in{'siirtoy'}."\n";
#close(HANDLE); 

# lue sarjat
open (SISAAN,"<$path"."sarjakanta_$in{'eventid'}.txt");
@sarjat=<SISAAN>;
close(SISAAN);
# lue radat
open (SISAAN,"<$path"."ratakanta_$in{'eventid'}.txt");
@radat=<SISAAN>;
close(SISAAN);  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";


print "<form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}>";

print "<p><b>Óêàæèòå äèñòàíöèè äëÿ ãðóïï:</b>

<input type=hidden name=act value=reititradat>
<input type=hidden name=sovitus value=$in{'sovitus'}>
<input type=hidden name=eventid value=$in{'eventid'}>
<input type=hidden name=skaalaus value=$in{'skaalaus'}>
<input type=hidden name=siirtox value=$in{'siirtox'}>
<input type=hidden name=siirtoy value=$in{'siirtoy'}>
<input type=hidden name=calibration value=\"$in{'calibration'}\">
<table>";
foreach $rec(@sarjat){
chomp($rec);
($sarjaid,$sarjanimi)=split(/\|/,$rec);
print "<tr><td>$sarjanimi</td><td><select name=\"sarja_".$sarjaid."\">\n"; 
print "<option value=pois>Ïðîïóñòèòü ýòó ãðóïïó\n";
foreach $rec2 (@radat){
chomp($rec2);
($aa,$bb)=split(/\|/,$rec2);
@snimet1=split(/ /,$bb);
@snimet2=split(/\,/,$bb);
$select="";
foreach $rec3(@snimet1){
$rec3=~s/\,//ig;
if($rec3 eq $sarjanimi){
$select=" selected";
}
}
foreach $rec3(@snimet2){
$rec3=~s/ //ig;
if($rec3 eq $sarjanimi){
$select=" selected";
}
}
print "<option value=\"".$aa."_".$bb."\"$select>$aa $bb\n";
}
print "</select></td></tr>";
}      
print"</table>\n";
print "<br><input type=submit value=\" OK \"></form>";

}else{ ############ relay
################# tallenna sovitus ja yhhdistä sarjat-radat ####################
## ei tallenne talteen, kierrätätään tiedot formissa
#open (HANDLE,">$path"."sovitus.txt");
#print HANDLE $in{'skaalaus'}."|".$in{'siirtox'}."|".$in{'siirtoy'}."\n";
#close(HANDLE); 

# lue sarjat
open (SISAAN,"<$path"."sarjakanta_$in{'eventid'}.txt");
@sarjat=<SISAAN>;
close(SISAAN);
# lue radat
open (SISAAN,"<$path"."ratakanta_$in{'eventid'}.txt");
@radat=<SISAAN>;
close(SISAAN);  
# lue hajonnat
open (SISAAN,"<$path"."hajontakanta_$in{'eventid'}.txt");
@hajonnat=<SISAAN>;
close(SISAAN);
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

print "<form action=reittimanager.".$extension." method=post>";

if($in{'eventtype'} == 4){
print "<p><b>Select start and finish points - Valitse lähdön ja maalin koodi:</b>";
open (SISAAN,"<$path"."rastikanta_$in{'eventid'}.txt");
@rastit=<SISAAN>;
close(SISAAN);

print "<p><b>Start - Lähtö</b><br><select name=startcode>";

foreach $rec(@rastit){
chomp($rec);
($koodi,$x,$y)=split(/\|/,$rec);
print "<option value=\"$koodi\">$koodi</option>\n";
}
print "</select>";
print "<p><b>Finish - Maali</b><br><select name=finishcode>";

foreach $rec(@rastit){
chomp($rec);
($koodi,$x,$y)=split(/\|/,$rec);
print "<option value=\"$koodi\">$koodi</option>\n";
}
print "</select><input type=hidden name=eventtype value=$in{'eventtype'}>";

open (SISAAN,"<$path"."sarjakanta_$in{'eventid'}.txt");
@sarjat=<SISAAN>;
close(SISAAN); 

print "<br><br><b>Publish these courses - Ota nämä sarjat mukaan:</b><br>";

foreach $sr (@sarjat){
chomp($sr);
($id, $nimi)=split(/\|/,$sr);
print "<br><input type=checkbox name=\"class_".$id."\" value=1 checked>($id) $nimi\n";
}
}


print "<p><b>Check courses - Tarkista hajonnat:</b>";

print "
<input type=hidden name=act value=reititradatviesti>
<input type=hidden name=eventid value=$in{'eventid'}>
<input type=hidden name=skaalaus value=$in{'skaalaus'}>
<input type=hidden name=siirtox value=$in{'siirtox'}>
<input type=hidden name=siirtoy value=$in{'siirtoy'}>
<input type=hidden name=keksi value=$in{'keksi'}> 
<input type=hidden name=calibration value=\"$in{'calibration'}\">
<table>";
foreach $rec(@hajonnat){
chomp($rec);
($sarjaid,$sarjanimi,$codes)=split(/\|/,$rec);
print "<tr><td>$sarjanimi</td><td><input type=hidden name=\"sarja2_".$sarjaid."\" value=\"$sarjanimi\"><select name=\"sarja_".$sarjaid."\">\n"; 
print "<option value=pois>Select course\n";

$codes=~ s/<cc>//g;
$codes=~ s/<\/cc>//g;
$codes =~ s/^_+//;
$codes =~ s/_+$//;

$loytyi=0;$pituus=0;
foreach $rec2 (@radat){
chomp($rec2);
($aa,$bb,$cc,$dd,$rcodes)=split(/\|/,$rec2,5);
$rcodes=~ s/\|/\_/g;
$rcodes=~ s/<cc>//g;
$rcodes=~ s/<\/cc>//g;
$rcodes =~ s/^_+//;
$rcodes =~ s/_+$//;

$select="";


# index($bb,$sarjanimi)>0 
if(index($codes,$rcodes) >-1){
$select=" selected";
if($pituus>length($rcodes)){
$select="";
}else{
$pituus=length($rcodes);
}
$loytyi=1;
print "<option value=\"".$aa."_".$bb."\"$select>$aa $bb\n";
}
}
if($loytyi==0){# ei löytynyt

foreach $rec2 (@radat){
chomp($rec2);
($aa,$bb,$cc,$dd,$rcodes)=split(/\|/,$rec2,5);

$select="";


# index($bb,$sarjanimi)>0 
if( index($bb.'_'.$aa,$sarjanimi)>-1 ||index($sarjanimi,$aa)>-1 && $aa ne '' || index($sarjanimi,$bb)>-1 && $bb ne '' ){
$select=" selected";
}
print "<option value=\"".$aa."_".$bb."\"$select>$aa $bb $select\n";


}

}
print "</select></td></tr>";

}      
print"</table>\n";
print "<br><input type=submit value=\" Valmis \"></form>";
}
}

##### sarjat radat#############################
if ($in{"act"} eq "reititradat"){ 

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";


#if ($in{"psw"} ne $password){ ## salasana ei ole käytössä, suojaus htaccessilla
# print "Annoit väärän salasanan. Tietoja ei tallennettu. <p>Palaa edelliselle sivulle ja anna oikea salasana";
#exit;
#}
$pii = 3.14159265; 
open (SISAAN,"<$path"."sarjakanta_$in{'eventid'}.txt");
@sarjat=<SISAAN>;
close(SISAAN);
# lue radat
open (SISAAN,"<$path"."ratakanta_$in{'eventid'}.txt");
@radat=<SISAAN>;
close(SISAAN); 

## perataan rastit
open (SISAAN,"<$path"."rastikanta_$in{'eventid'}.txt");
@rastit=<SISAAN>;
close(SISAAN);

$pi= 3.14159265; 
if($in{'calibration'} ne ''){
($x1,$y1,$x2,$y2,$ox1,$oy1,$ox2,$oy2)=split(/\,/,$in{'calibration'});


          $pit1=sqrt(($ox1-$ox2)*($ox1-$ox2)+($oy1-$oy2)*($oy1-$oy2));
		   $pit2=sqrt(($x1-$x2)*($x1-$x2)+($y1-$y2)*($y1-$y2));

           $gk1=0;
           $gk2=0;
           $gk3=0;


           if ($x2==$x1){

              if ($y2>$y1){
                 $gk1=$pi/2;
              }else{
                 $gk1=-$pi/2;
				 }

           }else{


              if ($x2<$x1){
                 $gk1=atan(($y2-$y1)/($x2-$x1))+$pi;
               
              }else{
                $gk1=atan(($y2-$y1)/($x2-$x1));
                 }
		    }
			
           if ($ox2==$ox1){

              if ($oy2>$oy1){
                 $gk2=$pi/2;
              }else{
                 $gk2=-$pi/2;
				 }

           }else{

              if ($ox2<$ox1){
                 $gk2=atan(($oy2-$oy1)/($ox2-$ox1))+$pi;
               
              }else{
                $gk2=atan(($oy2-$oy1)/($ox2-$ox1));
                 }
		    }
		}



foreach $rec(@rastit){
chomp($rec);
($koodi,$x,$y)=split(/\|/,$rec);
if($in{'calibration'} eq ''){
if($in{'sovitus'} ne "off"){
$rastix{$koodi}=floor(10*$x*$in{'skaalaus'}+$in{'siirtox'});
$rastiy{$koodi}=floor(10*$y*$in{'skaalaus'}+$in{'siirtoy'});
}else{
$rastix{$koodi}=floor(1*$x);
$rastiy{$koodi}=floor(1*$y);
}
}else{
# new js calibration with rotation

 $ox3=1*$x*10;
 $oy3=-1*$y*10;
		
	$pit3=sqrt(($ox1-$ox3)*($ox1-$ox3)+($oy1-$oy3)*($oy1-$oy3));
	           if ($ox3==$ox1){

              if ($oy3>$oy1){
                 $gk3=$pi/2;
              }else{
                 $gk3=-$pi/2;
				 }

           }else{

              if ($ox3<$ox1){
                 $gk3=atan(($oy3-$oy1)/($ox3-$ox1))+$pi;
               
              }else{
                $gk3=atan(($oy3-$oy1)/($ox3-$ox1));
                 }
		    }
	
$rastix{$koodi}=floor(0.5+(1*$x1 +(cos($gk3-$gk2+$gk1)*$pit3*$pit2/$pit1)));
$rastiy{$koodi}=-floor(0.5+(1*$y1 +(sin($gk3-$gk2+$gk1)*$pit3*$pit2/$pit1)));
}
}
open (HANDLE1,">$path"."sarjat_$in{'eventid'}.txt");
open (HANDLE2,">$path"."radat_$in{'eventid'}.txt");   
open (HANDLE3,">$path"."ratapisteet_$in{'eventid'}.txt"); 
foreach $rec(@sarjat){
chomp($rec);
($sarjaid,$sarjanimi)=split(/\|/,$rec);
if($in{'sarja_'.$sarjaid} ne "pois" && $in{'sarja_'.$sarjaid} ne ""){
print HANDLE1 "$rec\n";
foreach $rec2 (@radat){
chomp($rec2);
($aa,$bb,$lahto,$maali,$loput)=split(/\|/,$rec2,5);
@ratarastit=split(/\|/,$loput);
if($in{'sarja_'.$sarjaid} eq $aa."_".$bb){
print HANDLE2 "$sarjaid|1|$sarjanimi|";
#print HANDLE2 "2;".$rastix{$lahto}.";".$rastiy{$lahto}.";0;0N";
print HANDLE2 "2;".$rastix{$maali}.";".$rastiy{$maali}.";0;0N"; 

if($rastix{$lahto}eq'' ||$rastiy{$lahto} eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$lahto</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}

$ratapisteet="$sarjaid|".$rastix{$lahto}.";".$rastiy{$lahto}."N";
$x=$rastix{$lahto};$y=$rastiy{$lahto}; 
$i=0;$kulma=9999;
foreach $rec3 (@ratarastit){

if($rastix{$rec3}eq'' ||$rastiy{$rec3} eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$rec3</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}

$kulma2=$kulma;
$kulma=atan(($rastiy{$rec3}-$y)/($rastix{$rec3}-$x+0.0000001));

$xsiirto=20*cos($kulma);
$ysiirto=20*sin($kulma);
$suunta=0;
if($rastix{$rec3}<$x){
$xsiirto=-$xsiirto;
$ysiirto=-$ysiirto; 
$suunta=-1;
}
if($kulma2 != 9999){
if($kulma<0){
#$kulma=$kulma+2*$pii;
}
if($kulma>2*$pii){
#$kulma=$kulma-2*$pii;
}
$k=($kulma2+$kulma)/2;

if($edellinensuunta==$suunta){
$k=$k-$pii/2;
} 
$apukulma=$kulma;
if($suunta==-1)    {
$apukulma=$apukulma+$pii;
}

if(abs($apukulma-$k)<$pii/2 || abs($apukulma-$k)>$pii+$pii/2){
$k=$k+$pii;  #print "<br>XXX";
}else{
#print "<br>---";
}
}
$edellinensuunta=$suunta; 

if($i==0){
$lahto1x=($x+$xsiirto*.7);$lahto1y=($y+$ysiirto*.7);
$lahto2x=($x-$xsiirto*.7);$lahto2y=($y-$ysiirto*.7);
$lahtosuunta=$kulma; 
}
print HANDLE2 "1;".$rastix{$rec3}.";".$rastiy{$rec3}.";0;0N";
$ratapisteet=$ratapisteet.$rastix{$rec3}.";".$rastiy{$rec3}."N";
if(($rastix{$rec3}-$x)*($rastix{$rec3}-$x)+($rastiy{$rec3}-$y)*($rastiy{$rec3}-$y)>1600){
print HANDLE2 "4;".floor($x+$xsiirto).";".floor($y+$ysiirto).";".floor($rastix{$rec3}-$xsiirto).";".floor($rastiy{$rec3}-$ysiirto)."N";#rastiväliviiva
}
if($i>0){
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #rastinumero
}
$x=$rastix{$rec3};$y=$rastiy{$rec3};   
$i++;
}
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #viimeinenrastinumero
## vielä piirretään lähtö

if($rastix{$maali}eq'' ||$rastiy{$maali} eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$maali</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}

print HANDLE3 $ratapisteet.$rastix{$maali}.";".$rastiy{$maali}."N\n";
#print HANDLE2 "2;".$rastix{$lahto}.";".$rastiy{$lahto}.";0;0N";
$lahto3x=$lahto2x+cos($lahtosuunta+$pii/2)*20*0.7;
$lahto3y=$lahto2y+sin($lahtosuunta+$pii/2)*20*0.7;
$lahto4x=$lahto2x-cos($lahtosuunta+$pii/2)*20*0.7;
$lahto4y=$lahto2y-sin($lahtosuunta+$pii/2)*20*0.7; 

print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto1x).";".floor($lahto1y)."N";
print HANDLE2 "4;".floor($lahto1x).";".floor($lahto1y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "\n";
}
}

}
} 
close(HANDLE1);close(HANDLE2);close(HANDLE3);
unlink $path."rastikanta_$in{'eventid'}.txt";
unlink $path."ratakanta_$in{'eventid'}.txt";
unlink $path."sarjakanta_$in{'eventid'}.txt";
print "<p>Ready - Valmis!!!!</b><p>";

open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);
$ulos="";
foreach $rec (@data){ 
($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec);
if($id == $in{'eventid'}){
$mapid=$karttaid;
}
}

print "<p>If you like, you can <b>Georeference event's map</b> with GPX file: <form target=_blank action=../reitti.".$extension."?kieli= method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}><input type=hidden name=act value=map>";
print "<input type=hidden name=mapid value=$mapid>\n";
print "<input type=hidden name=calib value=1><input type=hidden name=gps value=1><input type=hidden name=id value=0>";
print "<br>Select GPX file:&nbsp;&nbsp;<input type=file name=tracklog>&nbsp;&nbsp;&nbsp;&nbsp;<input type=submit value=\"   Go   \" size=20> </form><p>
This will make it easier for competitors to calibrate their GPS routes. <p>You can calibrate map afterwards, tool can be found at manager menu.
";

print "<p><a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";
}
#################3
##### sarjat radat#############################
if ($in{"act"} eq "reititradatviesti"){ 
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manageri menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

$pii = 3.14159265; 
open (SISAAN,"<$path"."sarjakanta_$in{'eventid'}.txt");
@sarjat=<SISAAN>;
close(SISAAN); 

if($in{'eventtype'} == 4){

open (ULOS,">$path"."sarjat_$in{'eventid'}.txt");

foreach $sr (@sarjat){
($id, $nimi)=split(/\|/,$sr);
if($in{'class_'.$id} eq 1){
print ULOS $sr;
}
}

close(ULOS);

}else{
open (ULOS,">$path"."sarjat_$in{'eventid'}.txt");
print ULOS @sarjat;
close(ULOS);
}
# lue radat
open (SISAAN,"<$path"."ratakanta_$in{'eventid'}.txt");
@radat=<SISAAN>;
close(SISAAN); 
open (SISAAN,"<$path"."hajontakanta_$in{'eventid'}.txt");
@hajonnat=<SISAAN>;
close(SISAAN);
## perataan rastit
open (SISAAN,"<$path"."rastikanta_$in{'eventid'}.txt");
@rastit=<SISAAN>;
close(SISAAN);



$pi= 3.14159265; 
if($in{'calibration'} ne ''){
($x1,$y1,$x2,$y2,$ox1,$oy1,$ox2,$oy2)=split(/\,/,$in{'calibration'});


          $pit1=sqrt(($ox1-$ox2)*($ox1-$ox2)+($oy1-$oy2)*($oy1-$oy2));
		   $pit2=sqrt(($x1-$x2)*($x1-$x2)+($y1-$y2)*($y1-$y2));

           $gk1=0;
           $gk2=0;
           $gk3=0;


           if ($x2==$x1){

              if ($y2>$y1){
                 $gk1=$pi/2;
              }else{
                 $gk1=-$pi/2;
				 }

           }else{


              if ($x2<$x1){
                 $gk1=atan(($y2-$y1)/($x2-$x1))+$pi;
               
              }else{
                $gk1=atan(($y2-$y1)/($x2-$x1));
                 }
		    }
			
           if ($ox2==$ox1){

              if ($oy2>$oy1){
                 $gk2=$pi/2;
              }else{
                 $gk2=-$pi/2;
				 }

           }else{

              if ($ox2<$ox1){
                 $gk2=atan(($oy2-$oy1)/($ox2-$ox1))+$pi;
               
              }else{
                $gk2=atan(($oy2-$oy1)/($ox2-$ox1));
                 }
		    }
		}




foreach $rec(@rastit){
chomp($rec);
($koodi,$x,$y)=split(/\|/,$rec);

if($in{'calibration'} eq ''){
$rastix{$koodi}=floor(10*$x*$in{'skaalaus'}+$in{'siirtox'});
$rastiy{$koodi}=floor(10*$y*$in{'skaalaus'}+$in{'siirtoy'});
}else{

# new js calibration with rotation

 $ox3=1*$x*10;
 $oy3=-1*$y*10;
		
	$pit3=sqrt(($ox1-$ox3)*($ox1-$ox3)+($oy1-$oy3)*($oy1-$oy3));
	           if ($ox3==$ox1){

              if ($oy3>$oy1){
                 $gk3=$pi/2;
              }else{
                 $gk3=-$pi/2;
				 }

           }else{

              if ($ox3<$ox1){
                 $gk3=atan(($oy3-$oy1)/($ox3-$ox1))+$pi;
               
              }else{
                $gk3=atan(($oy3-$oy1)/($ox3-$ox1));
                 }
		    }
	
$rastix{$koodi}=floor(0.5+(1*$x1 +(cos($gk3-$gk2+$gk1)*$pit3*$pit2/$pit1)));
$rastiy{$koodi}=-floor(0.5+(1*$y1 +(sin($gk3-$gk2+$gk1)*$pit3*$pit2/$pit1)));

}
}
#open (HANDLE1,">$path"."sarjat_$in{'eventid'}.txt");
open (HANDLE2,">$path"."radat_$in{'eventid'}.txt");   
open (HANDLE3,">$path"."ratapisteet_$in{'eventid'}.txt"); 
foreach $rec(@hajonnat){
chomp($rec);
($sarjaid,$sarjanimi)=split(/\|/,$rec);
if($in{'sarja_'.$sarjaid} ne "pois" && $in{'sarja_'.$sarjaid} ne ""){

foreach $rec2 (@radat){
chomp($rec2);
($aa,$bb,$lahto,$maali,$loput)=split(/\|/,$rec2,5);

if($in{'startcode'} ne ''){
$lahto=$in{'startcode'};
$maali=$in{'finishcode'};
}

@ratarastit=split(/\|/,$loput);
if($in{'sarja_'.$sarjaid} eq $aa."_".$bb){
print HANDLE2 "$sarjaid|1|$in{'sarja2_'.$sarjaid}|";
#print HANDLE2 "2;".$rastix{$lahto}.";".$rastiy{$lahto}.";0;0N";
print HANDLE2 "2;".$rastix{$maali}.";".$rastiy{$maali}.";0;0N"; 
#$ratapisteet="$sarjaid|$in{'sarja2_'.$sarjaid}|".$rastix{$lahto}.";".$rastiy{$lahto}."N";
$ratapisteet="$sarjaid|".$rastix{$lahto}.";".$rastiy{$lahto}."N";
$x=$rastix{$lahto};$y=$rastiy{$lahto}; 

if($x eq'' || $y eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$lahto</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}

$i=0;$kulma=9999;
foreach $rec3 (@ratarastit){

$kulma2=$kulma;
$kulma=atan(($rastiy{$rec3}-$y)/($rastix{$rec3}-$x+0.0000001));

$xsiirto=20*cos($kulma);
$ysiirto=20*sin($kulma);
$suunta=0;
if($rastix{$rec3}<$x){
$xsiirto=-$xsiirto;
$ysiirto=-$ysiirto; 
$suunta=-1;
}
if($kulma2 != 9999){
if($kulma<0){
#$kulma=$kulma+2*$pii;
}
if($kulma>2*$pii){
#$kulma=$kulma-2*$pii;
}
$k=($kulma2+$kulma)/2;

if($edellinensuunta==$suunta){
$k=$k-$pii/2;
} 
$apukulma=$kulma;
if($suunta==-1)    {
$apukulma=$apukulma+$pii;
}

if(abs($apukulma-$k)<$pii/2 || abs($apukulma-$k)>$pii+$pii/2){
$k=$k+$pii;  #print "<br>XXX";
}else{
#print "<br>---";
}
}
$edellinensuunta=$suunta; 

if($i==0){
$lahto1x=($x+$xsiirto*.7);$lahto1y=($y+$ysiirto*.7);
$lahto2x=($x-$xsiirto*.7);$lahto2y=($y-$ysiirto*.7);
$lahtosuunta=$kulma; 
}

if($rastix{$rec3} eq'' || $rastiy{$rec3} eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$rec3</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}

print HANDLE2 "1;".$rastix{$rec3}.";".$rastiy{$rec3}.";0;0N";
$ratapisteet=$ratapisteet.$rastix{$rec3}.";".$rastiy{$rec3}."N";
if(($rastix{$rec3}-$x)*($rastix{$rec3}-$x)+($rastiy{$rec3}-$y)*($rastiy{$rec3}-$y)>1600){
print HANDLE2 "4;".floor($x+$xsiirto).";".floor($y+$ysiirto).";".floor($rastix{$rec3}-$xsiirto).";".floor($rastiy{$rec3}-$ysiirto)."N";#rastiväliviiva
}
if($i>0){
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #rastinumero
}
$x=$rastix{$rec3};$y=$rastiy{$rec3};   
$i++;
}
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #viimeinenrastinumero
## vielä piirretään lähtö
print HANDLE3 $ratapisteet.$rastix{$maali}.";".$rastiy{$maali}."N\n";

if($rastix{$maali} eq'' || $rastiy{$maali} eq ''){
if($virhe != 1){
print "<br><b>ERROR! All courses were not created succesfully!<br> Kaikkien ratojen luonti ei onnistunut!<B><br>\n";
}
print "<br>Control <b>$maali</b> not found (Rastia ei löytynyt)\n";
$virhe=1;
}


#print HANDLE2 "2;".$rastix{$lahto}.";".$rastiy{$lahto}.";0;0N";
$lahto3x=$lahto2x+cos($lahtosuunta+$pii/2)*20*0.7;
$lahto3y=$lahto2y+sin($lahtosuunta+$pii/2)*20*0.7;
$lahto4x=$lahto2x-cos($lahtosuunta+$pii/2)*20*0.7;
$lahto4y=$lahto2y-sin($lahtosuunta+$pii/2)*20*0.7; 

print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto1x).";".floor($lahto1y)."N";
print HANDLE2 "4;".floor($lahto1x).";".floor($lahto1y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "\n";
}
}

}
} 
#close(HANDLE1);
close(HANDLE2);close(HANDLE3);
unlink $path."rastikanta_$in{'eventid'}.txt";
unlink $path."ratakanta_$in{'eventid'}.txt";
unlink $path."sarjakanta_$in{'eventid'}.txt";
print "<p>Ready - Valmis!!!!</b><p><a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";

}



############## 
## kisan poisto
if($in{'act'} eq 'poistakisa' && $in{'kisaid'} ne 'valitse'){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<title></title>
<STYLE>";
&tyyli;
print "</STYLE>
<!--järjestelmän  copyright j.ryyppö 2003-2004 -->
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4>";

$in{'kisaid'}=1*$in{'kisaid'};
open(HANDLE, "<".$path."kisat.txt")|| die;
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);
$ulos="";
foreach $rec (@data){ 
($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec);
if($id eq $in{'kisaid'}){
 ## ei printata takaisin
 print "<p>Óäàëåí ýâåíò ñ ID: $id  $nimi</p><p>Íî èçîáðàæåíèå êàðòû ÍÅ óäàëåíî.</p>";
}else{
$ulos=$ulos.$rec;
}
}

open(HANDLE, ">".$path."kisat.txt");
&lock_file;
print HANDLE $ulos;
&unlock_file;
close HANDLE;
## poistettu indeksistä

unlink($path."kilpailijat_".$in{'kisaid'}.".txt");
unlink($path."kommentit_".$in{'kisaid'}.".txt");
unlink($path."merkinnat_".$in{'kisaid'}.".txt");
unlink($path."radat_".$in{'kisaid'}.".txt");
unlink($path."ratapisteet_".$in{'kisaid'}.".txt");
unlink($path."sarjat_".$in{'kisaid'}.".txt");  
unlink($path."sarjojenkoodit_".$in{'kisaid'}.".txt");  
unlink($path."sarjojenkoodit_".$in{'kisaid'}.".txt"); 
##tiedostot on poistettu
 
print "<p><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a>";


}

######## rastiston tallennus ##################
if ($in{"act"} eq "tallennarastisto"){
open (HANDLE,">".$path."rastikanta_$in{'eventid'}.txt");
print HANDLE $in{'rastisto'};
close(HANDLE);     
print "\n";
}           
######################################################################
if($in{'act'} eq 'tallennarata' ){  
$in{'eventid'}= 1*$in{'eventid'};
open(HANDLE,"<".$path."ratapisteet_$in{'eventid'}.txt");
@data=<HANDLE>;
close(HANDLE);

$uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$loput)=split(/\|/,$rec,2);
if($uusid < $id){$uusid=$id;}
}
$uusid++;
$in{'pisteet'}=~s/\,/\;/g;
open(HANDLE,">>".$path."ratapisteet_$in{'eventid'}.txt");
print HANDLE "$uusid|$in{'pisteet'}\n";
close(HANDLE);      

open(HANDLE,">>".$path."sarjat_$in{'eventid'}.txt");
print HANDLE "$uusid|$in{'ratanimi'}\n";
close(HANDLE);     

open(HANDLE2,">>".$path."radat_$in{'eventid'}.txt");

$pii = 3.14159265; 
@ratarastit=split(/N/,$in{'pisteet'});
$lahto=$ratarastit[0];
$maali=$ratarastit[$#ratarastit];
foreach $rec (@ratarastit){
	($rastix{$rec},$rastiy{$rec})=split(/\;/,$rec);
}
($pois,$in{'pisteet'})=split(/N/,$in{'pisteet'},2);
@ratarastit=split(/N/,$in{'pisteet'});

print HANDLE2 "$uusid|1|$in{'ratanimi'}|";
print HANDLE2 "2;".$rastix{$maali}.";".$rastiy{$maali}.";0;0N"; 
#$ratapisteet="$sarjaid|".$rastix{$lahto}.";".$rastiy{$lahto}."N";
$x=$rastix{$lahto};$y=$rastiy{$lahto}; 
$i=0;$kulma=9999;  $lkm=0;
foreach $rec3 (@ratarastit){
$lkm++;
if($lkm< $#ratarastit+1){
$kulma2=$kulma;
$kulma=atan(($rastiy{$rec3}-$y)/($rastix{$rec3}-$x+0.0000001));

$xsiirto=20*cos($kulma);
$ysiirto=20*sin($kulma);
$suunta=0;
if($rastix{$rec3}<$x){
$xsiirto=-$xsiirto;
$ysiirto=-$ysiirto; 
$suunta=-1;
}
if($kulma2 != 9999){
if($kulma<0){
#$kulma=$kulma+2*$pii;
}
if($kulma>2*$pii){
#$kulma=$kulma-2*$pii;
}
$k=($kulma2+$kulma)/2;

if($edellinensuunta==$suunta){
$k=$k-$pii/2;
} 
$apukulma=$kulma;
if($suunta==-1)    {
$apukulma=$apukulma+$pii;
}

if(abs($apukulma-$k)<$pii/2 || abs($apukulma-$k)>$pii+$pii/2){
$k=$k+$pii;  #print "<br>XXX";
}else{
#print "<br>---";
}
}
$edellinensuunta=$suunta; 

if($i==0){
$x=$rastix{$lahto};$y=$rastiy{$lahto}; 
$lahto1x=($x+$xsiirto*.7);$lahto1y=($y+$ysiirto*.7);
$lahto2x=($x-$xsiirto*.7);$lahto2y=($y-$ysiirto*.7);
$lahtosuunta=$kulma; 
}
print HANDLE2 "1;".$rastix{$rec3}.";".$rastiy{$rec3}.";0;0N";
$ratapisteet=$ratapisteet.$rastix{$rec3}.";".$rastiy{$rec3}."N";
if(($rastix{$rec3}-$x)*($rastix{$rec3}-$x)+($rastiy{$rec3}-$y)*($rastiy{$rec3}-$y)>1600){
print HANDLE2 "4;".floor($x+$xsiirto).";".floor($y+$ysiirto).";".floor($rastix{$rec3}-$xsiirto).";".floor($rastiy{$rec3}-$ysiirto)."N";#rastiväliviiva
}
if($i>0){
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #rastinumero
}
$x=$rastix{$rec3};$y=$rastiy{$rec3};   
$i++;
} 
}
## vielä piirretään lähtö

#print HANDLE2 "2;".$rastix{$lahto}.";".$rastiy{$lahto}.";0;0N";

if($lahto1x eq '' && $lahto2x eq ''){ ## start and finish only
$xsiirto=20*cos(0);
$ysiirto=20*sin(0);
$lahto1x=($x+$xsiirto*.7);$lahto1y=($y+$ysiirto*.7);
$lahto2x=($x-$xsiirto*.7);$lahto2y=($y-$ysiirto*.7);
}else{
print HANDLE2 "3;".floor($x+33*cos($k)-12).";".floor($y+25*sin($k)-8).";$i;0"."N"; #viimeinenrastinumero

}
$lahto3x=$lahto2x+cos($lahtosuunta+$pii/2)*20*0.7;
$lahto3y=$lahto2y+sin($lahtosuunta+$pii/2)*20*0.7;
$lahto4x=$lahto2x-cos($lahtosuunta+$pii/2)*20*0.7;
$lahto4y=$lahto2y-sin($lahtosuunta+$pii/2)*20*0.7; 

print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "4;".floor($lahto3x).";".floor($lahto3y).";".floor($lahto1x).";".floor($lahto1y)."N";
print HANDLE2 "4;".floor($lahto1x).";".floor($lahto1y).";".floor($lahto4x).";".floor($lahto4y)."N";
print HANDLE2 "\n";

close HANDLE2;


}
 ################################################
if($in{'act'} eq 'uusi1' ){  
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML>
<head>
<STYLE>";
&tyyli;
print "</STYLE>
</head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
print "<h3>Äîáàâèòü íîâûé ýâåíò:</h3>
 	
<form action=reittimanager.".$extension." method=post><input type=hidden name=keksi value=$in{'keksi'}>
<b>Òèï ýâåíòà:</b>
<br><input type=radio class=åíç name=eventmode value=0 checked> Çàäàíêà
<br><input type=radio class=radi name=eventmode value=1> Âûáîð
<br><br>
<b>Èçîáðàæåíèå êàðòû:</b>
<br><input type=radio class=radi name=karttatyyppi value=1 checked>1. Çàãðóçèòü íîâóþ êàðòó
<br><input type=radio class=radi name=karttatyyppi value=2>2. Âûáðàòü ðàíåå çàãðóæåííóþ êàðòó

<p>
<b>Results add split times:</b>
<br><input type=radio class=radi name=resulttype value=6 checked> SplitsBrowser CSV
<br><input type=radio class=radi name=resulttype value=3> SportIdent CSV
<br><input type=radio class=radi name=resulttype value=1> PekkaPiril? XML, Individual race format
<br><input type=radio class=radi name=resulttype value=13> PekkaPiril? XML, Relay format
<br><input type=radio class=radi name=resulttype value=7> J.Rajam?ki Reittih?rveli export
<br><input type=radio class=radi name=resulttype value=2> IOF-XML ver 2
<br><input type=radio class=radi name=resulttype value=10> IOF-XML ver 3
<br><input type=radio class=radi name=resulttype value=4> tTiMe CSV
<br><input type=radio class=radi name=resulttype value=8> WinSplits Standard Text Format
<br><input type=radio class=radi name=resulttype value=99> No results, ask name when route is saved.
<p>
<b>Course settings:</b>
<br><input type=radio class=radi name=coursetype value=1 checked> IOF-XML 2( Condes, Ocad9), no forking (Individual race)
<br><input type=radio class=radi name=coursetype value=14> IOF-XML 2 (Condes, Ocad9) with forking (butterflies, relay)
<br><input type=radio class=radi name=coursetype value=2> Ocad 8 courses.txt and dxf
<br><input type=radio class=radi name=coursetype value=3> Controls / courses are pointed manually.
<br><br>
<input type=checkbox class=radi name=ftp value=1> Use pre-loaded split time file \"<b>/kartat/results.txt</b>\"
(<i>use that file name even if you use csv/xml data</i>)
<br><br>
<input type=submit value=\"    OK    \" size=20> 
<input type=hidden name=act value=uusi2>
</form> 
";
      
}        

if($in{'act'} eq 'uusi2' ){  

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML><head><STYLE>";
&tyyli;
print "</STYLE></head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manager menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";
$exit=0;
if ($in{'eventmode'} eq '') {
    print "<br><br>Íå îïðåäåëåí òèï ýâåíòà!";
    $exit=1;
}
if ($in{'karttatyyppi'} eq ''){
    print "<br><br>Raster map type was not selected!";
    $exit=1;
}
if($in{'resulttype'} eq '' ){ 
    print "<br><br>Result type was not selected!";
    $exit=1;
}
if($in{'coursetype'} eq '' ){ 
    print "<br><br>Course settings file type was not selected!";
    $exit=1;
}
if($in{'coursetype'} ne '3' && $in{'resulttype'} eq '99' ){ 
    print "<br><br>The option you selected is not supported. If you have no result file, you have to draw courses manually.";
    $exit=1;
}
if($in{'resulttype'} eq '6' && $in{'coursetype'} eq '3'){
    print "<br><br>The option you selected (SplitsBrowser and manual courses) is not supported.";
    $exit=1;
}
if($exit==1){
    print "<br><br><a href=\"javascript:history.back();\">Back</a>";
    exit;
}
print "<h3>Äîáàâèòü íîâûé ýâåíò:</h3>
<form action=reittimanager.".$extension." method=post enctype='multipart/form-data'><input type=hidden name=keksi value=$in{'keksi'}>";

if($in{'karttatyyppi'} eq '2' ){ 

## luetaan valmiiksi palvelimella olevat kartat
open (SISAAN,"<".$path."kartat.txt");
@kartat=<SISAAN>;
close(SISAAN);  

print "<p>Map list:<br>\n";

foreach $rec (@kartat){ 
	chomp($rec);
($id,$nimi)=split(/\|/,$rec);
print "<a href=../../kartat/".$id.".jpg target=_blank>$nimi</a>\n";
}

print "<p>Select map:<br><select name=karttaid>\n";
foreach $rec (@kartat){ 
	chomp($rec);
($id,$nimi)=split(/\|/,$rec);
print "<option value=$id>$id $nimi\n";
}
print "</select><p>";
}else{
print "<b>Map</b><p>Map name:<br><input type=text name=karttanimi sixe=50 value=''></p>";
print "<p>Select map image (gif or jpg)<br><input type=file name=karttakuva></p>";
    print '<p>Ìàñøòàá: <select name="map_scale"><option value="4000">1:4000</option><option value="5000">1:5000</option><option value="7500" selected>1:7500</option><option value="10000">1:10000</option><option value="15000">1:15000</option></select>';
    print ' dpi: <select name="map_dpi"><option value="150">150</option><option value="200">200</option><option value="300" selected>300</option><option value="600">600</option></select></p>';
}

print "<p><B>Event name:</B><br><input type=text name=nimi sixe=50 value=''>";
print "<p><B>Club name:</B><br>";
if($clubnames_type eq 'field'){
print "<input type=text name=clubname size=50 value='$club_default'>";
}
if($clubnames_type eq 'list'){
open (SISAAN,"<".$path."clubnames.txt");
@data=<SISAAN>;
close(SISAAN);
@data=sort {$a <=> $b} @data;
print "<select name=clubname>";
print "<option value='Unclassified' selected>Select a Club Name below</option>";
foreach $rec (@data){ 
chomp($rec);
($sortid,$clubname)=split(/\|/,$rec);
print "<option value='$clubname'>$clubname</option>\n";
}
print "</select><p>";
}
print "<p><B>Event date:</B><br><table><tr><td><select name=year>";

for($yy=$year-50;$yy<$year+2;$yy++){
if($year == $yy){
print "<option value=$yy selected>$yy</option>\n";
}else{
print "<option value=$yy>$yy</option>\n";
}
}
print "</select></td><td><select name=month>";
for($mm=1;$mm<13;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mon == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td><td><select name=day>";

for($mm=1;$mm<32;$mm++){
if($mm<10){$mm='0'.$mm;}
if($mday == $mm){
print "<option value=$mm selected>$mm</option>\n";
}else{
print "<option value=$mm>$mm</option>\n";
}
}
print "</select></td></tr></table>";

print "<p><b>Event level</b><br>
<select name=eventlevel>
<option value=I>Ìåæäóíàðîäíûå</option>
<option value=N>Âñåðîññèéñêèå</option>
<option value=R selected>Îáëàñòíûå</option>
<option value=L>Ãîðîäñêèå</option>
<option value=T>Òðåíèðîâî÷íûå</option>
</select><p>";

print "Notes (optional):<br>
<textarea name=notes rows=7 cols=30></textarea>\n<p>";

if($in{'resulttype'} eq '99' ){ 
}

if($in{'ftp'} eq "1" && $in{'resulttype'} ne '99'){
print "<input type=hidden name=ftp value=1>";

if($in{'resulttype'} eq '1' ){ 
print "<br><input type=checkbox class=radi name=owncourses value=1>Individual courses - Hajonta/perhoslenkkiradatat (butterflies, score orienteering, goats...)";
}

if($in{'resulttype'} eq '13' ){ 
print "<br><input type=radio class=radi name=classify value=1 checked>Classify competitors by class (normal relays with many classes)
<br><input type=radio class=radi name=classify value=2 checked>Classify competitors by leg (big relays, one big class)";
}
}else{

if($in{'resulttype'} eq '1' ){ 
print "<p><b>Result / split times</b>";	
print "<p>split times xml - Väliajat xml  Pirilä <br><input type=file name=tulosxml>";
print "<br><input type=checkbox class=radi name=owncourses value=1>Individual courses - Hajonta/perhoslenkkiradatat (butterflies, score orienteering, goats...) ";
}
if($in{'resulttype'} eq '10' ){ 
print "<p><b>Result / split times</b>";	
print "<p>split times iof-xml 3 <br><input type=file name=tulosxml>";
print "<br><input type=checkbox class=radi name=owncourses value=1>Individual courses - Hajonta/perhoslenkkiradatat (butterflies, score orienteering, goats...) ";
}

if($in{'resulttype'} eq '13' ){ 
print "<p><b>Result / split times</b>";	
print "<p>split times xml - Väliajat xml  Pirilä Relay -(Viesti)<br><input type=file name=tulosxml><p>
<input type=radio class=radi name=classify value=1 checked>Classify competitors by class (normal relays with many classes)
<br><input type=radio class=radi name=classify value=2 checked>Classify competitors by leg (big relays, one big class)
";
}

if($in{'resulttype'} eq '2' ){          
print "<p><b>Result / split times</b>";	
print "<p>Split times IOF-XML - Väliajat IOF-XML (E-Results, eTiming, OLA, Orienteering Organizer)<br><input type=file name=tulosxml>";
}

if($in{'resulttype'} eq '3' ){          
print "<p><b>Result / split times</b>";	
print "<p>SportIdent split times csv - Väliajat SportIdent csv<br><input type=file name=tulosxml>";


print "<br><input type=radio class=radi name=classify value=1>Classify competitors by class 
<br><input type=radio class=radi name=classify value=2 checked>Classify competitors by course
<br><br><input type=radio class=radi name=owncourses value=0 checked>All runners in a same class have same course.
<br><input type=radio class=radi name=owncourses value=1>Create individual courses using SI csv control codes (butterflies, score orienteering, goats...)
<br><input type=radio class=radi name=owncourses value=2>Create individual courses using course name (butterflies)";

}

if($in{'resulttype'} eq '4' ){          
print "<p><b>Result / split times</b>";	
print "<p>tTiMe csv <br><input type=file name=tulosxml>";
}
if($in{'resulttype'} eq '5' ){          
print "<p><b>Result / split times</b>";	
print "<p>Split times IOF-XML - Väliajat IOF-XML (E-Results, eTiming, OLA, Orienteering Organizer)<br><input type=file name=tulosxml>";
}


if($in{'resulttype'} eq '6' ){          
print "<p><b>Result / split times</b>";	
print "<p>split times SplitsBrowser CSV<br><input type=file name=tulosxml>";
}
if($in{'resulttype'} eq '7' ){          
print "<p><b>Result / split times</b>";	
print "<p> Juhani rajamäen iltarastiohjelman Reittihärveliltiedosto (piir -tiedosto)<br><input type=file name=tulosxml>";
}
if($in{'resulttype'} eq '8' ){          
print "<p><b>Result / split times</b>";	
print "<p>WinSplits Standard Text Format<br><input type=file name=tulosxml>";
}

}
## result types ok

if($in{'coursetype'} ne '3' ){
print "<p><b>Courses</b>"; 
}

if($in{'coursetype'} eq '1' ){ 
print "<p>Courses IOF-XML (Condes, Ocad9)<br><input type=file name=rataxml><p>
<input type=checkbox class=radi name=ftpcondes value=1>Use pre-loaded Condes file \"<b>/kartat/condes.xml</b>\" instead";
}
if($in{'coursetype'} eq '14' ){ 
print "<p>Courses IOF-XML (Condes, Ocad9) with forking (Viesti)<br><input type=file name=rataxml>
<p>
<input type=checkbox class=radi name=ftpcondes value=1>Use pre-loaded IOF-XML (Condes, Ocad9) file \"<b>/kartat/courses.xml</b>\" instead - Käytä etukäteen ftp:llä palvelimelle ladattua <br>tiedostoa <B>\"/kartat/courses.xml\"</B>";

}
if($in{'coursetype'} eq '2' ){ 
print "<p>Courses.txt (Ocad8):<br><input type=file name=courses>";
print "<p> .dxf (Ocad8)<br><input type=file name=alldxf>";
}

print "<p><input type=submit value=\"    OK    \" size=20> 
<input type=hidden name=act value=uusi3>
<input type=hidden name=coursetype value=$in{'coursetype'}>
<input type=hidden name=resulttype value=$in{'resulttype'}>
<input type=hidden name=karttatyyppi value=$in{'karttatyyppi'}>
<input type=hidden name=eventmode value=$in{'eventmode'}>
</form> ";
}       


if($in{'act'} eq "uusi3"){
print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<HTML><head><STYLE>";
&tyyli;
print "</STYLE></head>
<BODY BGCOLOR=#A0A0A0  marginheight=4 topmargin=4><a href=reittimanager.".$extension."?act=manager&keksi=$in{'keksi'}>Manageri menu</a>| <a href=reittimanager.".$extension."?act=logout>Manager Logout</a><hr>";

srand;
$s=rand; 

$q = $in{CGI};

if($in{'karttatyyppi'} eq "1"){ 

open(HANDLE, "<".$path."kartat.txt");
&lock_file;
@data=<HANDLE>; 
&unlock_file;
close(HANDLE);
$map_uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$nimi)=split(/\|/,$rec);
if($map_uusid < $id){$map_uusid=$id;}
}
$map_uusid++;

$file = $q->param("karttakuva");
binmode $file;
@data =<$file>;
close($file); 
$d=join('',@data);          

open (HANDLE, ">".$path.$map_uusid.".jpg");
binmode HANDLE;
print HANDLE $d;
close (HANDLE);                   
if($chmod eq '1'){
    system "chmod 755 ".$path.$map_uusid.".jpg";
}
#äîáàâëÿåì ïàðàìåòðû êàðòû
open(HANDLE, ">>".$path."kartat.txt");
&lock_file;
print HANDLE "$map_uusid|$in{'karttanimi'}\n";
&unlock_file;
close(HANDLE);
#äîáàâëÿåì èíôîðìàöèþ scale,dpi
open(HANDLE, ">>".$path."kartat_dpi.txt");
&lock_file;
print HANDLE "$map_uusid|".$in{'map_scale'}."|".$in{'map_dpi'}."\n";
&unlock_file;
close(HANDLE);
## ok karta lisätty
}else{
$map_uusid=$in{'karttaid'};
}

open(HANDLE, "<".$path."kisat.txt");
&lock_file;
@data=<HANDLE>;
&unlock_file;
close(HANDLE);

$uusid=0;
foreach $rec (@data){
chomp($rec);
($id,$karttaid,$tyyppi,$nimi)=split(/\|/,$rec);
if($uusid < $id){$uusid=$id;}
}
$uusid ++;


$kisatyyppi=1;
if($in{'resulttype'} eq '99'){# no results
$kisatyyppi=2;
}
if($in{'resulttype'} eq '13' ){# relay or point-o
$kisatyyppi=3;
}
if($in{'owncourses'}>0){# relay or point-o
$kisatyyppi=3;
}

$in{'eventname'}=~s/\|//g;
$in{'clubname'}=~s/\|//g;
$in{'notes'}=~s/\|//g;
$in{'notes'}=~s/\n/<br>/g;
$in{'notes'}=~s/\r//g;


$ser='&#39;';
$in{'eventname'}=~s/\'/${ser}/g;
$in{'clubname'}=~s/\'/${ser}/g;
$in{'notes'}=~s/\'/${ser}/g;
$ser='&quot;';
$in{'eventname'}=~s/\"/${ser}/g;
$in{'clubname'}=~s/\"/${ser}/g;
$in{'notes'}=~s/\"/${ser}/g;

open(HANDLE, ">>".$path."kisat.txt");
&lock_file;
print HANDLE "$uusid|$map_uusid|$kisatyyppi|".$in{'nimi'}.'|'.$in{'year'}.'-'.$in{'month'}.'-'.$in{'day'}.'|'.$in{'clubname'}.'|'.$in{'eventlevel'}."|".$in{'notes'}.'|'.$in{'eventmode'}."\n";
&unlock_file;
close(HANDLE);

######################################
## phase1, results
###################################

if($in{'resulttype'} eq '99"'){# no results

}

############## PIRILÄ Relay xml
if($in{'resulttype'} eq "13"){ #pirila relay

if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");

open(HANDLE, ">".$path."emitajat_$s.xml");
while (defined ($rec = <$file>)){
$rec=~ s/\r//g;
$rec=~ s/\n//g;
print HANDLE $rec;
}
close(HANDLE);   
close($file); 

}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
$rec=~ s/\n//g;
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}

if ((-e "".$path."emitajat_$s.xml") eq "1") {
open (SIS,"<".$path."emitajat_$s.xml");
@emitajat=<SIS>;
close (SIS); 
$emitajat = $emitajat[0];
undef @emitajat;

open (HANDLE,">".$path."kilpailijat_$uusid.txt");

$sarjanro=0;$kilpailijannro=1;$osuusmax=0;
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja
$position_emitajat=0;
while($position_emitajat >-1){
print "X";
$sarjanro++;
($sarja,$position_emitajat)=getElement($emitajat,'<class>','</class>',$position_emitajat);

## sarjan nimi
($sarja[$sarjanro],$temp)=getElement($sarja,'<classname>','</classname>',0); 
$sarja[$sarjanro]=getElementValue($sarja[$sarjanro]);
print $sarja[$sarjanro]." "; 

$position_sarja=0;
while($position_sarja >-1){
($team,$position_sarja)=getElement($sarja,'<team>','</team>',$position_sarja);  
$teamnro++;
($team[$teamnro],$temp)=getElement($team,'<teamname>','</teamname>',0); 
$team[$teamnro]=getElementValue($team[$teamnro]);   

($teamnr,$temp)=getElement($team,'<teamnro>','</teamnro>',0); 
$teamnr=getElementValue($teamnr);
$team[$teamnro]=$team[$teamnro]." $teamnr";


$position_team=0;$lahtoaika=0;
while($position_team >-1){
($leg,$position_team)=getElement($team,'<leg>','</leg>',$position_team);  
$kilpnro++;

($temppi,$temp)=getElement($leg,'<legnro>','</legnro>',0); 
$osuus[$kilpnro]=getElementValue($temppi);         
if($osuus[$kilpnro]>$osuusmax){
	$osuusmax=$osuus[$kilpnro];
}
($temppi,$temp)=getElement($leg,'<result>','</result>',0); 
$tulos[$kilpnro]=getElementValue($temppi);

($temppi,$temp)=getElement($leg,'<tsecs','</tsecs>',0); 
$tulossek[$kilpnro]=getElementValue($temppi);

($kilpailija[$kilpnro],$temp)=getElement($leg,'<nm>','</nm>',0); 
$kilpailija[$kilpnro]=getElementValue($kilpailija[$kilpnro]);

($hajonta[$kilpnro],$temp)=getElement($leg,'<crs>','</crs>',0); 
$hajonta[$kilpnro]=getElementValue($hajonta[$kilpnro]); 

$position_leg=0; $splits=""; $ccodes="";
while($position_leg >-1){
($cou_code,$notused)=getElement($leg,'<cc>','</cc>',$position_leg);  
$cou_code=getElementValue($cou_code);
if($cou_code ne ''){
$ccodes.='_'.$cou_code;
}
($split,$position_leg)=getElement($leg,'<ct>','</ct>',$position_leg);  
$split=getElementValue($split);
($vhour,$vmin,$vsek)=split(/\:/,$split,3);
if($vsek eq ''){
$vsek=$vmin;
$vmin=$vhour;
$vhour=0;
}
if($vsek eq ''){ 
$vsek=$vmin;
$vhour=0;
$vmin=0;
}
$split=$vsek+60*$vmin+60*60*$vhour;  
$splits=$splits.$split.";";
}
$valiajat[$kilpnro]=$splits;


if($kilpailija[$kilpnro] ne ""){

###print "$sarja[$sarjanro]/$team[$teamnro]/$kilpailija[$kilpnro]/$hajonta[$kilpnro]/$valiajat[$kilpnro]\n"; 

if($hajontanimi{$sarja[$sarjanro].'('.$hajonta[$kilpnro].')'} eq ''){
$hajontalkm++;
$hajontanimi{$sarja[$sarjanro].'('.$hajonta[$kilpnro].')'}='1';
$hajontaname[$hajontalkm]=lc($sarja[$sarjanro]).'('.$hajonta[$kilpnro].')';
$hajontaID{$hajontaname[$hajontalkm]}=$hajontalkm;
$ccodes =~ s/^_+//;
$ccodes =~ s/_+$//;

$hajontacodes[$hajontalkm]=$ccodes;
}

if($in{'classify'} eq '1'){
print HANDLE "$kilpnro|$sarjanro|$sarja[$sarjanro]|$kilpailija[$kilpnro] ($osuus[$kilpnro]) $team[$teamnro]|$lahtoaika|$osuus[$kilpnro]|$hajontaID{lc($sarja[$sarjanro]).'('.$hajonta[$kilpnro].')'}|$tulos[$kilpnro]|$valiajat[$kilpnro]\n";
}else{
print HANDLE "$kilpnro|$osuus[$kilpnro]|$sarja[$sarjanro]|$kilpailija[$kilpnro] ($osuus[$kilpnro]) $team[$teamnro]|$lahtoaika|$osuus[$kilpnro]|$hajontaID{lc($sarja[$sarjanro]).'('.$hajonta[$kilpnro].')'}|$tulos[$kilpnro]|$valiajat[$kilpnro]\n";
}
$lahtoaika=$lahtoaika+$tulossek[$kilpnro];

}
}
}
}               
             

close (HANDLE);   
open (HANDLE,">".$path."sarjakanta_$uusid.txt");
if($in{'classify'} eq '1'){
	for ($i=1;$i<$sarjanro+1;$i++){ 
		if($sarja[$i] ne ''){
			print HANDLE "$i|$sarja[$i]\n";              
		}
	}
}else{
	for ($i=1;$i<$osuusmax+1;$i++){ 
		#if($sarja[$i] ne ''){
			print HANDLE "$i| $i \n";              
		#}
	}
}

close (HANDLE); 
print"\n";          
open (HANDLE,">".$path."hajontakanta_$uusid.txt");
for ($i=1;$i<$hajontalkm+1;$i++){ 
if($hajontaname[$i] ne ''){
print HANDLE "$i|$hajontaname[$i]|$hajontacodes[$i]\n";              
}
}
close (HANDLE); 
print"\n";
}else{
print "emitajat.xml puuttuu!";
exit;
}
}


###################################
if($in{'resulttype'} eq "1" || $in{'resulttype'} eq "10" ){#pirila or iof xml3 
if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 
$d=join('',@data); 
$d=~ s/\r//g;
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}
## xml formats

if ((-e "".$path."emitajat_$s.xml") eq "1") {
open (SIS,"<".$path."emitajat_$s.xml");
@emitajat=<SIS>;
close (SIS); 
$emitajat = join('',@emitajat);

if($in{'owncourses'} ==1){
open (HANDLE5,">".$path."ratakanta_$uusid.txt");  
open (HANDLE4,">".$path."hajontakanta_$uusid.txt");
}
# iof xml3 conversion 
if($in{'resulttype'} eq "10" ){
&iof3topirila;
$in{'resulttype'}='1'; # continue from here just as with pirila files
}

$pirila=1;

$sarjanro=1;$kilpailijannro=1;
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja

$sarjaloppu=0;
print "<b>Sarjat:</b><br>";
while($sarjaloppu==0){
if($pirila==1){
&haesarja_pirila;
}else{
&haesarja_eresults;
}
if($sarjaloppu ==0){
print $sarjat[$sarjanro-1]."\n";
$loppu=0;
while($loppu==0){
if($pirila==1){
&haekilpailija_pirila;
}else{
&haekilpailija_eresults;
}
if($loppu==0){ 
if($pirila==1){
&haevaliajat_pirila;
}else{
&haevaliajat_eresults;
}
 } 
 }
}
}
## ok, tiedot muuttujissa. Printataanpa ne tiedostoihin ##
## Sarjat:
open (HANDLE,">".$path."sarjakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u.'|'.$sarjat[$u]."\n";
}
close (HANDLE);

## Sarjat:          

open (HANDLE,">".$path."sarjojenkoodit_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u."|START".$erekoodi[$u]."|FINISH\n";
}
close (HANDLE);

print '#'.$in{'normalize'}.'#';
if($in{'normalize'}==1){ ## hajontalenkkien normalisointi

for($u=1;$u<$kilpailijannro;$u++){
if($normal{$sarjanro[$u]} eq ''){
	$normal{$sarjanro[$u]}=1;
@normalcodes=split(/\|/,$kooditonormalize[$u]);
$vali=1;
foreach $rec (@normalcodes){

$nvalilkm{$normalcodes[$vali-1].'_'.$normalcodes[$vali]}++;

$nvali[$vali]=$normalcodes[$vali-1].'_'.$normalcodes[$vali].'_'.$nvalilkm{$normalcodes[$vali-1].'_'.$normalcodes[$vali]};
$vali++;
}
}else{

undef %anvalilkm;
undef %anvali;
@anormalcodes=split(/\|/,$kooditonormalize[$u]);

$vali=1;
foreach $rec (@anormalcodes){
$anvalilkm{$anormalcodes[$vali-1].'_'.$anormalcodes[$vali]}++;
$anvali{$anormalcodes[$vali-1].'_'.$anormalcodes[$vali].'_'.$anvalilkm{$anormalcodes[$vali-1].'_'.$anormalcodes[$vali]}}=$vali;
$vali++;
}

##
$vali=1;
foreach $rec (@normalcodes){
$temp=$valiaika[$u][$vali];
$valiaika[$u][$vali]=$valiaika[$u][$anvali{$nvali[$vali]}]-$valiaika[$u][$anvali{$nvali[$vali]}-1]+$valiaika[$u][$vali-1];
$vali++;
if($valiaika[$u][$vali-1] != $temp){
print "M";
}
}
print '.';

## normalized
}
}
}

## Kilpailijat


open (HANDLE,">".$path."kilpailijat_$uusid.txt");
for($u=1;$u<$kilpailijannro;$u++){



$rasti=1;$out='';$codes='';
while($valiaika[$u][$rasti]>0){
$out.=$valiaika[$u][$rasti].";";
$rasti++;
}


$apu=$u.'|'.$sarjanro[$u].'|'.$sarja[$u].'|'.$kilpailija[$u].'|'.$laika[$u].'|'.$aika[$u].'|'.$hhajonta[$u].'|'.$tulos[$u].'|';
$apu =~ s/\n//g;
$apu =~ s/\r//g;
print HANDLE $apu.$out;
print HANDLE "\n";
}
close (HANDLE);
print "\n";

}else{
print "Results are missing!";
exit;
}

#### if no course files, we have to write out codes
if($in{'coursetype'} eq "3"){ 
open (HANDLE,">".$path."ratakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE "$sarjat[$u]|$sarjat[$u]|START|FINISH".$erekoodi[$u]."\n";
}
close (HANDLE);
}
}

#####################3
if($in{'resulttype'} eq "2"){#e-results, OLA etc IOF-XML
if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 
$d=join('',@data); 
$d=~ s/\r//g;
$d=~ s/\n//g;
$d=~ s/HH\:MM\:SS/H\:MM\:SS/gi; 
$d=~ s/\"MM\:SS\"/\"H\:MM\:SS\"/gi; 
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
$rec=~ s/\n//g;
$rec=~ s/HH\:MM\:SS/H\:MM\:SS/gi; 
$d=~ s/\"MM\:SS\"/\"H\:MM\:SS\"/gi; 
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}
##### parsing
 ## xml formats

if ((-e "".$path."emitajat_$s.xml") eq "1") {
open (SIS,"<".$path."emitajat_$s.xml");
@emitajat=<SIS>;
close (SIS); 
$emitajat = join('',@emitajat);


$pirila=0;

 
$sarjanro=1;$kilpailijannro=1;
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja

$sarjaloppu=0;
print "<b>Sarjat:</b><br>";
while($sarjaloppu==0){
if($pirila==1){
&haesarja_pirila;
}else{
&haesarja_eresults;
}
if($sarjaloppu ==0){
print $sarjat[$sarjanro-1]."\n";
$loppu=0;
while($loppu==0){
if($pirila==1){
&haekilpailija_pirila;
}else{
&haekilpailija_eresults;
}
if($loppu==0){ 
if($pirila==1){
&haevaliajat_pirila;
}else{
&haevaliajat_eresults;
}
 } 
 }
}
}
## ok, tiedot muuttujissa. Printataanpa ne tiedostoihin ##
## Sarjat:
open (HANDLE,">".$path."sarjakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u.'|'.$sarjat[$u]."\n";
}
close (HANDLE);

## Sarjat:                 
open (HANDLE,">".$path."sarjojenkoodit_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u."|START".$erekoodi[$u]."|FINISH\n";
}
close (HANDLE);



## Kilpailijat
open (HANDLE,">".$path."kilpailijat_$uusid.txt");
for($u=1;$u<$kilpailijannro;$u++){
$apu=$u.'|'.$sarjanro[$u].'|'.$sarja[$u].'|'.$kilpailija[$u].'|'.$laika[$u].'|'.$aika[$u].'|'.$sija[$u].'|'.$tulos[$u].'|';
$apu =~ s/\n//g;
$apu =~ s/\r//g;
print HANDLE $apu;
$rasti=1;
while($valiaika[$u][$rasti]>0){
print HANDLE $valiaika[$u][$rasti].";";
$rasti++;
}

if($aika[$u]>$valiaika[$u][$rasti-1]+1){ # OO && OLA missing last split fix
print HANDLE $aika[$u].";";
}

print HANDLE "\n";
}
close (HANDLE);
print"\n";

}else{
print "Results are missing!";
exit;
}

#### if no course files, we have to write out codes
if($in{'coursetype'} eq "3"){ 
open (HANDLE,">".$path."ratakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE "$sarjat[$u]|$sarjat[$u]|START|FINISH".$erekoodi[$u]."\n";
}
close (HANDLE);
}
}    

###################################
if($in{'resulttype'} eq "5"){#eTiming xml 
if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 
$d=join('',@data); 
$d=~ s/\r//g; 
$d=~ s/sequense/sequence/g; 
$d=~ s/HH\:MM\:SS/H\:MM\:SS/gi; 
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
$rec=~ s/sequense/sequence/g; 
$rec=~ s/HH\:MM\:SS/H\:MM\:SS/gi; 
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}


if ((-e "".$path."emitajat_$s.xml") eq "1") {
open (SIS,"<".$path."emitajat_$s.xml");
@emitajat=<SIS>;
close (SIS); 
$emitajat = join('',@emitajat);


$sarjanro=1;$kilpailijannro=1;
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja

$sarjaloppu=0;
print "<b>Sarjat:</b><br>";
while($sarjaloppu==0){

&haesarja_eresults;

if($sarjaloppu ==0){
print $sarjat[$sarjanro-1]."\n";
$loppu=0;
while($loppu==0){

&haekilpailija_eresults;

if($loppu==0){ 

&haevaliajat_eresults;

 } 
 }
}
}
## ok, tiedot muuttujissa. Printataanpa ne tiedostoihin ##
## Sarjat:
open (HANDLE,">".$path."sarjakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u.'|'.$sarjat[$u]."\n";
}
close (HANDLE);

## Sarjat:                 
open (HANDLE,">".$path."sarjojenkoodit_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE $u."|START".$erekoodi[$u]."|FINISH\n";
}
close (HANDLE);



## Kilpailijat
open (HANDLE,">".$path."kilpailijat_$uusid.txt");
for($u=1;$u<$kilpailijannro;$u++){
$apu=$u.'|'.$sarjanro[$u].'|'.$sarja[$u].'|'.$kilpailija[$u].'|'.$laika[$u].'|'.$aika[$u].'|'.$sija[$u].'|'.$tulos[$u].'|';
$apu =~ s/\n//g;
$apu =~ s/\r//g;
print HANDLE $apu;
$rasti=1;
while($valiaika[$u][$rasti]>0){
print HANDLE $valiaika[$u][$rasti].";";
$rasti++;
}



print HANDLE "\n";
}
close (HANDLE);
print"\n";

}else{
print "Results are missing!";
exit;
}

#### if no course files, we have to write out codes
if($in{'coursetype'} eq "3"){ 
open (HANDLE,">".$path."ratakanta_$uusid.txt");
for($u=1;$u<$sarjanro;$u++){
print HANDLE "$sarjat[$u]|$sarjat[$u]|START|FINISH".$erekoodi[$u]."\n";
}
close (HANDLE);
}
}



################################
if($in{'resulttype'} eq "6"){# SplitsBrowser CSV

if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 

$d=join('',@data); 
$d=~ s/\r//g;
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}

open(HANDLE, "<".$path."emitajat_$s.xml");
@data= <HANDLE>;
close(HANDLE); 

$d=join('',@data);

@d=split(/\n\n/,$d);


open (HANDLE1,">".$path."sarjakanta_$uusid.txt"); 
open (HANDLE2,">".$path."kilpailijat_$uusid.txt");


$id=0;$idclass=0;
foreach $rec (@d){
    chomp($rec);
($chead,$runners)=split(/\n/,$rec,2);
($apn,$ncls)=split(/\,/,$chead,2);

$idclass++;
print HANDLE1 "$idclass|$apn\n";  

@r=split(/\n/,$runners);

foreach $row (@r){
$id++;

($fname,$lname,$club,$stime,$splits)=split(/\,/,$row,5);
	
($min,$sec)=split(/\:/,$stime);
$stime=$sec+60*$min;

@s=split(/\,/,$splits);

$tmp='';$rtime=0;

foreach $sp (@s){
($min,$sec)=split(/\:/,$sp);
$spl=$sec+60*$min;
$rtime=$rtime+$spl;
$tmp=$tmp.$rtime.';';

}

$r_min=floor($rtime/60);
$r_sec=$rtime-60*floor($rtime/60);
	
	
print HANDLE2 "$id|$idclass|$apn|$fname $lname, $club|$stime|||$r_min:$r_sec|$tmp\n"; 
	
}	

}

close(HANDLE2); 
close(HANDLE1); 
}

######################################
if($in{'resulttype'} eq "7"){#Rajamäki
if($in{'ftp'} ne "1"){

$file = $q->param("tulosxml");
@data=<$file>;
close($file); 

}else{
open (HANDLE2,"<$path"."results.txt");  
@data=<HANDLE2>;
close(HANDLE2); 
}

$d=join('',@data); 
$d=~ s/\r//g;


open (HANDLE2,">".$path."kilpailijat_$uusid.txt");
print HANDLE2 $d;
close(HANDLE2);   

$out='';
foreach $rec (@data){
chomp($rec);
@r=split(/\|/,$rec);
if($srjaon{$r[1]} eq ''){
$out.=$r[1].'|'.$r[2]."\n";
$srjaon{$r[1]}=1;
}
}

open (HANDLE1,">".$path."sarjakanta_$uusid.txt"); 
print HANDLE1 $out;
close(HANDLE1);  
}


################################
if($in{'resulttype'} eq '8'){# WinSplits Standard Text Format

if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 

$d=join('',@data); 
$d=~ s/\r//g;
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}

open(HANDLE, "<".$path."emitajat_$s.xml");
@data= <HANDLE>;
close(HANDLE); 

$d=join('',@data);

($pois,$d)=split(/\n\n/,$d,2);
@d=split(/\n\n/,$d);

open (HANDLE1,">".$path."sarjakanta_$uusid.txt"); 
open (HANDLE2,">".$path."kilpailijat_$uusid.txt");


$id=0;$idclass=0;
foreach $rec (@d){
    chomp($rec);
($apn,$cdistances,$runners)=split(/\n/,$rec,3);
$idclass++;

print HANDLE1 "$idclass|$apn\n";  

@r=split(/\n/,$runners);

foreach $row (@r){
$id++;

($cname, $club,$stime,$splits)=split(/\t/,$row,4);

if($club ne ''){$cname.=', '.$club;}
	
($hour, $min,$sec)=split(/\./,$stime);
$stime=$hour*60*60+$sec+60*$min;

@s=split(/\t/,$splits);

$tmp='';$rtime=0;
$ok=1;
foreach $sp (@s){

if(&trim($sp) eq '-'){ ## DQ
$cresult=" DNF ";
$ok=10
}else{
if($ok == 1){
@spt=split(/\./,$sp);
$spl=$spt[$#spt]+$spt[$#spt-1]*60;
if($#spt >1){
$spl+=$spt[$#spt-2]*60*60;
}

if($spl== 0){$spl=1;} # the split is missing, one second used instead

$rtime=$rtime+$spl;
$tmp=$tmp.$rtime.';';
}
}
}

if($ok == 1){
$r_min=floor($rtime/60);
$r_sec=$rtime-60*floor($rtime/60);
if(length($r_sec)<2){$r_sec='0'.$r_sec;}
$cresult="$r_min:$r_sec";
}

print HANDLE2 "$id|$idclass|$apn|$cname|$stime|||$cresult|$tmp\n"; 
	
}	

}

close(HANDLE2); 
close(HANDLE1); 
}

######################################
if($in{'resulttype'} eq "3"){#si
&SISPLITS;
}

################################3
if($in{'resulttype'} eq "4"){#ttime

if($in{'ftp'} ne "1"){
$file = $q->param("tulosxml");
@data=<$file>;
close($file); 
$d=join('',@data); 
$d=~ s/\r//g;
open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $d;
close(HANDLE);   
}else{
open(HANDLE, ">".$path."emitajat_$s.xml");
open (HANDLE2,"<$path"."results.txt");
while (defined ($rec = <HANDLE2>)) {   
$rec=~ s/\r//g;
print HANDLE $rec;
}
close(HANDLE2); 
close(HANDLE); 
}

open(HANDLE, "<".$path."emitajat_$s.xml");
@data=<HANDLE>;
close(HANDLE);   

open (HANDLE1,">".$path."sarjakanta_$uusid.txt"); 
open (HANDLE,">".$path."ratakanta_$uusid.txt");
open (HANDLE3,">".$path."sarjojenkoodit_$uusid.txt");

## lets see what courses we have
$id=0;$idclass=0;
foreach $rec (@data){
    chomp($rec);
if($rec ne ''){
@f=split(/\;/,$rec);

$field{'L'}=&getOptVal($rec, 'L');

if($eClass{$f[3]} eq '' && $f[3] ne '' && $f[1] eq 'X'){
$idclass++;
print HANDLE1 "$idclass|$f[3]\n";    
$eClass{$f[3]}=$idclass;
}
if($eCourse{$field{'L'}} eq '' && $f[3] ne '' && $f[1] eq 'X'){
$id++;
$eCourse{$field{'L'}}=$id;
if($field{'L'} ne ''){
print HANDLE "$field{'L'}|$field{'L'} $f[3]|START"; $out='|FINISH';
print HANDLE3 "$id|START";
###
$j=1;
foreach $split (@f){
$j++;
if($j%3==0 && $j>11){  
#print HANDLE "|$f[$j-4]";
$out=$out."|$f[$j-4]";$lastcode=$f[$j-4];
print HANDLE3 "|$f[$j-4]";
}
}
$out =~ s/\|FINISH/${lastcode}/;
print HANDLE "|$out\n";         
print HANDLE3 "\n";
}# if($field{'L'} ne '')
#######  

}
}
}
close(HANDLE2);        
close(HANDLE);    
close(HANDLE3);                    
 
## OK, let's parse splits etc
open (HANDLE2,">".$path."kilpailijat_$uusid.txt");
$id=0;             
foreach $rec (@data){
if($rec ne ''){
     $id++;
     chomp($rec);
@f=split(/\;/,$rec);
if($f[1] eq 'X'){

$field{'S'}=&getOptVal($rec, 'S');

($hour,$min,$sec)=split(/\:/,$field{'S'});
if($sec eq ""){
$sec=$min;
$min=$hour;
$hour=0;
}  
$field{'S'}=$sec+60*$min+60*60*$hour;

print HANDLE2 "$id|$eClass{$f[3]}|$f[3]|$f[2], $f[4]|$field{'S'}|||$f[7]|";    
$i=1;
foreach $split (@f){
$i++;
if($i%3==0 && $i>11){  
($hour,$min,$sec)=split(/\:/,$split);
if($sec eq ""){
$sec=$min;
$min=$hour;
$hour=0;
}  
$split=$sec+60*$min+60*60*$hour;
$code=$code.'|'.$f[$i-4];
print HANDLE2 "$split;";
}
}
 print HANDLE2 "\n";         
 

 }
}
}


}

#################################################
######## course parsers #########################
#################################################

if($in{'coursetype'} eq "1"){ # Condes

$file = $q->param("rataxml");
@data=<$file>;
close($file); 
$d=join('',@data);
$d =~ s/\r//g;
open(HANDLE, ">".$path."radat_$s.xml");
print HANDLE $d;
close(HANDLE); 
### condes  parser#############


open (SIS,"<".$path."radat_$s.xml");
@radat=<SIS>;
close (SIS); 
$radat = join('',@radat);

print "<p><b>Maastopisteet:</b><br>";
open (HANDLE,">".$path."rastikanta_$uusid.txt");

######lähdöt################################
$lahtolkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haelahto;
}

for($i=1;$i<$lahtolkm+1;$i++){
print "$startcode[$i] ";
print HANDLE $startcode[$i]."|";
print HANDLE $start_x[$i]."|";
print HANDLE $start_y[$i]."\n";
}
######rastit################################
$rastilkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haerasti;
}


for($i=1;$i<$rastilkm+1;$i++){
print "$rasticode[$i] ";
print HANDLE $rasticode[$i]."|";
print HANDLE $rasti_x[$i]."|";
print HANDLE $rasti_y[$i]."\n";
}

#######maalit#################################3
$maalilkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haemaali;
}

for($i=1;$i<$maalilkm+1;$i++){
print "$fcode[$i] ";
print HANDLE $fcode[$i]."|";
print HANDLE $f_x[$i]."|";
print HANDLE $f_y[$i]."\n";
}
close(HANDLE); 
## skaalataan rastit 0-1000 -alueelle
open (HANDLE,"<".$path."rastikanta_$uusid.txt");
@rastit=<HANDLE>;
close (HANDLE);
 
$xmax=-999999999;
$xmin=999999999;
$ymax=-999999999;
$ymin=999999999;

foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($xx<$xmin){$xmin=$xx;}
if($yy<$ymin){$ymin=$yy;}
if($xx>$xmax){$xmax=$xx;}
if($yy>$ymax){$ymax=$yy;}
}

if($xmax==$xmin && $ymax==$ymin){
$xmax++;
$ymax++;
$samassapisteessa=1;
}

## skaalauskessoin
$k=150/($xmax-$xmin);
$k2=150/($ymax-$ymin); 
if($k2<$k){$k=$k2;}

$siirtyma_x=-$xmin;
$siirtyma_y=-$ymax;
                                                 
# tallennetaan skaalatut tiedot
open (HANDLE,">".$path."rastikanta_$uusid.txt");
foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($samassapisteessa==1){
$xx++;
$yy++;
$samassapisteessa=0;
}
$x=($xx+$siirtyma_x)*$k+25;
$y=($yy+$siirtyma_y)*$k+25;
print HANDLE "$kod|$x|$y\n";
} 
close (HANDLE);
# valmis
print "<p><b>Radat:</b><br>";
if($in{'owncourses'} !=1){
open (HANDLE,">".$path."ratakanta_$uusid.txt");
}
#######radat#################################3
$ratalkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haerata;
if($loppu == 0){
$clkm=0;$loppu_=0;$v1_=0;$v2_=0;
while($loppu_==0){
&haec;
}
$v1_=0;$v2_=0;
&haes;
$v1_=0;$v2_=0;
&haef;
$v1_=0;$v2_=0;
&haeid;
$v1_=0;$v2_=0;
&haename;
$v1_=0;$v2_=0;
&haesarjat;      
$test++;
if($test>500){exit;}
print "$rid[$ratalkm] ";

if($in{'owncourses'} !=1){
print HANDLE $rid[$ratalkm]."|".$rname[$ratalkm]."|".$scode[$ratalkm]."|".$fcode[$ratalkm];

for($i=1;$i<$clkm+1;$i++){
print HANDLE "|".$ccode[$ratalkm][$i];
}
print HANDLE "\n";
}
}

}
if($in{'owncourses'} !=1){
close(HANDLE);
}
}

########## condes relay 

if($in{'coursetype'} eq "14"){ # Condes relay

if($in{'ftpcondes'} ne "1"){
$file = $q->param("rataxml");
}else{
$file="HANDLE2";
open($file, "<".$path."courses.xml");
}
open(HANDLE, ">".$path."radat_$s.xml");
while (defined ($rec = <$file>)){
$rec=~ s/\r//g;
$rec=~ s/\n//g;
$rec=~ s/CourseBranch/CourseVariation/g;

print HANDLE $rec;
}
close(HANDLE);   
close($file); 

### radat.xml -tiedoston purku
if ((-e "".$path."radat_$s.xml") eq "1") {

undef $emitajat;

open (SIS,"<".$path."radat_$s.xml");
@rdt=<SIS>;
close (SIS); 

$radat = $rdt[0];
undef @rdt;

print "v";
print "<p><b>Maastopisteet:</b><br>";
open (HANDLE,">".$path."rastikanta_$uusid.txt");

######lähdöt################################
$lahtolkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haelahto;
}

for($i=1;$i<$lahtolkm+1;$i++){
print "$startcode[$i] ";
print HANDLE $startcode[$i]."|";
print HANDLE $start_x[$i]."|";
print HANDLE $start_y[$i]."\n";
}
######rastit################################
$rastilkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haerasti;
}


for($i=1;$i<$rastilkm+1;$i++){
print "$rasticode[$i] ";
print HANDLE $rasticode[$i]."|";
print HANDLE $rasti_x[$i]."|";
print HANDLE $rasti_y[$i]."\n";
}

#######maalit#################################3
$maalilkm=0;$loppu=0;$v1=0;$v2=0;
while($loppu==0){
&haemaali;
}

for($i=1;$i<$maalilkm+1;$i++){
print "$fcode[$i] ";
print HANDLE $fcode[$i]."|";
print HANDLE $f_x[$i]."|";
print HANDLE $f_y[$i]."\n";
}
close(HANDLE); 
## skaalataan rastit 0-1000 -alueelle
open (HANDLE,"<".$path."rastikanta_$uusid.txt");
@rastit=<HANDLE>;
close (HANDLE);
 
$xmax=-999999999;
$xmin=999999999;
$ymax=-999999999;
$ymin=999999999;

foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($xx<$xmin){$xmin=$xx;}
if($yy<$ymin){$ymin=$yy;}
if($xx>$xmax){$xmax=$xx;}
if($yy>$ymax){$ymax=$yy;}
}

if($xmax==$xmin && $ymax==$ymin){
$xmax++;
$ymax++;
$samassapisteessa=1;
}

## skaalauskessoin
$k=150/($xmax-$xmin);
$k2=150/($ymax-$ymin); 
if($k2<$k){$k=$k2;}

$siirtyma_x=-$xmin;
$siirtyma_y=-$ymax;
                                                 
# tallennetaan skaalatut tiedot
open (HANDLE,">".$path."rastikanta_$uusid.txt");
foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($samassapisteessa==1){
$xx++;
$yy++;
$samassapisteessa=0;
}
$x=($xx+$siirtyma_x)*$k+25;
$y=($yy+$siirtyma_y)*$k+25;
print HANDLE "$kod|$x|$y\n";
} 
close (HANDLE);
# valmis

print "<p>Radat:<br>";
if($in{'owncourses'} !=1){
open (HANDLE,">".$path."ratakanta_$uusid.txt");
}
$position_rata=0;
while($position_rata >-1){
($course,$position_rata)=getElement($radat,'<Course>','</Course>',$position_rata);
($coursename,$temp)=getElement($course,'<CourseName>','</CourseName>',0);


$coursename=getElementValue($coursename);

$position_course=0;
while($position_course >-1){
$ratanro++;
($coursevariation,$position_course)=getElement($course,'<CourseVariation>','</CourseVariation>',$position_course);
if($coursevariation =~ /<Name>/){
($coursevariationname,$temp)=getElement($coursevariation,'<Name>','</Name>',0);
}else{
($coursevariationname,$temp)=getElement($coursevariation,'<CourseVariationId>','</CourseVariationId>',0);
}
$coursevariationname=getElementValue($coursevariationname);

if($coursevariationname ne ''){
if($in{'owncourses'} !=1){
print HANDLE $ratanro."|".$coursename."($coursevariationname)|";  
}
print $coursename."($coursevariationname), ";  

($startcode,$temp)=getElement($coursevariation,'<StartPointCode>','</StartPointCode>',0);
$startcode=&trim(getElementValue($startcode));
if($in{'owncourses'} !=1){
print HANDLE "$startcode|";
                }
($finishcode,$temp)=getElement($coursevariation,'<FinishPointCode>','</FinishPointCode>',0);
$finishcode=&trim(getElementValue($finishcode));
if($in{'owncourses'} !=1){
print HANDLE "$finishcode";                
}
$position_coursevariation=0;
while($position_coursevariation >-1){
($controlcode,$position_coursevariation)=getElement($coursevariation,'<ControlCode>','</ControlCode>',$position_coursevariation);
$controlcode=&trim(getElementValue($controlcode));    
if($controlcode ne ''){
if($in{'owncourses'} !=1){
print HANDLE "|$controlcode";
}
}
}
if($in{'owncourses'} !=1){   
print HANDLE "\n";
}
}
}
}       
if($in{'owncourses'} !=1){
close(HANDLE);
}
}
}

#############3
if($in{'coursetype'} eq "2"){ # Ocad(

$file = $q->param("courses");
@data=<$file>;
close($file); 
$d=join('',@data);
$d=~ s/\r//g;
open(HANDLE, ">".$path."Courses_$s.txt");
print HANDLE $d;
close(HANDLE); 

$file = $q->param("alldxf");

@data=<$file>;
close($file); 
$d=join('',@data);
$d=~ s/\r//g;
open(HANDLE, ">".$path."Cs_All_$s.dxf");
print HANDLE $d;
close(HANDLE);   
### ocad parser#############
 
### dxf -tiedoston purku
if ((-e "".$path."Cs_All_$s.dxf") eq "1") {
open (SIS,"<".$path."Cs_All_$s.dxf");
@rastikanta=<SIS>;
close (SIS); 
$apu=join('',@rastikanta);
$apu =~ s/\r//g;
@rastikanta = split(/\n/,$apu);
$apu="";
$i=0;
foreach $rec (@rastikanta){
chomp($rec);
if($rec eq "TEXT"){
$i++;    
$vaihe=1;
}
if($apu eq "1" && $vaihe==1){
$rastix[$i]=$rec;
$apu="";                  
$vaihe=2;
}
if($apu eq "2"  && $vaihe==2){
$rastiy[$i]=$rec;
$apu="";     
$vaihe=3;
} 
if($apu eq "3"  && $vaihe==3){
$rastikoodi[$i]=$rec;
$apu=""; 
$vaihe=0;
if($rec =~ /[^0-9]/){
$rastiy[$i]=$rastiy[$i]-0.7;
$rastix[$i]=$rastix[$i]-0.7;
}
}
if($rec eq " 10"){
$apu="1";
}
 
if($rec eq " 20"){
$apu="2";
}        
if($rec eq "  1"){
$apu="3";
}
}
print "<p><b>Maastopisteet:</b><br>";
open (HANDLE,">".$path."rastikanta_$uusid.txt");
for($j=1;$j<$i+1;$j++){
print $rastikoodi[$j]." ";
print HANDLE "$rastikoodi[$j]|$rastix[$j]|$rastiy[$j]\n";
}
close(HANDLE);

## skaalataan rastit 0-1000 -alueelle
open (HANDLE,"<".$path."rastikanta_$uusid.txt");
@rastit=<HANDLE>;
close (HANDLE);
 
$xmax=-999999999;
$xmin=999999999;
$ymax=-999999999;
$ymin=999999999;

foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($xx<$xmin){$xmin=$xx;}
if($yy<$ymin){$ymin=$yy;}
if($xx>$xmax){$xmax=$xx;}
if($yy>$ymax){$ymax=$yy;}
}
if($xmax==$xmin && $ymax==$ymin){
$xmax++;
$ymax++;
$samassapisteessa=1;
}
## skaalauskessoin
$k=150/($xmax-$xmin);
$k2=150/($ymax-$ymin); 
if($k2<$k){$k=$k2;}

$siirtyma_x=-$xmin;
$siirtyma_y=-$ymax;
                                                 
# tallennetaan skaalatut tiedot
open (HANDLE,">".$path."rastikanta_$uusid.txt");
foreach $rec (@rastit){
chomp($rec);
($kod,$xx,$yy)=split(/\|/,$rec);
if($samassapisteessa==1){
$xx++;
$yy++;
$samassapisteessa=0;
}
$x=($xx+$siirtyma_x)*$k+25;
$y=($yy+$siirtyma_y)*$k+25;
print HANDLE "$kod|$x|$y\n";
} 
close (HANDLE);
# valmis

if ((-e "".$path."Courses_$s.txt") eq "1") {

print "<p><b>Radat:</b><br>";

open (SIS,"<".$path."Courses_$s.txt");
@ratakanta=<SIS>;
close (SIS); 
if($in{'owncourses'} !=1){
open (HANDLE,">".$path."ratakanta_$uusid.txt");
}
foreach $rec (@ratakanta){
chomp($rec);
@rata=split(/\;/,$rec);
$i=0;       
print $rata[1]." ";
if($in{'owncourses'} !=1){
print  HANDLE $rata[1]."|".$rata[0]."|".$rata[5]."|".$rata[$#rata];
}
foreach $rec2 (@rata){
$i++;
chomp($rec2);
if($i>7 && $i%2==0 && $i< $#rata){
if($in{'owncourses'} !=1){
print HANDLE "|".$rec2;   
}   
}
}
if($in{'owncourses'} !=1){
print HANDLE "\n";
}
}  
if($in{'owncourses'} !=1){
close HANDLE;
}
}else{
if($in{'owncourses'} !=1){
print "Courses.txt is missing!";
exit; 
}
}

}else{    

}
}

if($in{'coursetype'} ne "3"){ # no course setting

if($in{'owncourses'}==1){# relay or point-o
$kisatyyppi=4;
}

print "<p><b>OK.</b><p>Next <a href=../reitti.".$extension."?kohdistus=1&owncourses=&id=$uusid&eventtype=$kisatyyppi&act=map&keksi=$in{'keksi'}>Adjust controls on the map</a>";
}else{
print "<p><b>OK.</b><p>Next <a href=../reitti.".$extension."?piirrarastit=1&id=$uusid&eventtype=$kisatyyppi&act=map&keksi=$in{'keksi'}>Draw controls on map</a>";
}
unlink $path."radat_$s.xml";
unlink $path."emitajat_$s.xml";
unlink $path."Courses_$s.txt";
unlink $path."Cs_All_$s.dxf";
exit;
}




sub haevaliajat_pirila{ 
## valiajat muuttujaan $valiaika[kilpailijannro][rasti]
$v1=0;$v2=0;$rasti=1;
#print "Valiajat: ";

while(index($valiajat,'<ControlOrder>'.$rasti.'</ControlOrder>',$v2)>0){

if($in{'normalize'}==1){
$v1=index($valiajat,'<CCode>',$v2);
$v2=index($valiajat,'</CCode>',$v1);
$kooditonormalize[$kilpailijannro-1].='|'.substr($valiajat,$v1+7,$v2-$v1-7);
}
$v1=index($valiajat,'<CTSecs>',$v2);
$v2=index($valiajat,'</CTSecs>',$v1);
$valiaika[$kilpailijannro-1][$rasti]=substr($valiajat,$v1+8,$v2-$v1-8);

#print $valiaika[$kilpailijannro-1][$rasti]." ";
$rasti++;
}

## koodit talteen
$koodilista='';
$v1=0;$v2=0;$rasti=1;
while(index($valiajat,"<CCode>",$v2)>0){
$v1=index($valiajat,"<CCode>",$v2);
$v2=index($valiajat,"</CCode>",$v1);  
$koodilista.='|'.substr($valiajat,$v1+7,$v2-$v1-7);
$rasti++;                                    
}

##
if($erekoodi[$sarjanro-1] eq ""){
$erekoodi[$sarjanro-1]=$koodilista;
}

## perhoset
if($in{'owncourses'} ==1){

if($hajOlemassa{$koodilista} eq ''){
$hajont++;
$hajOlemassa{$koodilista}=$hajont;

$hcodes=$koodilista;

print HANDLE5 "$hajont|$sarja[$kilpailijannro-1] $kilpailija[$kilpailijannro-1]|START|FINISH"."$hcodes\n"; 
$hcodes=~s/\|/\_/g; 
print HANDLE4 "$hajont|$sarja[$kilpailijannro-1] $kilpailija[$kilpailijannro-1]"."|$hcodes\n";  
}
$hhajonta[$kilpailijannro-1]=$hajOlemassa{$koodilista};
}

#print "\n";
}

sub haekilpailija_pirila { 
## kilpailijan tiedot muuttujiin 
## $kilpailija[kilpailijannro], $aika[kilpailijannro], $sarja[kilpailijannro], kilpailijan valiajajat muuttujaan $valiajat;

# seuraavan kilpailijan blokki
$s1=index($sarja,'<Competitor>',$s2);
$s2=index($sarja,'</Competitor>',$s1);
if($s1 == -1){
$loppu=1;
}else{
$kilpailija=substr($sarja,$s1+11,$s2-$s1-11);

# nimi
$apu1=index($kilpailija,'<Name>',0);
$apu2=index($kilpailija,'</Name>',0);
$apunimi=substr($kilpailija,$apu1+6,$apu2-$apu1-6);

$apunimi =~ s/<Family>//;
$apunimi =~ s/<\/Family>//;
$apunimi =~ s/<Given>//;
$apunimi =~ s/<\/Given>//;
$apunimi =~ s/\n/ /g;
if(substr($apunimi,0,1) eq " "){
$apunimi=substr($apunimi,1,length($apunimi)-1);
}
if(substr($apunimi,length($apunimi)-1,1) eq " "){
$apunimi=substr($apunimi,0,length($apunimi)-1);
}
$kilpailija[$kilpailijannro]=$apunimi;
# lahtoaika
($pois,$tmpl)=split(/<StartTime>/,$kilpailija,2);
($tmpl,$pois)=split(/</,$tmpl,2);
($s_ere,$m_ere,$h_ere)=reverse(split(/\:/,$tmpl));


$laika[$kilpailijannro]=60*60*$h_ere+60*$m_ere+$s_ere;
# sija
$apu1=index($kilpailija,'<Rank>',0);
$apu2=index($kilpailija,'</Rank>',0);
if($apu1>0){
$sija[$kilpailijannro]=substr($kilpailija,$apu1+6,$apu2-$apu1-6);
}
# tulos
$apu1=index($kilpailija,'<Time>',0);
$apu2=index($kilpailija,'</Time>',0);
if($apu1 == -1){
$apu1=index($kilpailija,'<Status>',0);
$apu2=index($kilpailija,'</Status>',0);
$tulos[$kilpailijannro]=substr($kilpailija,$apu1+8,$apu2-$apu1-8);
}else{
$tulos[$kilpailijannro]=substr($kilpailija,$apu1+6,$apu2-$apu1-6);
}
## aika sekunteina
$apu1=index($kilpailija,'<TSecs>',0);
$apu2=index($kilpailija,'</TSecs>',0);
if($apu1 == -1){
$apu1=index($kilpailija,'<Status>',0);
$apu2=index($kilpailija,'</Status>',0);
$aika[$kilpailijannro]=substr($kilpailija,$apu1+8,$apu2-$apu1-8);
}else{
$aika[$kilpailijannro]=substr($kilpailija,$apu1+7,$apu2-$apu1-7);
}

# sarja
$sarja[$kilpailijannro]=$sarjat[$sarjanro-1];
$sarjanro[$kilpailijannro]=$sarjanro-1;
# väliaikablokki
$apu1=index($kilpailija,'<SplitTimes>',0);
$apu2=index($kilpailija,'</SplitTimes>',0);
$valiajat=substr($kilpailija,$apu1+12,$apu2-$apu1-12);

$kilpailijannro++;
}
}

sub haesarja_pirila  { 
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja
$s1=0;$s2=0;
$i1=index($emitajat,'<EventClass>',$i2);
$i2=index($emitajat,'</EventClass>',$i1);
if($i1==-1){
$sarjaloppu=1;
}else{
$sarja=substr($emitajat,$i1+12,$i2-$i1-12);

$apu1=index($sarja,'<ClassName>',0);
$apu2=index($sarja,'</ClassName>',0);

$sarjat[$sarjanro]=substr($sarja,$apu1+11,$apu2-$apu1-11);
$sarjanro++;
}
}
## here is eTiming parsing functions




## tässä eresult xml-perkauksen vastaavaat


sub haevaliajat_eresults{ 
## valiajat muuttujaan $valiaika[kilpailijannro][rasti]

$v1=0;$v2=0;$rasti=1;
while(index($valiajat,"<SplitTime sequence=\"$rasti\"",$v2)>-1){
$v2=index($valiajat,"<SplitTime sequence=\"$rasti\"",$v2);
$v1=index($valiajat,"<Time",$v2);
$v1=index($valiajat,">",$v1);
$v2=index($valiajat,'</Time>',$v1);
($s_ere,$m_ere,$h_ere)=reverse(split(/\:/,substr($valiajat,$v1+1,$v2-$v1-1)));
$valiaika[$kilpailijannro-1][$rasti]=60*60*$h_ere+60*$m_ere+$s_ere;
$rasti++;
}
#vielä koodit talteen
if($erekoodi[$sarjanro-1] eq ""){
$v1=0;$v2=0;$rasti=1;
while(index($valiajat,"<ControlCode>",$v2)>0){
$v1=index($valiajat,"<ControlCode>",$v2);
$v2=index($valiajat,"</ControlCode>",$v1);  
$erekoodi[$sarjanro-1]=$erekoodi[$sarjanro-1]."|".substr($valiajat,$v1+13,$v2-$v1-13);
$rasti++;                                    
}
}
}

sub haekilpailija_eresults { 
## kilpailijan tiedot muuttujiin 
## $kilpailija[kilpailijannro], $aika[kilpailijannro], $sarja[kilpailijannro], kilpailijan valiajajat muuttujaan $valiajat;

# seuraavan kilpailijan blokki
$s1=index($sarja,'<PersonResult>',$s2);
$s2=index($sarja,'</PersonResult>',$s1);
if($s1 == -1){
$loppu=1;
}else{
$kilpailija=substr($sarja,$s1+14,$s2-$s1-14);

# nimi
$apunimi=$kilpailija;

$apu1=index($apunimi,'<PersonName>',0);
$apu2=index($apunimi,'</PersonName>',0);
if($apu1 >-1 && $apu2>-1 && $apu2>$apu1){
$apunimi=substr($apunimi,$apu1+12,$apu2-$apu1-12);
}

$apu1=index($apunimi,'<Person ',0);
$apu2=index($apunimi,'</Person>',$apu1);
if($apu1 >-1 && $apu2>-1 && $apu2>$apu1){
$apunimi=substr($apunimi,$apu1+7,$apu2-$apu1-7);
}

$apu1=index($apunimi,'<Name>',0);
$apu2=index($apunimi,'</Name>',0);
if($apu1 >-1 && $apu2>-1 && $apu2>$apu1){
$apunimi=substr($apunimi,$apu1+6,$apu2-$apu1-6);
}


$apunimi =~ s/<Family>/ /gi;
$apunimi =~ s/<\/Family>//gi;
$apunimi =~ s/<Given>/ /gi;
$apunimi =~ s/<\/Given>//gi;
$apunimi =~ s/<Given sequence=\"1\">/ /gi;
$apunimi =~ s/<Given sequence=\"2\">/ /gi;
$apunimi =~ s/<Given sequence=\"3\">/ /gi;
$apunimi =~ s/<Given sequence=\"4\">/ /gi;
$apunimi =~ s/<Given order=\"1\">/ /gi;
$apunimi =~ s/<Given order=\"2\">/ /gi;
$apunimi =~ s/<Given order=\"3\">/ /gi;
$apunimi =~ s/<Given order=\"4\">/ /gi;
$apunimi =~ s/ +/ /g;

$apunimi=&trim($apunimi);

$kilpailija[$kilpailijannro]=" ".$apunimi;
# seura
$apu1=index($kilpailija,'<Club>',0);
$apu2=index($kilpailija,'</Club>',0);
if($apu1 >-1){
$seura[$kilpailijannro]=substr($kilpailija,$apu1+6,$apu2-$apu1-6);
$seura[$kilpailijannro] =~ s/<Name>//;
$seura[$kilpailijannro] =~ s/<\/Name>//;
}else{ #etiming
($pois,$tseura)=split(/clubName/,$kilpailija);
($pois,$tseura,$pois)=split(/\"/,$kilpailija);
$seura[$kilpailijannro]=$tseura;
}
# tulos

$apu1=index($kilpailija,"<Time",0);
if($apu1 == -1){
$apu1=index($kilpailija,'<CompetitorStatus value=',0);
$apu2=index($kilpailija,"\"",$apu1+26);
if($apu2-$apu1 >0 && $apu2-$apu1 <7){
$tulos[$kilpailijannro]=substr($kilpailija,$apu1+25,$apu2-$apu1-25);
}
}else{
$apu1=index($kilpailija,">",$apu1);
$apu2=index($kilpailija,'</Time>',0);

$tulos[$kilpailijannro]=substr($kilpailija,$apu1+1,$apu2-$apu1-1);
}
## aika sekunteina
($s_ere,$m_ere,$h_ere)=reverse(split(/\:/,$tulos[$kilpailijannro]));
$aika[$kilpailijannro]=60*60*$h_ere+60*$m_ere+$s_ere;

## lahtoaika
if(index($kilpailija,'<StartTime>',0)>0){
$apu1=index($kilpailija,'<StartTime>',0);   
$apu2=index($kilpailija,'</StartTime>',0);
$laika[$kilpailijannro]=substr($kilpailija,$apu1+11,$apu2-$apu1-11);
($pois,$laika[$kilpailijannro])=split(/>/,$laika[$kilpailijannro],2);
($laika[$kilpailijannro],$pois)=split(/</,$laika[$kilpailijannro],2);


($s_ere,$m_ere,$h_ere)=reverse(split(/\:/,$laika[$kilpailijannro]));  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=$h_ere;
$h_ere=0;
}  

if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=0;
$h_ere=0;
}

$laika[$kilpailijannro]=60*60*$h_ere+60*$m_ere+$s_ere;
}else{

if(index($kilpailija,'<StartTime ',0)>0){
$apu1=index($kilpailija,'<StartTime ',0);
$apu1=index($kilpailija,'>',$apu1+3);
$apu2=index($kilpailija,'<',$apu1);
($s_ere,$m_ere,$h_ere)=reverse(split(/\:/,substr($kilpailija,$apu1+1,$apu2-$apu1-1)));
$laika[$kilpailijannro]=60*60*$h_ere+60*$m_ere+$s_ere;
}
}

# sarja
$sarja[$kilpailijannro]=$sarjat[$sarjanro-1];
$sarjanro[$kilpailijannro]=$sarjanro-1;
# väliaikablokki
#$apu1=index($kilpailija,'<SplitTimes>',0);
#$apu2=index($kilpailija,'</SplitTimes>',0);
#$valiajat=substr($kilpailija,$apu1+12,$apu2-$apu1-12);
$valiajat=$kilpailija;
$kilpailijannro++;
}
}

sub haesarja_eresults  { 
## sarjan nimi muuttujaan $sarjat[sarjanro] sisältö muuttujaan $sarja
$s1=0;$s2=0;
$i1=index($emitajat,'<ClassResult>',$i2);
$i2=index($emitajat,'</ClassResult>',$i1);
if($i1==-1){
$sarjaloppu=1;
}else{
$sarja=substr($emitajat,$i1+13,$i2-$i1-13);

$apu1=index($sarja,'<ClassShortName>',0);
$apu2=index($sarja,'</ClassShortName>',0);

$sarjat[$sarjanro]=substr($sarja,$apu1+16,$apu2-$apu1-16);
$sarjanro++;
}
}


## eresultsin xml-perkaus

sub haerata{
$v1=index($radat,'<Course>',$v2);
$v2=index($radat,'</Course>',$v1);
if($v1<0){
$loppu=1;
$rata="";
}else{
$rata=substr($radat,$v1+8,$v2-$v1-8);
$ratalkm++;
}
}

sub haef{
$v1_=index($rata,'<FinishPointCode>',$v2_);
$v2_=index($rata,'</FinishPointCode>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$fcode[$ratalkm]=substr($rata,$v1_+17,$v2_-$v1_-17);
$fcode[$ratalkm] =~ s/ //g;
}
}

sub haes{
$v1_=index($rata,'<StartPointCode>',$v2_);
$v2_=index($rata,'</StartPointCode>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$scode[$ratalkm]=substr($rata,$v1_+16,$v2_-$v1_-16);
$scode[$ratalkm] =~ s/ //g;
}
}
sub haename{
$v1_=index($rata,'<CourseName>',$v2_);
$v2_=index($rata,'</CourseName>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$rname[$ratalkm]=substr($rata,$v1_+12,$v2_-$v1_-12);
}  
while(index($rata,'<ClassShortName>',$v2_)>0){
$v1_=index($rata,'<ClassShortName>',$v2_);
$v2_=index($rata,'</ClassShortName>',$v1_);
$rname[$ratalkm]=$rname[$ratalkm]." ".substr($rata,$v1_+16,$v2_-$v1_-16);
}
}
sub haeid{
$v1_=index($rata,'<CourseId>',$v2_);
$v2_=index($rata,'</CourseId>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$rid[$ratalkm]=substr($rata,$v1_+10,$v2_-$v1_-10);
$rid[$ratalkm] =~ s/ //g;
}
}
sub haesarjat{
$v1_=index($rata,'<ClassShortName>',$v2_);
$v2_=index($rata,'</ClassShortName>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$rsarj[$ratalkm]=substr($rata,$v1_+16,$v2_-$v1_-16);
$rsarj[$ratalkm] =~ s/ //g;
}
}
sub haec{
$v1_=index($rata,'<CourseControl>',$v2_);
$v2_=index($rata,'</CourseControl>',$v1_);
if($v1_<0){
$loppu_=1;
}else{
$apu=substr($rata,$v1_+15,$v2_-$v1_-15);
$clkm++;

$a1=index($apu,'<ControlCode>',0);
$a2=index($apu,'</ControlCode>',0);
$ccode[$ratalkm][$clkm]=substr($apu,$a1+13,$a2-$a1-13);
$ccode[$ratalkm][$clkm] =~ s/ //g;

}
}

sub haemaali{
$v1=index($radat,'<FinishPoint>',$v2);
$v2=index($radat,'</FinishPoint>',$v1);
if($v1<0){
$loppu=1;
}else{
$apu=substr($radat,$v1+13,$v2-$v1-13);
$maalilkm++;

$a1=index($apu,'<FinishPointCode>',0);
$a2=index($apu,'</FinishPointCode>',0);
$fcode[$maalilkm]=substr($apu,$a1+17,$a2-$a1-17);
$fcode[$maalilkm] =~ s/\"//g;
$fcode[$maalilkm] =~ s/ //g;
$a1=index($apu,"x=\"",0);
$a2=index($apu,"\"",$a1+4);
$f_x[$maalilkm]=substr($apu,$a1+2,$a2-$a1-1);
$f_x[$maalilkm] =~ s/\"//g;
$f_x[$maalilkm] =~ s/ //g;
$a1=index($apu,"y=\"",0);
$a2=index($apu,"\"",$a1+4);
$f_y[$maalilkm]=substr($apu,$a1+2,$a2-$a1-1);
$f_y[$maalilkm] =~ s/\"//g;
$f_y[$maalilkm] =~ s/ //g;
}
}

sub haelahto{
$v1=index($radat,'<StartPoint>',$v2);
$v2=index($radat,'</StartPoint>',$v1);
if($v1<0){
$loppu=1;
}else{
$apu=substr($radat,$v1+12,$v2-$v1-12);
$lahtolkm++;

$a1=index($apu,'<StartPointCode>',0);
$a2=index($apu,'</StartPointCode>',0);
$startcode[$lahtolkm]=substr($apu,$a1+16,$a2-$a1-16);
$startcode[$lahtolkm] =~ s/\"//g;
$startcode[$lahtolkm] =~ s/ //g;
$a1=index($apu,"x=\"",0);
$a2=index($apu,"\"",$a1+4);
$start_x[$lahtolkm]=substr($apu,$a1+2,$a2-$a1-1);
$start_x[$lahtolkm] =~ s/\"//g;
$start_x[$lahtolkm] =~ s/ //g;
$a1=index($apu,"y=\"",0);
$a2=index($apu,"\"",$a1+4);
$start_y[$lahtolkm]=substr($apu,$a1+2,$a2-$a1-1);
$start_y[$lahtolkm] =~ s/\"//g;
$start_y[$lahtolkm] =~ s/ //g;
}
}

sub haerasti{
$v1=index($radat,'<Control>',$v2);
$v2=index($radat,'</Control>',$v1);
if($v1<0){
$loppu=1;
}else{
$apu=substr($radat,$v1+9,$v2-$v1-9);
$rastilkm++;

$a1=index($apu,'<ControlCode>',0);
$a2=index($apu,'</ControlCode>',0);
$rasticode[$rastilkm]=substr($apu,$a1+13,$a2-$a1-13);
$rasticode[$rastilkm] =~ s/\"//g;
$rasticode[$rastilkm] =~ s/ //g;
$a1=index($apu,"x=\"",0);
$a2=index($apu,"\"",$a1+4);
$rasti_x[$rastilkm]=substr($apu,$a1+2,$a2-$a1-1);
$rasti_x[$rastilkm] =~ s/\"//g;
$rasti_x[$rastilkm] =~ s/ //g;
$a1=index($apu,"y=\"",0);
$a2=index($apu,"\"",$a1+4);
$rasti_y[$rastilkm]=substr($apu,$a1+2,$a2-$a1-1);
$rasti_y[$rastilkm] =~ s/\"//g;
$rasti_y[$rastilkm] =~ s/ //g;
}
}
             
##############################################

sub SISPLITS{


if($in{'ftp'} ne "1"){

$file = $q->param("tulosxml");
@data=<$file>;
close($file); 

}else{
open (HANDLE2,"<$path"."results.txt");  
@data=<HANDLE2>;
close(HANDLE2); 
}

$i=0;
foreach $rec (@data){
$i++;
chomp($rec);
$rec=~ s/\r//g;

if($i==1){
$delim=(scalar(split(/\,/,$rec)) > scalar(split(/\;/,$rec)))?',':';'; 

#############################################################################################
## This SI CSV column index reading system has been shamelessly copied from splitbroser   ###
## source code.                         http://www.splitsbrowser.org.uk                   ###
#############################################################################################

		$SIVer=0;
		 if((index($rec,'First name') != -1) || 
			(index($rec,'Förnamn') != -1) ||
			(index($rec,'Prénom') != -1) ||
                        (index($rec,'Nome') != -1) ||
                        (index($rec,'Jméno (kuest.)') != -1) ||
                        (index($rec,'Utónév') != -1) ||
                        (index($rec,'Fornavn') != -1) || 
                        (index($rec,'Imiz') != -1) ||
                        (index($rec,'Ime') != -1) || 
                        (index($rec,'Nombre') != -1) || 
                        (index($rec,'Vorname') != -1) ){
                             $SIVer=1;
			}

                if ($SIVer==1) { 
                        $NAME_INDEX = 3; 
                        $START_TIME_INDEX = 9; 
                        $TOTAL_TIME_INDEX = 11; 
                        $CLUB_INDEX = 15; 
                        $CLASS_INDEX = 18; 
                        $COURSE_INDEX = 39; 
                        $DISTANCE_INDEX = 40; 
                        $CLIMB_INDEX = 41; 
                        $NUM_CONTROLS_INDEX = 42; 
                        $START_PUNCH_INDEX = 44; 
                        $FIRST_SPLIT_INDEX = 47; 
                        $FIRSTNAME_INDEX = 4; 
                        
                        $INDEX_STEP=2;
                        $CODE_STEP=-1;
                } else { 
                        $NAME_INDEX = 3; 
                        $START_TIME_INDEX = 7; 
                        $TOTAL_TIME_INDEX = 9; 
                        $CLUB_INDEX = 13; 
                        $CLASS_INDEX = 16; 
                        $COURSE_INDEX = 37; 
                        $DISTANCE_INDEX = 38; 
                        $CLIMB_INDEX = 39; 
                        $NUM_CONTROLS_INDEX = 40; 
                        $START_PUNCH_INDEX = 42; 
                        $FIRST_SPLIT_INDEX = 44; 
                        
                        $INDEX_STEP=2;
                        $CODE_STEP=-1;
                     } 


 if(index($rec,'Course') != -1){
 @row=split(/${delim}/,$rec);
$j=0;
foreach $rec2 (@row){
chomp($rec2); 
$field{$rec2}=$j;
$j++;
}  

                        $NAME_INDEX = $field{'Surname'};
                        $FIRSTNAME_INDEX = $field{'First name'};
                        $START_TIME_INDEX =$field{'Surname'};
                        $TOTAL_TIME_INDEX = $field{'Time'};
                        $CLASS_INDEX = $field{'Long'};
                        $COURSE_INDEX = $field{'Course'};

                        $START_PUNCH_INDEX= $field{'Start'}; 
                        $FIRST_SPLIT_INDEX = $field{'Punch1'};
                        $SECOND_SPLIT_INDEX = $field{'Punch2'};
                        $FIRST_CODE_INDEX = $field{'Control1'};
                        
                        $INDEX_STEP=$SECOND_SPLIT_INDEX-$FIRST_SPLIT_INDEX;
                        $CODE_STEP=$FIRST_CODE_INDEX-$FIRST_SPLIT_INDEX;                        
                               
                } 

$COURSE_IND=$COURSE_INDEX;
if($in{'classify'}==1){
$COURSE_INDEX=$CLASS_INDEX;
}
}

 $DATABASE_INDEX = $field{'Database Id'};
 $STNO_INDEX = $field{'Stno'};

## poistetaan lainausmerkkien sisällä olevat välimerkit
@d=split(/\"/,$rec);
$j=0;
foreach $re (@d){
$j++;
if($j%2==0){
$re =~ s/${delim}/ /g;
}
}
$rec=join('',@d);

$out.=$rec;
if($rec ne''){
if(substr($rec,length($rec)-1,1) eq $delim || substr($rec,length($rec)-3,3) eq '...'   || substr($rec,length($rec)-15,15) eq 'Course controls'){
$out.="\n";
}
}
}


open(HANDLE, ">".$path."emitajat_$s.xml");
print HANDLE $out;
close(HANDLE); 


if($in{'act'} ne 'updatesplits'){
open (HANDLE1,">".$path."sarjakanta_$uusid.txt");
open (HANDLE2,">".$path."kilpailijat_$uusid.txt");
open (HANDLE,">".$path."ratakanta_$uusid.txt");  

open (HANDLE4,">".$path."hajontakanta_$uusid.txt");

open (HANDLE3,">".$path."sarjojenkoodit_$uusid.txt");
}## if not update


open (SIS,"<".$path."emitajat_$s.xml");
@emitajat=<SIS>;
close (SIS); 



$i=0;
foreach $rec (@emitajat){
chomp($rec); 
$i++;
$rec =~s/\"//g;


@row=split(/${delim}/,$rec);

if($i>1){

## class
if($SIclass{$row[$COURSE_INDEX]} eq '' && $in{'act'} ne 'updatesplits'){
$coursenro++;
$newcourse=1;
$SIclass{$row[$COURSE_INDEX]}=$coursenro;
print HANDLE1 "$coursenro|$row[$COURSE_INDEX]\n";
if($in{'owncourses'} == 0){
print HANDLE "$coursenro|$row[$COURSE_INDEX]|START|FINISH";
}
print HANDLE3 "$coursenro|START";
}


## start time
$start="";
($h_ere,$m_ere,$s_ere)=split(/\:/,$row[$START_PUNCH_INDEX]);
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=$h_ere;
$h_ere=0;
}  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=0;
$h_ere=0;
}
$start=60*60*$h_ere+60*$m_ere+$s_ere;

$result=$row[$TOTAL_TIME_INDEX];
if(index($rec,'-----')>-1){ ## if a puch is missing
$result="DNF ($row[$TOTAL_TIME_INDEX])";
}
if($SIVer == 1){
$competitorname=$row[$FIRSTNAME_INDEX].' '.$row[$NAME_INDEX]; 
}else{
$competitorname=$row[$NAME_INDEX];
}

$splitupdateid=''.$row[$DATABASE_INDEX].'_'.$row[$STNO_INDEX].'_'.$competitorname;

$out1= "$i|$SIclass{$row[$COURSE_INDEX]}|$row[$COURSE_INDEX]|$competitorname|$start|$splitupdateid|";
$out2= "|$result|";
$valiaika_edellinen=-99999;
$codes='';  
$isdnf=0;

if($INDEX_STEP>0 && $FIRST_SPLIT_INDEX>0 ){

for($j=$FIRST_SPLIT_INDEX;$j<$#row+1;$j=$j+$INDEX_STEP){                        
 
if($row[$j] eq '-----'){$isdnf=1;}
($h_ere,$m_ere,$s_ere)=split(/\:/,$row[$j]);  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=$h_ere;
$h_ere=0;
}  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=0;
$h_ere=0;
}
$valiaika=60*60*$h_ere+60*$m_ere+$s_ere;
if($valiaika_edellinen-1<$valiaika && $isdnf==0){
$out2.= "$valiaika;";       
$valiaika_edellinen=$valiaika;
$codes=$codes.'|'.$row[$j+$CODE_STEP]; 
}
}
}
## vielä maaliaika
($h_ere,$m_ere,$s_ere)=split(/\:/,$row[$TOTAL_TIME_INDEX]);  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=$h_ere;
$h_ere=0;
}  
if($s_ere eq ""){
$s_ere=$m_ere;
$m_ere=0;
$h_ere=0;
}
$valiaika=60*60*$h_ere+60*$m_ere+$s_ere;
if($isdnf==0){
$out2.= $valiaika;
}

if($in{'act'} ne 'updatesplits'){
if($in{'owncourses'} ==1){
if($hajOlemassa{$codes} eq''){
$hajont++;
$hajOlemassa{$codes}=$hajont;
$hajontakant[$hajont]=$codes;
($pois,$hcodes)=split(/\|/,$codes,2);
$hcodes=~s/\|/\_/g;
print HANDLE4 "$hajont|$row[$COURSE_INDEX] $competitorname"."|$hcodes\n";  
print HANDLE "$hajont|$row[$COURSE_INDEX] $competitorname|START|FINISH"."$codes\n";  
}
$klhajont=$hajOlemassa{$codes};
}

if($in{'owncourses'} == 2){

if($hajOlemassa{$row[$COURSE_IND]} eq''){
$hajont++;
$hajOlemassa{$row[$COURSE_IND]}=$hajont;
$hajontakant[$hajont]=$row[$COURSE_IND];

print HANDLE4 "$hajont|$row[$COURSE_IND]"."|\n";  
}
$klhajont=$hajOlemassa{$row[$COURSE_IND]};
}
}

if($in{'act'} eq 'updatesplits'){
$UPD_START{$splitupdateid}=$start;
$UPD_SPLITS{$splitupdateid}=$out2;
}

if($in{'act'} ne 'updatesplits'){
print HANDLE2 $out1.$klhajont.$out2."\n";  
if($newcourse==1){
if($in{'owncourses'} !=1){
print HANDLE "$codes\n";  
}
print HANDLE3 "$codes|FINISH\n";  
$newcourse=0;
}
}
}
}

}
           
                                                               
##############
#############################################################                                                               
sub getElement{
$element=$_[0];
$start=$_[1];
$stop=$_[2];
$position=$_[3];
$i1_temp=index($element,$start,$position);
$i2_temp=index($element,$stop,$i1_temp);         
if($i1_temp==-1 || $i2_temp==-1){
return ("",-1);
}
$temp=substr($element,$i1_temp,($i2_temp-$i1_temp)+length($stop));
return ($temp,$i2_temp);
}

sub getElementValue{
$element=$_[0];

$temp=substr($element,index($element,'>')+1,rindex($element,'<')-index($element,'>')-1);
}

sub getElementParameters{
$element=$_[0];
#$element=substr($element,0,index($element,'>'));
#print "##$element##\n";
$temp=substr($element,index($element,' ')+1,index($element,'>')-index($element,' ')-1);
print "##$temp##\n";
@temp=split(/\=/,$temp);

$temp="";
$i_temp=0;
foreach $rec (@temp){
$temp_name[$i_temp+1]=substr($rec,rindex($rec,' ')+1);
$temp_value[$i_temp]=substr($rec,0,rindex($rec,' '));
if(rindex($rec,' ')<0){
$temp_value[$i_temp]=$rec;
}
$temp_value[$i_temp] =~ s/\"//g;
$temp_value[$i_temp] =~ s/\'//g;

if($i_temp>0){
$temp=$temp.$temp_name[$i_temp]."=".$temp_value[$i_temp].'&';
$tmp{$temp_name[$i_temp]}=$temp_value[$i_temp];
}else{
$temp_name[$i_temp+1]=$rec;
}
$i_temp++;

}

return %tmp;
}                                                                           
            
sub trim($)
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
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
sub unlock_file {
if($locking eq '1'){
flock(HANDLE,LOCK_UN);
}
}

sub tyyli {
print "
input.radi{COLOR: #000000; background-color: #A0A0A0; border-width:1px; border-style:outline;  FONT-FAMILY: Verdana, Arial, Helvetica; FONT-SIZE: 11px; FONT-WEIGHT: normal; }
input {COLOR: #000000; background-color: #FFFFFF; border-color:#FFFFFF;  border-width:1px; border-style:outline;  FONT-FAMILY: Verdana, Arial, Helvetica; FONT-SIZE: 11px; FONT-WEIGHT: normal; }
body{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
td{font-family: Verdana, Arial, Helvetica, sans-serif; color: #000000; font-size: 11px; }
H3{ font-family: Verdana, Arial, Helvetica, sans-serif; color: #005578; font-size: 12px; font-weight : bold; }
";
}

#### IOF3 to pirila conversion ###################3

sub iof3topirila{

$emitajat=~ s/<PersonResult>/<Competitor>/g;
$emitajat=~ s/<\/PersonResult>/<\/Competitor>/g;

@vsarjat=split(/<\/ClassResult>/,$emitajat);

foreach $vsarja (@vsarjat){

if($vsarja =~ /<Competitor>/){

@vd=split(/<Competitor>/,$vsarja);

foreach $vrec (@vd){
$vl++;
if($vrec=~ /<Person>/){

if($vrec =~ /<Organisation>/){
$vrec=~ s/<\/Organisation>/<Organisation>/g;
($va,$vb,$vc)=split(/<Organisation>/,$vrec,3);
$vrec=$va.$vc;
}

$vrec=~ s/<Result>//g;
$vrec=~ s/<\/Result>//g;

#starttime
$vq=$vrec;
$vq=~ /<StartTime>(.*?)<\/StartTime>/ig;
($vday,$vtime)=split(/T/,$1);
($vtime,$vzone)=split(/\-/,$vtime);
($vtime,$vzone)=split(/\+-/,$vtime);
($vs,$vm,$vh)=reverse(split(/\:/,$vaika));

$vt=$vs+60*$vm+60*60+$vh;
$vstart='<StartTime>'.$vt.'</StartTime>';
$vrec=~ s/StartTime/STime/g;

#time
$vrec=~ s/<Time>/<TSecs>/g;
$vrec=~ s/<\/Time>/<\/TSecs>/g;

$vrec=~ /<TSecs>(.*?)<\/TSecs>/ig;

$vlastsplit=$1;

$vh=floor($1/60/60);
$vm=floor(($1-$vh*60*60)/60);
$vs=$1-$vm*60-$vh*60*60;

$vresult="\n".$vstart."\n".'<Time>'."$vh:$vm:$vs".'</Time>';
# controls
$vrec=~ s/ status="Missing"//g;

if($vrec =~ /<SplitTime>/){

($valku,$vsplits)=split(/<SplitTime>/,$vrec,2);
@vcontrols=split(/<SplitTime>/,$vsplits);
$vi=0;$vorder=0;
foreach $vc (@vcontrols){
$vi++;
$vrest='';

if($vc =~ /<\/SplitTime>/){
$vorder++;
($vc,$vrest)=split(/<\/SplitTime>/,$vc,2);

$vc=~s/ControlCode/CCode/g;
$vc=~ s/<TSecs>/<CTSecs>/g;
$vc=~ s/<\/TSecs>/<\/CTSecs>/g;

$vc=~ s/<\/SplitTime>/<\/Control>/g;

$vc="<Control><ControlOrder>$vi</ControlOrder>".$vc;

$vc.='</Control>';
}
$vc=~ s/<\/Competitor>//g;
}

$vorder++;
$vlplit="<Control>
<ControlOrder>$vorder</ControlOrder>
<CCode>F</CCode>
<CTSecs>$vlastsplit</CTSecs>
</Control>";

$vrec=$valku.$vresult.'<SplitTimes>'.join('',@vcontrols).$vlplit.'</SplitTimes>'.$vrest;
}
}
}

$vsarja=join('<Competitor>',@vd);

}
}
$emitajat= join('</ClassResult>',@vsarjat);


@vclasses=split(/<\/ClassResult>/,$emitajat);

foreach $vclass (@vclasses){
if($vclass =~ /<Class>/){
($valku,$vloppu)=split(/<\/Class>/,$vclass ,2);
$valku=~ s/<Name>/<ClassShortName>/;
$valku=~ s/<\/Name>/<\/ClassShortName>/;
$valku=~ /<ClassShortName>(.*?)<\/ClassShortName>/ig;
$valku.="<ClassName>$1</ClassName>";
$vclass=$valku.'</Class>'.$vloppu;


}
}
$emitajat=join('</ClassResult>',@vclasses);

## classnames

$emitajat=~ s/ClassResult/EventClass/g;

$emitajat=~ s/\r/\n/g;
$emitajat=~ s/\n+/\n/g;

return 1;
}

##################################################################
sub getOptVal {
##################################################################
     my ($set, $opt) = @_;
     while($set =~ /(?:^|\,)([A-Z])(.*?)(?=\,[A-Z]\,|\,[A-Z]$|$)/g){
  my $a = $1;
  my $b = $2;
  if($opt eq $a){
      $b =~ s/^\,//;
      return $b;
  }
     }
     return undef;
}