<?php
/* Redownloads all of a wordpress sites themes */

include_once("wp-load.php");
include_once("wp-admin/includes/admin.php");
include_once("wp-admin/includes/class-wp-upgrader.php");

$themes = wp_get_themes();
$current = get_site_transient('update_themes');
$upgrader = new WP_Upgrader();

foreach($themes as $plugin_dir => $plugin_details) {
	if( isset($current->response[$plugin_dir]) ) {

		$upgrader->run( array(
			'package' => $r['package'],
			'destination' => get_theme_root( $theme ),
			'clear_destination' => true,
			'clear_working' => true,
			'hook_extra' => array(
				'theme' => $theme,
				'type' => 'theme',
				'action' => 'update',
			),
		));

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
