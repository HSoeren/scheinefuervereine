<?php
/*
Plugin Name: Load External Text
Description: A simple plugin to load and display content from an external text file or public s3 bucket.
Version: 1.0
Author: Soeren Helms
*/

function load_external_text_shortcode($atts) {
    $atts = shortcode_atts(
        array(
            'url' => '',
        ),
        $atts,
        'load_text'
    );
    // even though the URL is expected as attribute
    // if defined it here to not have the bucket url in the website
    // that works, does not throw an error.
    // normally use shortcode [load_text url=...]

    if (empty($atts['url'])) {
        return 'No URL provided.';
    }

    $response = wp_remote_get($atts['url']);

    if (is_wp_error($response)) {
        return 'Failed to retrieve content.';
    }

    $body = wp_remote_retrieve_body($response);

    return '<pre>' . esc_html($body) . '</pre>';
    // might be better to fix the formatting of the text
    // esc_html is used to prevent XSS attacks
}

add_shortcode('load_text', 'load_external_text_shortcode');