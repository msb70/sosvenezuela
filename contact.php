<?php
/* Endpoint del formulario de contacto — SOS Venezuela (apoyo-fem-vzla.org) */
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo json_encode(['ok' => false, 'error' => 'method']);
  exit;
}

$nombre   = trim($_POST['nombre']   ?? '');
$apellido = trim($_POST['apellido'] ?? '');
$email    = trim($_POST['email']    ?? '');
$mensaje  = trim($_POST['mensaje']  ?? '');
$honeypot = trim($_POST['web']      ?? ''); // campo oculto: los humanos no lo llenan

/* Bots que llenan el honeypot: responder ok sin enviar nada */
if ($honeypot !== '') { echo json_encode(['ok' => true]); exit; }

if ($nombre === '' || $apellido === '' || $mensaje === ''
    || !filter_var($email, FILTER_VALIDATE_EMAIL)
    || mb_strlen($nombre) > 60 || mb_strlen($apellido) > 60
    || mb_strlen($email) > 120 || mb_strlen($mensaje) > 2000) {
  http_response_code(400);
  echo json_encode(['ok' => false, 'error' => 'datos']);
  exit;
}

$to      = 'contacto@apoyo-fem-vzla.org';
$subject = '=?UTF-8?B?' . base64_encode("Solicitud de información — SOS Venezuela ({$nombre} {$apellido})") . '?=';
$body    = "Nombre: {$nombre} {$apellido}\n"
         . "Correo de contacto: {$email}\n"
         . "Fecha: " . date('d/m/Y H:i:s') . " (hora del servidor)\n"
         . "IP: " . ($_SERVER['REMOTE_ADDR'] ?? 'n/d') . "\n\n"
         . "Solicitud:\n{$mensaje}\n\n"
         . "— Enviado desde el formulario de apoyo-fem-vzla.org";
$headers = "From: SOS Venezuela <no-reply@apoyo-fem-vzla.org>\r\n"
         . "Reply-To: {$email}\r\n"
         . "MIME-Version: 1.0\r\n"
         . "Content-Type: text/plain; charset=UTF-8\r\n"
         . "Content-Transfer-Encoding: 8bit";

$sent = mail($to, $subject, $body, $headers);

if (!$sent) { http_response_code(500); }
echo json_encode(['ok' => (bool)$sent]);
