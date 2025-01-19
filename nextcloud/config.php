<?php
$CONFIG = array (
  'htaccess.RewriteBase' => '/',
  'memcache.local' => '\\OC\\Memcache\\APCu',
  'apps_paths' =>
  array (
    0 =>
    array (
      'path' => '/var/www/html/apps',
      'url' => '/apps',
      'writable' => false,
    ),
    1 =>
    array (
      'path' => '/var/www/html/custom_apps',
      'url' => '/custom_apps',
      'writable' => true,
    ),
  ),
  'instanceid' => 'ocq1xjl0nh22',
  'passwordsalt' => '<value>',              # <-- should be auto set when created or set manually
  'secret' => '<value>',                    # <-- should be auto set when created or set manually
  'trusted_domains' =>
  array (
    0 => '192.168.0.102:8080',
    1 => 'nextcloud.lr-projects.de',
    2 => '10.217.236.3:8080',
    3 => 'localhost:8080',
    4 => 'nextcloud.thinkpad.lr-projects.de'
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '29.0.0.19',
  'trusted_proxies' =>
  array (
    0 => '10.217.236.1',
  ),
  'overwriteprotocol' => 'https',
  'overwritehost' => 'nextcloud.lr-projects.de',
  'overwrite.cli.url' => 'https://nextcloud.lr-projects.de/',
  'dbname' => 'nextcloud',
  'dbhost' => 'database',
  'dbport' => '',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'nextcloud',
  'dbpassword' => 'nextcloud',
  'installed' => true,
  'log_type' => 'file',
  'logfile' => 'nextcloud.log',
  'loglevel' => 3,
  'logdateformat' => 'F d, Y H:i:s',
  'maintenance' => false,
  'maintenance_window_start' => 1,
  'mail_smtpmode' => 'smtp',
  'mail_smtpauth' => 1,
  'mail_sendmailmode' => 'smtp',
  'mail_from_address' => 'lr.dev.projects',
  'mail_domain' => 'gmail.com',
  'mail_smtphost' => 'smtp.googlemail.com',
  'mail_smtpport' => '465',
  'mail_smtpsecure' => 'ssl',
  'mail_smtpname' => '<EMAIL_USERNAME>',                     # <-- TODO
  'mail_smtppassword' => '<EMAIL_PASSWORD>',                 # <-- TODO
);