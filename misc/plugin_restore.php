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

	$active  = get_option( 'active_plugins', array() );

	$options = array(
		'body' => array(
			'plugins' => wp_json_encode( compact( 'plugins', 'active' ) ),
			'all' => wp_json_encode( true ),
		),
		'user-agent' => 'WordPress/'.$wp_version.'; '. get_bloginfo( 'url' )
	);

	$url = 'https://api.wordpress.org/plugins/update-check/1.1/';
	$raw_response = wp_remote_post( $url, $options );
	$response = json_decode( wp_remote_retrieve_body( $raw_response ), true );
	$current = array_merge($response['plugins'], $response['no_update']);
} else {
	$current = get_site_transient('update_plugins');
	$current = $current->response;
}

foreach($plugins as $plugin_dir => $plugin_details) {
	$plugin_directory = untrailingslashit(WP_PLUGIN_DIR .'/'. plugin_dir_path($plugin_dir));
	if( isset($current[$plugin_dir]) && ! is_link($plugin_directory) ) {
		$plugin = (object) $current[$plugin_dir];
		$result = $upgrader->run( array(
			'package' => $plugin->package,
			'destination' => WP_PLUGIN_DIR,
			'clear_destination' => true,
			'clear_working' => true,
			'hook_extra' => array( 'plugin' => $plugin_dir )
		));
		echo "Updated {$plugin_dir}\n";
	} else {
		$reason = is_link($plugin_directory) ? "it's a sym link" : "can't find source";
		echo "Skipping {$plugin_dir} - {$reason}\n";
	}

}

wp_clean_plugins_cache();

?>
