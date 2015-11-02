<?php

include_once("wp-load.php");
include_once("wp-admin/includes/admin.php");

$updates = get_core_updates();

if( $updates[0]->response != "latest" ) {
	wp_update_core($updates[0]);
}

?>
