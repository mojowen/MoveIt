<?php

// Table prefix tripped me up here

echo 'starting';

$vals = array(
	'db_user' => '',
	'db_pass' => '',
	'db_name' => '',
	'db_host' => ''
);

$command = "mysql -u ".$vals['db_user']." -p".$vals['db_pass']." -h ".$vals['db_host']." -D ".$vals['db_name']." < db.sql";

$output = shell_exec($command );

echo $command;
echo $output;

?>