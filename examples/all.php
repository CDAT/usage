<?php
   $link = mysql_connect($db_host, $db_user, $db_pass);
   if (!$link){
    die('Could not connect: ' . mysql_error());
  	echo 'Connection Failed';
  }
  //echo 'Connected Successfully <br/>';

	$db_selected = mysql_select_db($db_name, $link);
	if (!$db_selected) {
		die ('Can\'t use ' . $db_name . ' : ' . mysql_error());
	}
	//echo 'Using ' . $db_name;
	$getdata = mysql_query("select distinct machines.platform as name, count(*) as value from users, machines, access where users.machine = machines.id and access.user = users.id group by machines.platform;");

	$myFile = "data1.csv";
	$fh = fopen($myFile, 'w') or die("can't open file");
	$header = "name,value\n";
	fwrite($fh, $header);
	while($show = mysql_fetch_array($getdata)){
		$stringData =  $show[name] . "," . $show[value] . "\n"; 
		fwrite($fh, $stringData);
	}	
	
	fclose($fh);
	
	mysql_close($link); 
?>
