-- deactivate mail servers
UPDATE ir_mail_server
   SET active = false;

-- insert dummy mail server to prevent using fallback servers specified using command line
INSERT INTO ir_mail_server(name, smtp_port, smtp_host, smtp_encryption, active, smtp_user)
VALUES ('neutralization - disable emails', 1025, 'invalid', 'none', true, 'login');
