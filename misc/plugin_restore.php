<?php
/* Redownloads and upgrades all of a wordpress sites plugins */

include_once("wp-load.php");
include_once("wp-admin/includes/admin.php");
include_once("wp-admin/includes/class-wp-upgrader.php");
$plugins = get_plugins();
$current = get_site_transient('update_plugins');
$upgrader = new WP_Upgrader();

foreach($plugins as $plugin_dir => $plugin_details) {
	if( isset($current->response[$plugin_dir]) ) {
		$result = $upgrader->run( array(
			'package' => $current->response[$plugin_dir]->package,
			'destination' => WP_PLUGIN_DIR,
			'clear_destination' => true,
			'clear_working' => true,
			'hook_extra' => array('plugin' => $plugin_dir )
		));
		echo "Updated ".$plugin_dir;
	}
}


?>
