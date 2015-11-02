<?php
/*
Redownloads and upgrades all of a wordpress sites plugins

from https://github.com/WordPress/WordPress/blob/master/wp-admin/includes/class-wp-upgrader.php#L998-L1032
*/

include_once("wp-load.php");
include_once("wp-admin/includes/admin.php");
include_once("wp-admin/includes/class-wp-upgrader.php");

$plugins = get_plugins();
$upgrader = new WP_Upgrader();

if( $argv[1] == 'all' ) {
	/*
	To retrieve fresh packages - use the wordpress update api

	https://github.com/WordPress/WordPress/blob/master/wp-includes/update.php#L280-L304
	*/

	$options = array(
		'body' => array( 'plugins' => wp_json_encode( compact('plugins') ) ),
		'user-agent' => 'WordPress/'.$wp_version.'; '. get_bloginfo( 'url' )
	);

	$url = 'https://api.wordpress.org/plugins/update-check/1.1/';
	$raw_response = wp_remote_post( $url, $options );
	$response = json_decode( wp_remote_retrieve_body( $raw_response ), true );
	$current = $response['plugins']
} else {
	$current = get_site_transient('update_plugins');
}

foreach($plugins as $plugin_dir => $plugin_details) {
	if( isset($current->response[$plugin_dir]) ) {

		$result = $upgrader->run( array(
			'package' => $current->response[$plugin_dir]->package,
			'destination' => WP_PLUGIN_DIR,
			'clear_destination' => true,
			'clear_working' => true,
			'hook_extra' => array( 'plugin' => $plugin_dir )
		));

		echo "Updated ".$plugin_dir;
	}

}

wp_clean_plugins_cache();

?>
