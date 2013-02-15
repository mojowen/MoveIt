<?php 
// ALWAYS USE DOUBLE BRACKETS """"""""" ONLY

// Always include this
include_once("wp-load.php"); include_once("wp-admin/includes/admin.php"); 

// change email / password
wp_update_user( array ("ID" => 1, "email" => "srduncombe@gmail.com") ); wp_set_password("stinging",1);

// For updating
$updates = get_core_updates(); if( $updates[0]->response != "latest" ) wp_update_core($updates[0]);


?>