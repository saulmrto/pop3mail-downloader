import os
import time
import poplib
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime, parsedate
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError # Para manejo de zonas horarias (ej. CST)
import re
import logging # Módulo para el registro de eventos del script

# Esta variable se llenará después de la selección de idioma
LANG_MESSAGES = {}

# --- Estructura de Mensajes Internacionalizados (Copiado de metadata.py para ejecución independiente) ---
MESSAGES = {
    'en': {
        # General
        'script_started': "Script started.",
        'script_finished': "Script finished.",
        'critical_error': "CRITICAL ERROR: {details}",
        'error_deleting_file': "Error deleting existing metadata file '{path}': {error}",
        'deleted_existing_metadata': "Existing metadata file '{path}' deleted.",
        'error_saving_metadata': "Error saving metadata to '{path}': {error}",
        'extracting_metadata_from_eml': "Extracting metadata from found .eml files...",
        'file_rename_failed': "Failed to rename '{old_name}' -> '{new_name}': {error}",
        'file_rename_not_found': "Could not rename '{filename}': File not found or already moved.",
        'file_renamed': "Renamed: '{old_name}' -> '{new_name}'",
        'file_not_found': "File not found: {path}",
        'filter_file_not_found': "Filter file '{path}' not found. Using empty collection for this filter.",
        'filters_loaded': "Filter lists loaded successfully.",
        'found_eml_files': "Found {count} .eml file(s).",
        'loading_filters': "Loading filter lists (whitelists/blacklists for emails and keywords)...",
        'metadata_saved_successfully': "Metadata saved successfully to '{path}'.",
        'error_loading_list': "Error loading list from '{path}': {error}. Returning empty collection.",
        'list_loaded': "{count} entries loaded from '{path}'.",
        'log_raw_date_header': "Raw Date Header",
        'log_date_not_parsable': "N/A (Not parsable)",
        'log_date_header_not_found': "N/A (Header not found)",
        'log_date_conversion_error': "N/A (Conversion error)",
        'log_date_tz_not_found': "N/A (Timezone not found)",
        'log_parsing_attempt': "--- Attempting to parse ---",
        'user_data_dir_creation_failed_path_not_dir': "CRITICAL ERROR: The path for user data exists but is not a directory: {path}",
        'script_will_exit': "The script will now exit.",
        'language_selection_prompt': "Please select a language for script messages:",
        'language_selection_english': "'en' for English",
        'language_selection_spanish': "'es' para Español",
        'language_selection_input': "Enter your choice / Ingrese su opción ('en' or 'es'): ",
        'invalid_selection': "Invalid selection. Please enter 'en' or 'es'.",
        'no_input_defaulting': "No input received (EOFError), defaulting to '{default_lang}'.",
        'selection_cancelled_defaulting': "Language selection cancelled by user, defaulting to '{default_lang}'.",
        'language_set_and_saved': "Language set to English and saved in '{path}'",
        'critical_config_error_save': "CRITICAL ERROR: Could not save language setting to '{path}': {error}",
        'defaulting_for_session': "Defaulting to '{default_lang}' for this session.",
        'settings_json_not_found': "settings.json not found, will prompt for language selection.",
        'invalid_lang_in_settings': "Invalid language '{lang}' found in settings.json, will prompt for selection.",
        'error_reading_settings_json': "Could not read or parse settings.json: {error}. Will prompt for language selection.",
        'essential_dirs_verified': "Essential directories verified/created successfully within the user data folder.",
        'critical_dir_creation_error': "The script cannot continue. Essential directories could not be created: {error}",
        'accounts_file_instructions': "Please create this file in the user data folder ('{data_dir}') with the format 'user:password@server:port'.",
        'no_emails_this_cycle': "No emails will be processed this cycle.",
        'account_parsed_successfully': "Line {line_num}: Account for user '{user_part}' parsed successfully.",
        'invalid_account_format': "Line {line_num}: Invalid format in accounts.txt for line: '{line}'. Expected 'user:password@server:port'.",
        'unexpected_error_parsing_account': "Line {line_num}: Unexpected error parsing line '{line}' in accounts.txt. Details: {e}",
        'general_error_reading_accounts': "ERROR: General failure reading accounts file '{path}'. Details: {e}",
        'user_dir_ready': "User directory for '{user_email}' ready at '{user_dir}'.",
        'error_creating_user_dir': "ERROR: Could not create directory for user '{user_email}' at '{user_dir}'. Details: {e}",
        'error_writing_raw_date_log': "ERROR: Could not write raw date to log file '{file}'. Details: {e}",
        'error_parsing_sender': "WARNING: Error parsing sender '{sender}'. Using raw value. Details: {e}",
        'email_date_not_available': "WARNING: Email date not available. Using generic filename: '{filename}'",
        'attempting_to_save_email': "Attempting to save email: Subject='{subject}', Sender='{sender}'",
        'email_file_saved_successfully': "Email file saved successfully at '{path}'.",
        'error_saving_eml_file': "ERROR: Could not save .eml file '{path}'. Details: {e}. Metadata for this email will not be registered.",
        'error_getting_file_size': "WARNING: Error getting size of file '{path}'. Details: {e}",
        'error_decoding_subject': "WARNING: Error decoding subject '{subject}'. Setting to 'No Subject'. Details: {e}",
        'spam_filter_info': "Spam filter info for this email: Score={score}, Filtered: '{filtered}', Whitelist Active: '{whitelist}'.",
        'loading_existing_metadata': "Attempting to load existing metadata from '{path}'...",
        'existing_metadata_loaded': "Existing metadata loaded successfully. Found {count} records.",
        'metadata_file_bad_format': "WARNING: Metadata file '{path}' does not have the expected format. Proceeding as if it's a new file.", # Keep
        'json_decode_error_metadata': "ERROR: Could not decode JSON file '{path}'. File might be corrupt or empty. Proceeding as if it's a new file.",
        'unexpected_error_loading_metadata': "ERROR: Unexpected error loading metadata from '{path}'. Details: {e}. Proceeding as if it's a new file.",
        'metadata_file_not_found': "Metadata file '{path}' not found. A new one will be created after the verification cycle.",
        'saving_metadata_records': "Saving {count} metadata records to '{path}'...",
        'error_saving_consolidated_metadata': "Could not save consolidated metadata: {error}",

        # script.py specific
        'downloader_script_started': "EMAIL DOWNLOAD AND FILTERING SCRIPT STARTED",
        'new_cycle_started': "--- STARTING NEW VERIFICATION CYCLE ({timestamp}) ---",
        'no_valid_accounts': "No valid accounts found in 'accounts.txt'. Script will wait before retrying.",
        'accounts_loaded': "Accounts loaded.",
        'processing_account': ">>> Processing account: {user} <<<",
        'connecting_to_server': "Connecting to {server}:{port}...",
        'authenticating_user': "Authenticating user '{user}'...",
        'auth_successful': "Authentication successful for '{user}'.",
        'auth_failed': "Authentication failed for {user}. Please check credentials.",
        'auth_failed_unexpected': "Authentication failed for {user} due to an unexpected error.",
        'mailbox_status': "Mailbox for '{user}': {count} email(s) total.",
        'mailbox_status_error': "Could not get mailbox status for {user}.",
        'mailbox_status_error_unexpected': "Unexpected error getting mailbox status for {user}.",
        'no_new_emails': "No new emails in mailbox for '{user}'.",
        'processing_email_num': "Processing email #{current}/{total}...",
        'email_already_exists': "Email #{num} already exists in registry. Skipping.",
        'downloading_new_email': "Downloading new email #{num}...",
        'email_saved_metadata_registered': "Email #{num} saved and metadata registered.",
        'email_save_metadata_failed': "Could not save email #{num} or its metadata.",
        'pop3_error_processing_email': "POP3 protocol error processing email #{num}: {error}. Skipping this email.",
        'unexpected_error_processing_email': "Unexpected error processing email #{num}: {error}. Skipping this email.",
        'pop3_connection_closed': "POP3 connection for '{user}' closed.",
        'pop3_connection_close_error': "Error closing POP3 connection for {user}.",
        'critical_account_processing_error': "CRITICAL ERROR: General failure processing account {user}: {error}. Moving to next account if applicable.",
        'metadata_extracted_successfully': "Metadata extracted successfully for '{filename}'.",
        'metadata_extraction_failed': "Failed to extract metadata for '{filename}'. Check logs for details.",
        'no_eml_found': "No .eml files found in the specified directory. Metadata file will not be generated.",
        'processing_eml_file': "Processing file #{current}/{total}: '{filename}'",
        'renamed_files_count': "{count} .eml file(s) renamed.",
        'renaming_eml_files': "Verifying and renaming .eml files on disk (if necessary)...",
        'cycle_finished_waiting': "--- Verification cycle finished. Waiting {minutes} minute(s) before next cycle. ---",
        'trigger_file_deleted': "Trigger file '{path}' deleted.",
        'trigger_file_delete_failed': "Could not delete trigger file '{path}'. Please delete manually to avoid unexpected restarts. Error: {error}",
        'trigger_file_detected': "Trigger file '{path}' detected. Restarting cycle manually.",
        'log_raw_dates_script_file': "RawDates_Script_{date}.log",
        'calculated_headers_hash': "Calculated headers hash: {hash}...",
        'email_already_downloaded': "Email #{num} (hash {hash}...) has already been downloaded for '{user}'. Skipping.",
        'email_is_new': "Email #{num} (hash {hash}...) is new for '{user}'. Downloading full body.",
        'email_body_downloaded': "Email body downloaded and parsed.",
        'email_processed_saved_metadata_obtained': "Email #{num} processed, saved, and metadata obtained successfully.",
        'error_getting_or_saving_metadata': "ERROR: Could not get or save metadata for email #{num}. Hash will not be registered.",
        'finished_processing_emails': "Finished processing emails for account '{user}'. Closing connection.",
        'pop3_connection_closed_successfully': "POP3 connection closed successfully.",
        'ssl_connection_established': "SSL connection established with {server}:{port}.",
        'non_secure_connection_established': "Non-secure connection established with {server}:{port}. Attempting to start TLS...",
        'tls_started_successfully': "TLS started successfully.",
        'warning_tls_not_started': "WARNING: Could not start TLS for account '{user}'. Connection might not be secure. Details: {e}",
        'warning_unexpected_tls_error': "WARNING: Unexpected error starting TLS for account '{user}'. Details: {e}",
        'starting_account_processing': "Starting account processing: '{user}' on {server}:{port}.",
        'getting_mailbox_status': "Getting mailbox status for '{user}'...",
        'mailbox_status_info': "Mailbox for '{user}': {count} email(s) with a total size of {total_size} bytes.",
        'ignoring_empty_line': "Line {line_num}: Ignoring empty line or comment in accounts.txt.",
    },
    'es': {
        # General
        'script_started': "Script iniciado.",
        'script_finished': "Script finalizado.",
        'critical_error': "ERROR CRÍTICO: {details}",
        'error_deleting_file': "Error al eliminar el archivo de metadatos existente '{path}': {error}",
        'deleted_existing_metadata': "Archivo de metadatos existente '{path}' eliminado.",
        'error_saving_metadata': "Error al guardar metadatos en '{path}': {error}",
        'extracting_metadata_from_eml': "Extrayendo metadatos de los archivos .eml encontrados...",
        'file_rename_failed': "Falló el renombramiento de '{old_name}' -> '{new_name}': {error}",
        'file_rename_not_found': "No se pudo renombrar '{filename}': Archivo no encontrado o ya movido.",
        'file_renamed': "Renombrado: '{old_name}' -> '{new_name}'",
        'file_not_found': "Archivo no encontrado: {path}",
        'filter_file_not_found': "Archivo de filtro '{path}' no encontrado. Se usará una colección vacía para este filtro.",
        'filters_loaded': "Listas de filtros cargadas exitosamente.",
        'found_eml_files': "Se encontraron {count} archivo(s) .eml.",
        'loading_filters': "Cargando listas de filtros (listas blancas/negras de correos y palabras clave)...",
        'metadata_saved_successfully': "Metadatos guardados exitosamente en '{path}'.",
        'error_loading_list': "Error al cargar la lista desde '{path}': {error}. Se retornará una colección vacía.",
        'list_loaded': "{count} entradas cargadas desde '{path}'.",
        'log_raw_date_header': "Encabezado de Fecha Crudo",
        'log_date_not_parsable': "N/A (No parseable)",
        'log_date_header_not_found': "N/A (Encabezado no encontrado)",
        'log_date_conversion_error': "N/A (Error de conversión)",
        'log_date_tz_not_found': "N/A (Zona horaria no encontrada)",
        'log_parsing_attempt': "--- Intentando parsear ---",
        'user_data_dir_creation_failed_path_not_dir': "ERROR CRÍTICO: La ruta para los datos de usuario existe pero no es un directorio: {path}",
        'script_will_exit': "El script se cerrará ahora.",
        'language_selection_prompt': "Por favor seleccione un idioma para los mensajes del script:",
        'language_selection_english': "  'en' para Inglés",
        'language_selection_spanish': "  'es' para Español",
        'language_selection_input': "Ingrese su opción ('en' o 'es'): ",
        'invalid_selection': "Selección inválida. Por favor ingrese 'en' o 'es'.",
        'no_input_defaulting': "No se recibió entrada (EOFError), usando '{default_lang}' por defecto.",
        'selection_cancelled_defaulting': "Selección de idioma cancelada por el usuario, usando '{default_lang}' por defecto.",
        'language_set_and_saved': "Idioma configurado a Español y guardado en '{path}'",
        'critical_config_error_save': "ERROR CRÍTICO: No se pudo guardar la configuración de idioma en '{path}': {error}",
        'defaulting_for_session': "Usando '{default_lang}' por defecto para esta sesión.",
        'settings_json_not_found': "settings.json no encontrado, se solicitará la selección de idioma.",
        'invalid_lang_in_settings': "Idioma inválido '{lang}' encontrado en settings.json, se solicitará la selección.",
        'error_reading_settings_json': "No se pudo leer o parsear settings.json: {error}. Se solicitará la selección de idioma.",
        'essential_dirs_verified': "Directorios esenciales verificados/creados exitosamente dentro de la carpeta de datos del usuario.",
        'critical_dir_creation_error': "El script no puede continuar. No se pudieron crear los directorios esenciales: {error}",
        'accounts_file_instructions': "Por favor, cree este archivo en la carpeta de datos del usuario ('{data_dir}') con el formato 'usuario:contraseña@servidor:puerto'.",
        'no_emails_this_cycle': "No se procesarán correos en este ciclo.",
        'account_parsed_successfully': "Línea {line_num}: Cuenta para el usuario '{user_part}' parseada exitosamente.",
        'invalid_account_format': "Línea {line_num}: Formato inválido en accounts.txt para la línea: '{line}'. Se esperaba 'usuario:contraseña@servidor:puerto'.",
        'unexpected_error_parsing_account': "Línea {line_num}: Error inesperado al parsear la línea '{line}' en accounts.txt. Detalles: {e}",
        'general_error_reading_accounts': "ERROR: Fallo general al leer el archivo de cuentas '{path}'. Detalles: {e}",
        'user_dir_ready': "Directorio de usuario para '{user_email}' listo en '{user_dir}'.",
        'error_creating_user_dir': "ERROR: No se pudo crear el directorio para el usuario '{user_email}' en '{user_dir}'. Detalles: {e}",
        'error_writing_raw_date_log': "ERROR: No se pudo escribir la fecha cruda en el archivo de log '{file}'. Detalles: {e}",
        'error_parsing_sender': "ADVERTENCIA: Error al parsear el remitente '{sender}'. Usando el valor original. Detalles: {e}",
        'email_date_not_available': "ADVERTENCIA: Fecha de correo no disponible. Usando nombre de archivo genérico: '{filename}'",
        'attempting_to_save_email': "Intentando guardar correo: Asunto='{subject}', Remitente='{sender}'",
        'email_file_saved_successfully': "Archivo de correo guardado exitosamente en '{path}'.",
        'error_saving_eml_file': "ERROR: No se pudo guardar el archivo .eml '{path}'. Detalles: {e}. Los metadatos de este correo no serán registrados.",
        'error_getting_file_size': "ADVERTENCIA: Error al obtener el tamaño del archivo '{path}'. Detalles: {e}",
        'error_decoding_subject': "ADVERTENCIA: Error al decodificar el asunto '{subject}'. Estableciendo como 'Sin Asunto'. Detalles: {e}",
        'spam_filter_info': "Información del filtro de spam para este correo: Puntuación={score}, Filtrado: '{filtered}', Lista Blanca Activa: '{whitelist}'.",
        'loading_existing_metadata': "Intentando cargar metadatos existentes desde '{path}'...",
        'existing_metadata_loaded': "Metadatos existentes cargados exitosamente. Se encontraron {count} registros.",
        'metadata_file_bad_format': "ADVERTENCIA: El archivo de metadatos '{path}' no tiene el formato esperado. Se procederá como si fuera un archivo nuevo.", # Keep
        'json_decode_error_metadata': "ERROR: No se pudo decodificar el archivo JSON '{path}'. El archivo podría estar corrupto o vacío. Se procederá como si fuera un archivo nuevo.",
        'unexpected_error_loading_metadata': "ERROR: Error inesperado al cargar metadatos desde '{path}'. Detalles: {e}. Se procederá como si fuera un archivo nuevo.",
        'metadata_file_not_found': "Archivo de metadatos '{path}' no encontrado. Se creará uno nuevo después del ciclo de verificación.",
        'saving_metadata_records': "Guardando {count} registros de metadatos en '{path}'...",
        'error_saving_consolidated_metadata': "No se pudieron guardar los metadatos consolidados: {error}",

        # script.py specific
        'downloader_script_started': "SCRIPT DE DESCARGA Y FILTRADO DE CORREOS INICIADO",
        'new_cycle_started': "--- INICIANDO NUEVO CICLO DE VERIFICACIÓN ({timestamp}) ---",
        'no_valid_accounts': "No se encontraron cuentas válidas en 'accounts.txt'. El script esperará antes de intentar de nuevo.",
        'accounts_loaded': "Cuentas cargadas.",
        'processing_account': ">>> Procesando cuenta: {user} <<<",
        'connecting_to_server': "Conectando a {server}:{port}...",
        'authenticating_user': "Autenticando usuario '{user}'...",
        'auth_successful': "Autenticación exitosa para '{user}'.",
        'auth_failed': "Falló la autenticación para {user}. Verifique sus credenciales.",
        'auth_failed_unexpected': "Falló la autenticación para {user} debido a un error inesperado.",
        'mailbox_status': "Buzón de '{user}': {count} correo(s) en total.",
        'mailbox_status_error': "No se pudo obtener el estado del buzón para {user}.",
        'mailbox_status_error_unexpected': "Error inesperado al obtener el estado del buzón para {user}.",
        'no_new_emails': "No hay correos nuevos en el buzón para '{user}'.",
        'processing_email_num': "Procesando correo #{current}/{total}...",
        'email_already_exists': "Correo #{num} ya existe en el registro. Omitiendo.",
        'downloading_new_email': "Descargando correo nuevo #{num}...",
        'email_saved_metadata_registered': "Correo #{num} guardado y metadatos registrados.",
        'email_save_metadata_failed': "No se pudo guardar el correo #{num} o sus metadatos.",
        'pop3_error_processing_email': "Error de protocolo POP3 al procesar correo #{num}: {error}. Omitiendo este correo.",
        'unexpected_error_processing_email': "Error inesperado al procesar correo #{num}: {error}. Omitiendo este correo.",
        'pop3_connection_closed': "Conexión POP3 para '{user}' cerrada.",
        'pop3_connection_close_error': "Error al cerrar la conexión POP3 para {user}.",
        'critical_account_processing_error': "ERROR CRÍTICO: Fallo general al procesar la cuenta {user}: {error}. Pasando a la siguiente cuenta (si aplica).",
        'metadata_extracted_successfully': "Metadatos extraídos exitosamente para '{filename}'.",
        'metadata_extraction_failed': "Falló la extracción de metadatos para '{filename}'. Consulte los logs para más detalles.",
        'no_eml_found': "No se encontraron archivos .eml en el directorio especificado. No se generará el archivo de metadatos.",
        'processing_eml_file': "Procesando archivo #{current}/{total}: '{filename}'",
        'renamed_files_count': "{count} archivo(s) .eml renombrados.",
        'renaming_eml_files': "Verificando y renombrando archivos .eml en disco (si es necesario)...",
        'cycle_finished_waiting': "--- Ciclo de verificación finalizado. Esperando {minutes} minuto(s) antes del próximo ciclo. ---",
        'trigger_file_deleted': "Archivo de trigger '{path}' eliminado.",
        'trigger_file_delete_failed': "No se pudo eliminar el archivo de trigger '{path}'. Por favor, elimínelo manualmente si desea evitar reinicios inesperados. Error: {error}",
        'trigger_file_detected': "Archivo de trigger '{path}' detectado. Reiniciando ciclo manualmente.",
        'log_raw_dates_script_file': "FechasCrudas_Script_{date}.log",
        'calculated_headers_hash': "Hash de encabezados calculado: {hash}...",
        'email_already_downloaded': "Correo #{num} (hash {hash}...) ya ha sido descargado para '{user}'. Omitiendo.",
        'email_is_new': "Correo #{num} (hash {hash}...) es nuevo para '{user}'. Descargando cuerpo completo.",
        'email_body_downloaded': "Cuerpo del correo descargado y parseado.",
        'email_processed_saved_metadata_obtained': "Correo #{num} procesado, guardado y metadatos obtenidos exitosamente.",
        'error_getting_or_saving_metadata': "ERROR: No se pudieron obtener o guardar los metadatos para el correo #{num}. El hash no será registrado.",
        'finished_processing_emails': "Procesamiento de correos finalizado para la cuenta '{user}'. Cerrando conexión.",
        'pop3_connection_closed_successfully': "Conexión POP3 cerrada exitosamente.",
        'ssl_connection_established': "Conexión SSL establecida con {server}:{port}.",
        'non_secure_connection_established': "Conexión no segura establecida con {server}:{port}. Intentando iniciar TLS...",
        'tls_started_successfully': "TLS iniciado exitosamente.",
        'warning_tls_not_started': "ADVERTENCIA: No se pudo iniciar TLS para la cuenta '{user}'. La conexión podría no ser segura. Detalles: {e}",
        'warning_unexpected_tls_error': "ADVERTENCIA: Error inesperado al iniciar TLS para la cuenta '{user}'. Detalles: {e}",
        'starting_account_processing': "Iniciando procesamiento de cuenta: '{user}' en {server}:{port}.",
        'getting_mailbox_status': "Obteniendo estado del buzón para '{user}'...",
        'mailbox_status_info': "Buzón de '{user}': {count} correo(s) con un tamaño total de {total_size} bytes.",
        'ignoring_empty_line': "Línea {line_num}: Ignorando línea vacía o comentario en accounts.txt.",
    }
}

def _get_or_create_user_data_directory():
    """
    Obtiene o crea el directorio raíz para los datos del usuario.
    Si el directorio existe pero no es un directorio, o si hay un error al crearlo,
    el script terminará con un mensaje crítico.
    """
    user_data_root = os.path.join(os.path.expanduser("~"), "Documents", "Pop3MailDownloader_UserData")
    try:
        os.makedirs(user_data_root, exist_ok=True)
        if not os.path.isdir(user_data_root):
            # Mensaje bilingüe codificado porque LANG_MESSAGES aún no está cargado.
            print(LANG_MESSAGES.get('user_data_dir_creation_failed_path_not_dir', "CRITICAL ERROR: The path for user data exists but is not a directory: {path}").format(path=user_data_root))
            print(LANG_MESSAGES.get('script_will_exit', "The script will now exit."))
            exit(1)
    except Exception as e:
        print(LANG_MESSAGES.get('critical_error', "CRITICAL ERROR: {details}").format(details=LANG_MESSAGES.get('user_data_dir_creation_failed', "Could not create or access user data directory: {path}\nDetails: {error}").format(path=user_data_root, error=e)))
        print(LANG_MESSAGES.get('script_will_exit', "The script will now exit."))
        exit(1)
    return user_data_root


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_ROOT = _get_or_create_user_data_directory()

# --- Configuración de Idioma ---
def load_or_select_language(user_data_root_path):
    """
    Carga el idioma guardado en settings.json o solicita al usuario que lo seleccione.
    Guarda la selección en settings.json.
    """
    settings_file_path = os.path.join(user_data_root_path, "settings.json")
    default_lang = 'en'
    lang = None
    settings_data = {}
    try:
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            lang = settings_data.get("lang")
            if lang not in ['en', 'es']:
                print(f"[CONFIG] {LANG_MESSAGES.get('invalid_lang_in_settings', 'Invalid language \'{lang}\' found in settings.json, will prompt for selection.').format(lang=lang)}")
                lang = None
        else:
            print(f"[CONFIG] {LANG_MESSAGES.get('settings_json_not_found', 'settings.json not found, will prompt for language selection.')}")
    except (json.JSONDecodeError, IOError) as e:
        print(f"[CONFIG-ERROR] {LANG_MESSAGES.get('error_reading_settings_json', 'Could not read or parse settings.json: {error}. Will prompt for language selection.').format(error=e)}")
        lang = None

    if lang is None:
        print("\n====================================================================")
        print(f" {LANG_MESSAGES.get('language_selection_prompt', 'Language Selection / Selección de Idioma')}")
        print("====================================================================")
        while True:
            try:
                print(f"\n{LANG_MESSAGES.get('language_selection_prompt', 'Please select a language for script messages:')}")
                print(f"{LANG_MESSAGES.get('language_selection_english', '  \'en\' for English')}")
                print(f"{LANG_MESSAGES.get('language_selection_spanish', '  \'es\' para Español')}")
                chosen_lang_input = input(LANG_MESSAGES.get('language_selection_input', "Enter your choice / Ingrese su opción ('en' or 'es'): ")).strip().lower()
                if chosen_lang_input in ['en', 'es']:
                    lang = chosen_lang_input
                    break
                else:
                    print(f"\n{LANG_MESSAGES.get('invalid_selection', 'Invalid selection. Please enter \'en\' or \'es\'.')}\n")
            except EOFError:
                print(LANG_MESSAGES.get('no_input_defaulting', "No input received (EOFError), defaulting to '{default_lang}'.").format(default_lang=default_lang))
                lang = default_lang
                break
            except KeyboardInterrupt:
                print(LANG_MESSAGES.get('selection_cancelled_defaulting', "\nLanguage selection cancelled by user, defaulting to '{default_lang}'.").format(default_lang=default_lang))
                lang = default_lang
                break
        settings_data["lang"] = lang
        try:
            os.makedirs(user_data_root_path, exist_ok=True)
            with open(settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            if lang == 'en':
                print(LANG_MESSAGES.get('language_set_and_saved', "\nLanguage set to English and saved in '{path}'").format(path=settings_file_path))
            else:
                print(LANG_MESSAGES.get('language_set_and_saved', "\nIdioma configurado a Español y guardado en '{path}'").format(path=settings_file_path))
            print("====================================================================\n")
        except IOError as e:
            print(LANG_MESSAGES.get('critical_config_error_save', "[CRITICAL-CONFIG-ERROR] Could not save language setting to '{path}': {error}").format(path=settings_file_path, error=e))
            print(LANG_MESSAGES.get('defaulting_for_session', "Defaulting to '{default_lang}' for this session.").format(default_lang=default_lang))
            lang = default_lang
    return lang

SELECTED_LANG_CODE = load_or_select_language(USER_DATA_ROOT)
LANG_MESSAGES = MESSAGES[SELECTED_LANG_CODE]

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [SCRIPT] - %(message)s')

# --- Configuraciones de Rutas Globales ---
DATA_DIR = USER_DATA_ROOT

FILTERS_DIR = os.path.join(DATA_DIR, "filters") # Subcarpeta para los archivos de filtro (listas blancas/negras).
EMAILS_DIR_NAME = "emails" # Nombre de la subcarpeta donde se guardarán los correos descargados.
EMAILS_BASE_DIR = os.path.join(DATA_DIR, EMAILS_DIR_NAME) # Ruta completa al directorio de correos
LOG_DIR_SCRIPT = os.path.join(DATA_DIR, "Logs") # Directorio para los archivos de log de este script

CHECK_INTERVAL = 15 * 60 # Intervalo de verificación en segundos (15 minutos)

TRIGGER_FILE_NAME = "trigger_check.txt"
TRIGGER_FILE_PATH = os.path.join(DATA_DIR, TRIGGER_FILE_NAME)

METADATA_FILE = os.path.join(DATA_DIR, "emails_metadata.json")

ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.txt")
USER_SETTINGS_FILE_IN_DATA = os.path.join(DATA_DIR, "settings.json") # Used for language
SPAM_CONFIG_FILE = os.path.join(DATA_DIR, "spam_config.json") # Path defined, but file won't be read by default

def crear_directorios_necesarios():
    """
    Crea los directorios esenciales para el funcionamiento del script si no existen.
    Termina el script si no se pueden crear.
    """
    try:
        os.makedirs(EMAILS_BASE_DIR, exist_ok=True) # Carpeta para los archivos .eml
        os.makedirs(FILTERS_DIR, exist_ok=True) # Directorio de filtros, aunque no se usen los archivos individuales ahora
        os.makedirs(LOG_DIR_SCRIPT, exist_ok=True) # Carpeta para los logs de depuración
        logging.info(LANG_MESSAGES.get('essential_dirs_verified', "Essential directories verified/created successfully within the user data folder."))
    except Exception as e:
        logging.critical(LANG_MESSAGES.get('critical_error', "CRITICAL ERROR: {details}").format(details=f"Could not create necessary directories. Please check write permissions. Error: {e}"))
        print(f"\n[CRITICAL ERROR] {LANG_MESSAGES.get('critical_dir_creation_error', 'The script cannot continue. Essential directories could not be created: {error}').format(error=e)}")
        exit(1) # Termina la ejecución del script.

def parse_accounts():
    """
    Lee el archivo de cuentas y parsea las credenciales de cada cuenta.
    Retorna una lista de diccionarios con 'user', 'password', 'server', 'port'.
    """
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        logging.error(LANG_MESSAGES.get('file_not_found', "File not found: {path}").format(path=ACCOUNTS_FILE) + ". " + LANG_MESSAGES.get('accounts_file_instructions', "Please create this file in the user data folder ('{data_dir}') with the format 'user:password@server:port'.").format(data_dir=USER_DATA_ROOT))
        print(f"\n[WARNING] {LANG_MESSAGES.get('file_not_found', 'File not found: {path}').format(path=ACCOUNTS_FILE)}. {LANG_MESSAGES.get('no_emails_this_cycle', 'No emails will be processed this cycle.')}")
        return []

    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1): # Itera sobre las líneas con su número.
                line = line.strip() # Elimina espacios en blanco al inicio y al final.
                if not line or line.startswith("#"):
                    logging.debug(LANG_MESSAGES.get('ignoring_empty_line', "Line {line_num}: Ignoring empty line or comment in accounts.txt.").format(line_num=line_num))
                    continue

                try:
                    user_part, rest = line.split(":", 1) # Divide una vez por el primer ':'
                    password_part, server_part = rest.rsplit("@", 1) # Divide una vez por el último '@'
                    server, port_str = server_part.rsplit(":", 1) # Divide una vez por el último ':'
                    port = int(port_str) # Convierte el puerto a entero.
                    accounts.append({
                        "user": user_part,
                        "password": password_part,
                        "server": server,
                        "port": port
                    })
                    logging.info(LANG_MESSAGES.get('account_parsed_successfully', "Line {line_num}: Account for user '{user_part}' parsed successfully.").format(line_num=line_num, user_part=user_part))
                except ValueError:
                    logging.warning(LANG_MESSAGES.get('invalid_account_format', "Line {line_num}: Invalid format in accounts.txt for line: '{line}'. Expected 'user:password@server:port'.").format(line_num=line_num, line=line))
                    pass
                except Exception as e:
                    logging.error(LANG_MESSAGES.get('unexpected_error_parsing_account', "Line {line_num}: Unexpected error parsing line '{line}' in accounts.txt. Details: {e}").format(line_num=line_num, line=line, e=e))
                    pass
    except Exception as e:
        logging.critical(LANG_MESSAGES.get('general_error_reading_accounts', "ERROR: General failure reading accounts file '{path}'. Details: {e}").format(path=ACCOUNTS_FILE, e=e))
        pass
    return accounts

def crear_estructura_directorios_usuario(user_email):
    """
    Crea el directorio específico para un usuario dentro del directorio de correos.
    """
    user_dir = os.path.join(EMAILS_BASE_DIR, user_email)
    try:
        os.makedirs(user_dir, exist_ok=True) # Crea el directorio del usuario si no existe.
        logging.info(LANG_MESSAGES.get('user_dir_ready', "User directory for '{user_email}' ready at '{user_dir}'.").format(user_email=user_email, user_dir=user_dir))
    except Exception as e:
        logging.error(LANG_MESSAGES.get('error_creating_user_dir', "ERROR: Could not create directory for user '{user_email}' at '{user_dir}'. Details: {e}").format(user_email=user_email, user_dir=user_dir, e=e))
        pass
    return user_dir

def sanitizar_nombre(nombre):
    """
    Sanitiza una cadena para usarla en nombres de archivo, eliminando caracteres no válidos.
    """
    return "".join(c if c.isalnum() or c in ("_", "-", ".", " ") else "" for c in nombre)

def log_fecha_cruda(fecha_str, user_email, fecha_cst_formateada):
    """
    Registra la fecha cruda del encabezado del correo y su conversión en un archivo de log.
    """
    log_filename_template = LANG_MESSAGES.get('log_raw_dates_script_file', "RawDates_Script_{date}.log")
    log_file = os.path.join(LOG_DIR_SCRIPT, log_filename_template.format(date=datetime.now().strftime('%Y-%m-%d')))
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: User: {user_email} | Raw Date: '{fecha_str}' | Converted CST: '{fecha_cst_formateada}'\n")
    except Exception as e:
        logging.error(LANG_MESSAGES.get('error_writing_raw_date_log', "ERROR: Could not write raw date to log file '{file}'. Details: {e}").format(file=log_file, e=e))
        pass

def obtener_fecha_hora_correo(msg, user_email_for_log="Desconocido"):
    """
    Extrae y formatea la fecha y hora de un correo electrónico, convirtiéndola a CST.
    """
    fecha_str = msg.get('Date')
    fecha_formateada = "" # Valor por defecto si no se puede obtener la fecha.
    fecha_iso = ""        # Valor por defecto si no se puede obtener la fecha ISO.
    fecha_dt = None       # Objeto datetime para la fecha parseada.
    log_fecha_cruda(
        fecha_str if fecha_str else LANG_MESSAGES.get('log_raw_date_header', "No Date Header"),
        user_email_for_log,
        LANG_MESSAGES.get('log_parsing_attempt', "--- Attempting to parse ---"))
    if fecha_str: # Procede solo si el encabezado 'Date' existe.
        try:
            fecha_dt = parsedate_to_datetime(fecha_str)
            if fecha_dt is None: # Si parsedate_to_datetime no pudo parsear.
                 pass
        except Exception as e: # Captura errores durante el parseo con parsedate_to_datetime.
            fecha_dt = None # Asegura que fecha_dt sea None para el siguiente intento.
        if fecha_dt is None: # Si el primer intento falló, intenta con parsedate.
            try:
                fecha_tuple = parsedate(fecha_str) # parsedate devuelve una tupla de tiempo.
                if fecha_tuple:
                    year, month, day, hour, minute, second, *rest = fecha_tuple
                    fecha_dt = datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo("UTC"))
                else:
                    pass
            except Exception as e: # Captura errores durante el parseo con parsedate.
                pass
        if fecha_dt: # Si se logró parsear la fecha a un objeto datetime.
            try:
                cst_zone = ZoneInfo("America/Mexico_City") # Define la zona horaria de destino.
                if fecha_dt.tzinfo is None:
                     fecha_dt = fecha_dt.replace(tzinfo=ZoneInfo("UTC"))
                fecha_cst = fecha_dt.astimezone(cst_zone)
                fecha_formateada = f"{fecha_cst.day:02d}-{fecha_cst.month:02d}-{fecha_cst.year}_{fecha_cst.hour:02d}-{fecha_cst.minute:02d}"
                fecha_iso = fecha_cst.isoformat() # Formato ISO 8601.
                log_fecha_cruda(fecha_str, user_email_for_log, fecha_formateada)
            except ZoneInfoNotFoundError:
                fecha_formateada = ""
                fecha_iso = ""
                log_fecha_cruda(fecha_str, user_email_for_log, LANG_MESSAGES.get('log_date_tz_not_found', "N/A (Timezone not found)"))
            except Exception as e:
                fecha_formateada = ""
                fecha_iso = ""
                log_fecha_cruda(fecha_str, user_email_for_log, LANG_MESSAGES.get('log_date_conversion_error', "N/A (Conversion error)"))
        else: # Si después de todos los intentos, fecha_dt sigue siendo None.
            log_fecha_cruda(fecha_str, user_email_for_log, LANG_MESSAGES.get('log_date_not_parsable', "N/A (Not parsable)"))
    else: # Si el encabezado 'Date' no se encontró en el correo.
        log_fecha_cruda(LANG_MESSAGES.get('log_raw_date_header', "No Date Header"), user_email_for_log, LANG_MESSAGES.get('log_date_header_not_found', "N/A (Header not found)"))
    return fecha_formateada, fecha_iso

def obtener_hash_encabezados(msg):
    """
    Calcula un hash SHA256 de los encabezados de un mensaje de correo.
    """
    headers_bytes = b'\r\n'.join(
        f"{key}: {value}".encode('utf-8', errors='ignore')
        for key, value in msg.items()
    )
    return hashlib.sha256(headers_bytes).hexdigest()

def load_spam_config():
    """
    Esta función ahora retorna filtros vacíos ya que spam_config.json no se debe usar.
    """
    mail_whitelist = set()
    mail_blacklist = set()
    word_whitelist = []
    word_blacklist = []
    # Ya no se lee spam_config.json
    logging.info(LANG_MESSAGES.get('filters_loaded', "Spam filtering is currently not configured to read spam_config.json. Using empty filters."))
    return mail_whitelist, mail_blacklist, word_whitelist, word_blacklist

def load_list_from_file(file_path, use_set=False):
    """
    Carga una lista de elementos desde un archivo de texto.
    Puede retornar un set (para búsquedas rápidas) o una lista.
    """
    items_collection = set() if use_set else [] # Inicializa como set o list según el parámetro.
    if not os.path.exists(file_path):
        logging.warning(LANG_MESSAGES.get('filter_file_not_found', "Filter file '{path}' not found. Using empty collection for this filter.").format(path=file_path))
        return items_collection
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().lower() # Elimina espacios y convierte a minúsculas para una comparación uniforme.
                if line and not line.startswith("#"): # Procesa solo líneas no vacías y no comentarios.
                    if use_set:
                        items_collection.add(line) # Añade al set.
                    else:
                        items_collection.append(line) # Añade a la lista.
        logging.info(LANG_MESSAGES.get('list_loaded', "{count} entries loaded from '{path}'.").format(count=len(items_collection), path=file_path))
    except Exception as e:
        logging.error(LANG_MESSAGES.get('error_loading_list', "Error loading list from '{path}': {error}. Returning empty collection.").format(path=file_path, error=e))
        return set() if use_set else [] # Retorna una colección vacía en caso de error.
    return items_collection

def extraer_score_spam(msg):
    """
    Extrae la puntuación de spam de los encabezados del correo, si está presente.
    """
    spam_score = None
    spam_headers = ['X-Spam-Score', 'X-Spam-Level', 'X-Mail-filter-Score', 'X-Spam-Status']
    for header_name in spam_headers:
        header_value = msg.get(header_name)
        if header_value: # Si el encabezado existe.
            match = re.search(r'score=([\d.]+)', header_value, re.IGNORECASE)
            if match:
                try:
                    spam_score = float(match.group(1)) # Extrae y convierte el score a flotante.
                    return spam_score # Retorna el primer score válido encontrado.
                except ValueError:
                    pass # Continúa buscando en otros encabezados si la conversión falla.
            if header_name in ['X-Spam-Score', 'X-Spam-Level']:
                 try:
                     spam_score = float(header_value.strip()) # Intenta convertir el valor directamente.
                     return spam_score # Retorna el primer score válido encontrado.
                 except ValueError:
                    pass # Continúa buscando.
    return spam_score # Retorna None si no se encontró ningún score válido en ningún encabezado.

def check_text_contains_keywords(text, keywords_collection):
    """
    Verifica si el texto contiene alguna de las palabras clave de la colección.
    """
    if not text or not keywords_collection: # Si el texto o la colección están vacíos, no hay coincidencias.
        return False
    text_lower = text.lower() # Convierte el texto a minúsculas una sola vez para eficiencia.
    for keyword in keywords_collection:
        if keyword in text_lower: # Comprueba si la palabra clave está en el texto.
            return True # Retorna True en la primera coincidencia.
    return False # Si se recorrieron todas las palabras clave y no se encontró ninguna.

def extraer_texto_del_cuerpo(msg):
    """
    Extrae el texto plano del cuerpo de un mensaje de correo.
    Maneja mensajes multipart y decodifica el contenido.
    """
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk(): # Itera a través de todas las partes del mensaje.
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition")) # Para identificar adjuntos.
            if "attachment" not in content_disposition and content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body_text += part.get_payload(decode=True).decode(charset, errors='replace') + "\n"
                except Exception as e:
                    pass
    else:
        if msg.get_content_type() == "text/plain":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                body_text = msg.get_payload(decode=True).decode(charset, errors='replace')
            except Exception as e:
                pass
    return body_text.strip() # Elimina cualquier espacio en blanco al inicio y al final del texto extraído.

def guardar_correo_y_obtener_metadata(user_email, msg_bytes, msg, hash_correo, mail_whitelist, mail_blacklist, word_whitelist, word_blacklist):
    """
    Guarda el contenido raw del correo en un archivo .eml y extrae sus metadatos.
    Aplica reglas de filtro de spam basadas en listas blancas/negras.
    """
    from_header = msg.get('From', 'N/A')
    nombre_real_remitente, direccion_email_remitente = "N/A", "N/A"
    if from_header != 'N/A':
        try:
            nombre_real_remitente, direccion_email_remitente = parseaddr(from_header)
            if not nombre_real_remitente and not direccion_email_remitente:
                nombre_real_remitente = from_header
                direccion_email_remitente = from_header
        except Exception as e:
            logging.warning(LANG_MESSAGES.get('error_parsing_sender', "WARNING: Error parsing sender '{sender}'. Using raw value. Details: {e}").format(sender=from_header, e=e))
            nombre_real_remitente = from_header
            direccion_email_remitente = from_header
    if direccion_email_remitente and direccion_email_remitente != 'N/A':
        sender_display = direccion_email_remitente
    elif nombre_real_remitente and nombre_real_remitente != 'N/A':
        sender_display = nombre_real_remitente
    elif from_header != 'N/A':
        sender_display = from_header
    else:
        sender_display = "N/A" # Último recurso si no se encuentra información.
    sender_email_for_filter = direccion_email_remitente.lower() if direccion_email_remitente and direccion_email_remitente != 'N/A' else ""
    asunto = msg.get('Subject', 'Sin Asunto') # Valor predeterminado si no hay asunto.
    if asunto != 'Sin Asunto': # Solo intentar decodificar si no es el valor por defecto.
        try:
            asunto = asunto.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception as e:
            logging.warning(LANG_MESSAGES.get('error_decoding_subject', "WARNING: Error decoding subject '{subject}'. Setting to 'No Subject'. Details: {e}").format(subject=asunto, e=e))
            asunto = "Sin Asunto" # Si falla la decodificación, también se usa "Sin Asunto".
    message_id = msg.get('Message-ID', 'N/A')
    to_header = msg.get('To', 'N/A')
    cc_header = msg.get('Cc', 'N/A')
    bcc_header = msg.get('Bcc', 'N/A') # Nota: Bcc rara vez está presente en correos recibidos.
    def parse_recipients_list(header_value):
        recipients = []
        if header_value != 'N/A':
            for recipient_entry in header_value.split(','):
                _, addr = parseaddr(recipient_entry.strip())
                if addr:
                    recipients.append(addr)
        return recipients
    recipients_to = parse_recipients_list(to_header)
    recipients_cc = parse_recipients_list(cc_header)
    recipients_bcc = parse_recipients_list(bcc_header)
    remitente_s = sanitizar_nombre(sender_display)
    asunto_s = sanitizar_nombre(asunto)
    fecha_formateada, fecha_iso = obtener_fecha_hora_correo(msg, user_email)
    if fecha_formateada: # Solo usa la fecha si no está vacía.
        max_len = 150 # Longitud máxima deseada para el nombre del archivo.
        base_name = f"{fecha_formateada} --- {asunto_s} --- {remitente_s}"
        if len(base_name) > max_len:
            truncated_asunto_len = max_len - len(fecha_formateada) - len(remitente_s) - 6 # 6 por los " --- "
            truncated_asunto_len = max(0, truncated_asunto_len) # Asegura que la longitud no sea negativa.
            truncated_asunto = asunto_s[:truncated_asunto_len].strip()
            base_name = f"{fecha_formateada} --- {truncated_asunto} --- {remitente_s}"
        nombre_archivo_eml = f"{base_name}.eml"
    else:
        nombre_archivo_eml = f"Correo_SinFecha_{hash_correo[:10]}.eml"
        logging.warning(LANG_MESSAGES.get('email_date_not_available', "WARNING: Email date not available. Using generic filename: '{filename}'").format(filename=nombre_archivo_eml))

    path_usuario = os.path.join(EMAILS_BASE_DIR, user_email)
    archivo_eml_completo = os.path.join(path_usuario, nombre_archivo_eml)
    raw_email_bytes = b'\r\n'.join(msg_bytes)
    logging.info(LANG_MESSAGES.get('attempting_to_save_email', "Attempting to save email: Subject='{subject}', Sender='{sender}'").format(subject=asunto, sender=sender_display))
    try:
        with open(archivo_eml_completo, 'wb') as f: # Abre el archivo en modo escritura binaria.
            f.write(raw_email_bytes) # Escribe el contenido raw del correo.
        logging.info(LANG_MESSAGES.get('email_file_saved_successfully', "Email file saved successfully at '{path}'.").format(path=archivo_eml_completo))
    except Exception as e:
        logging.error(LANG_MESSAGES.get('error_saving_eml_file', "ERROR: Could not save .eml file '{path}'. Details: {e}. Metadata for this email will not be registered.").format(path=archivo_eml_completo, e=e))
        return None # Retorna None si el archivo no se pudo guardar, indicando un fallo.
    tamano_eml = -1
    try:
        tamano_eml = os.path.getsize(archivo_eml_completo)
        logging.debug(f"Size of saved .eml file: {tamano_eml} bytes.")
    except Exception as e:
        logging.warning(LANG_MESSAGES.get('error_getting_file_size', "WARNING: Error getting size of file '{path}'. Details: {e}").format(path=archivo_eml_completo, e=e))
        pass
    asunto_lower = asunto.lower() if asunto != 'Sin Asunto' else ""
    cuerpo_correo_lower = extraer_texto_del_cuerpo(msg).lower()
    spam_score = extraer_score_spam(msg) # Extrae la puntuación de spam (puede ser None).
    spam_filter_status = "no" # Asume que el correo no es spam por defecto.
    spam_filter_whitelist_status = "no" # Nuevo campo para indicar si una whitelist se activó.
    
    # Lógica de filtrado de spam eliminada ya que spam_config.json no se usa.
    # Si se quisiera reintroducir una lógica de filtrado diferente, iría aquí.
    # Por ahora, todos los correos tendrán spam_filter_status = "no" y spam_filter_whitelist_status = "no"
    # a menos que se modifique esta sección.

    metadatos = {
        "name": nombre_archivo_eml,
        "path": os.path.relpath(archivo_eml_completo, EMAILS_BASE_DIR),
        "date": fecha_formateada.split('_')[0] if '_' in fecha_formateada else fecha_formateada, # Solo la fecha (DD-MM-AAAA), o ""
        "time": fecha_formateada.split('_')[1] if '_' in fecha_formateada else "", # Solo la hora (HH-MM), o ""
        "subject": asunto, # "Sin Asunto" si no se encontró.
        "sender": sender_display,
        "recipient": user_email, # El usuario de la cuenta POP3 que descargó el correo.
        "to": recipients_to,
        "cc": recipients_cc,
        "bcc": recipients_bcc,
        "message_id": message_id,
        "fecha_iso": fecha_iso, # Formato ISO 8601, o ""
        "tamano_eml": tamano_eml,
        "hash": hash_correo,
        "spam_score": spam_score, # Puntuación de spam numérica o None (solo informativa).
        "spam_filter": spam_filter_status, # 'yes' si es spam según las reglas (sin score), 'no' si no lo es o fue anulado por lista blanca.
        "spam_filter_whitelist": spam_filter_whitelist_status # Nuevo campo: 'yes' si una whitelist se activó, 'no' en caso contrario.
    }
    logging.info(LANG_MESSAGES.get('spam_filter_info', "Spam filter info for this email: Score={score}, Filtered: '{filtered}', Whitelist Active: '{whitelist}'.").format(score=spam_score if spam_score is not None else 'N/A', filtered=spam_filter_status, whitelist=spam_filter_whitelist_status))
    return metadatos

def cargar_metadatos_existentes():
    """
    Carga los metadatos de correos electrónicos existentes desde el archivo JSON.
    Retorna una lista de metadatos y un set de hashes de correos existentes.
    """
    all_emails_metadata = []
    existing_hashes = set()
    logging.info(LANG_MESSAGES.get('loading_existing_metadata', "Attempting to load existing metadata from '{path}'...").format(path=METADATA_FILE))
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f) # Carga el contenido JSON del archivo.
                if isinstance(data, dict) and "emails" in data and isinstance(data["emails"], list):
                    all_emails_metadata = data["emails"]
                    for email_entry in all_emails_metadata:
                        if "hash" in email_entry:
                            existing_hashes.add(email_entry["hash"])
                    logging.info(LANG_MESSAGES.get('existing_metadata_loaded', "Existing metadata loaded successfully. Found {count} records.").format(count=len(all_emails_metadata)))
                else:
                    logging.warning(LANG_MESSAGES.get('metadata_file_bad_format', "WARNING: Metadata file '{path}' does not have the expected format. Proceeding as if it's a new file.").format(path=METADATA_FILE))
                    pass
        except json.JSONDecodeError:
            logging.error(LANG_MESSAGES.get('json_decode_error_metadata', "ERROR: Could not decode JSON file '{path}'. File might be corrupt or empty. Proceeding as if it's a new file.").format(path=METADATA_FILE))
            pass
        except Exception as e:
            logging.error(LANG_MESSAGES.get('unexpected_error_loading_metadata', "ERROR: Unexpected error loading metadata from '{path}'. Details: {e}. Proceeding as if it's a new file.").format(path=METADATA_FILE, e=e))
            pass
    else:
        logging.info(LANG_MESSAGES.get('metadata_file_not_found', "Metadata file '{path}' not found. A new one will be created after the verification cycle.").format(path=METADATA_FILE))
        pass
    return all_emails_metadata, existing_hashes

def guardar_metadatos_consolidados(all_emails_metadata):
    """
    Guarda la lista consolidada de metadatos de correos electrónicos en un archivo JSON.
    """
    logging.info(LANG_MESSAGES.get('saving_metadata_records', "Saving {count} metadata records to '{path}'...").format(count=len(all_emails_metadata), path=METADATA_FILE))
    try:
        os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True) # Asegura que el directorio de destino exista.
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"emails": all_emails_metadata, "total_emails": len(all_emails_metadata)}, f, ensure_ascii=False, indent=2)
        logging.info(LANG_MESSAGES.get('metadata_saved_successfully', "Metadata saved successfully to '{path}'.").format(path=METADATA_FILE))
        print(f"  {LANG_MESSAGES.get('metadata_saved_successfully', 'Metadata updated and saved to {path}.').format(path=METADATA_FILE)}")
    except Exception as e:
        logging.error(LANG_MESSAGES.get('error_saving_metadata', "Error saving metadata to '{path}': {error}").format(path=METADATA_FILE, error=e))
        print(f"  [ERROR] {LANG_MESSAGES.get('error_saving_consolidated_metadata', 'Could not save consolidated metadata: {error}').format(error=e)}")
        pass

def procesar_cuenta(account, all_emails_metadata, existing_hashes, mail_whitelist, mail_blacklist, word_whitelist, word_blacklist):
    """
    Procesa una cuenta de correo POP3: se conecta, autentica, descarga nuevos correos
    y guarda sus metadatos.
    """
    user = account["user"]
    password = account["password"]
    server = account["server"]
    port = account["port"]
    servidor_pop = None # Inicializa la variable para asegurar que esté definida.
    logging.info(LANG_MESSAGES.get('starting_account_processing', "Starting account processing: '{user}' on {server}:{port}.").format(user=user, server=server, port=port))
    print(LANG_MESSAGES.get('processing_account', "\n  >>> Procesando cuenta: {user} <<<").format(user=user))

    try:
        logging.info(LANG_MESSAGES.get('connecting_to_server', "Connecting to {server}:{port}...").format(server=server, port=port))
        print(LANG_MESSAGES.get('connecting_to_server', "  Conectando a {server}:{port}...").format(server=server, port=port))
        if port == 995:
            servidor_pop = poplib.POP3_SSL(server, port=port, timeout=30)
            logging.info(LANG_MESSAGES.get('ssl_connection_established', "SSL connection established with {server}:{port}.").format(server=server, port=port))
        else:
            servidor_pop = poplib.POP3(server, port=port, timeout=30)
            logging.info(LANG_MESSAGES.get('non_secure_connection_established', "Non-secure connection established with {server}:{port}. Attempting to start TLS...").format(server=server, port=port))
            try:
                servidor_pop.starttls() # Intenta actualizar la conexión a TLS.
                logging.info(LANG_MESSAGES.get('tls_started_successfully', "TLS started successfully."))
            except poplib.error_proto as e:
                logging.warning(LANG_MESSAGES.get('warning_tls_not_started', "WARNING: Could not start TLS for account '{user}'. Connection might not be secure. Details: {e}").format(user=user, e=e))
                pass
            except Exception as e:
                logging.warning(LANG_MESSAGES.get('warning_unexpected_tls_error', "WARNING: Unexpected error starting TLS for account '{user}'. Details: {e}").format(user=user, e=e))
                pass
        
        logging.info(LANG_MESSAGES.get('authenticating_user', "Authenticating user '{user}'...").format(user=user))
        print(LANG_MESSAGES.get('authenticating_user', "  Autenticando usuario '{user}'...").format(user=user))
        try:
            servidor_pop.user(user) # Envía el nombre de usuario.
            servidor_pop.pass_(password) # Envía la contraseña.
            logging.info(LANG_MESSAGES.get('auth_successful', "Authentication successful for '{user}'.").format(user=user))
            print(LANG_MESSAGES.get('auth_successful', "  Autenticación exitosa para '{user}'.").format(user=user))
        except poplib.error_proto as e:
            logging.error(LANG_MESSAGES.get('auth_failed', "Authentication failed for {user}. Please check credentials.").format(user=user) + f" Details: {e}")
            print(LANG_MESSAGES.get('auth_failed', "  [ERROR] Falló la autenticación para {user}. Verifique sus credenciales.").format(user=user))
            if servidor_pop: # Asegura cerrar la conexión si se estableció.
                try:
                    servidor_pop.quit()
                except Exception:
                    pass
            return # Sale de la función si la autenticación falla.
        except Exception as e:
            logging.error(LANG_MESSAGES.get('auth_failed_unexpected', "Authentication failed for {user} due to an unexpected error.").format(user=user) + f" Details: {e}")
            print(LANG_MESSAGES.get('auth_failed_unexpected', "  [ERROR] Falló la autenticación para {user} debido a un error inesperado.").format(user=user))
            if servidor_pop:
                try:
                    servidor_pop.quit()
                except Exception:
                    pass
            return
        
        logging.info(LANG_MESSAGES.get('getting_mailbox_status', "Getting mailbox status for '{user}'...").format(user=user))
        try:
            count, total_size = servidor_pop.stat() # Obtiene el número de correos y el tamaño total.
            logging.info(LANG_MESSAGES.get('mailbox_status_info', "Mailbox for '{user}': {count} email(s) with a total size of {total_size} bytes.").format(user=user, count=count, total_size=total_size))
            print(LANG_MESSAGES.get('mailbox_status', "  Buzón de '{user}': {count} correo(s) en total.").format(user=user, count=count))
        except poplib.error_proto as e:
            logging.error(LANG_MESSAGES.get('mailbox_status_error', "Could not get mailbox status for {user}.").format(user=user) + f" Details: {e}")
            print(LANG_MESSAGES.get('mailbox_status_error', "  [ERROR] No se pudo obtener el estado del buzón para {user}.").format(user=user))
            if servidor_pop:
                try:
                    servidor_pop.quit()
                except Exception:
                    pass
            return
        except Exception as e:
            logging.error(LANG_MESSAGES.get('mailbox_status_error_unexpected', "Unexpected error getting mailbox status for {user}.").format(user=user) + f" Details: {e}")
            print(LANG_MESSAGES.get('mailbox_status_error_unexpected', "  [ERROR] Error inesperado al obtener el estado del buzón para {user}.").format(user=user))
            if servidor_pop:
                try:
                    servidor_pop.quit()
                except Exception:
                    pass
            return
        
        directorio_guardado_usuario = crear_estructura_directorios_usuario(user)
        if count == 0:
            logging.info(LANG_MESSAGES.get('no_new_emails', "No new emails in mailbox for '{user}'.").format(user=user))
            print(LANG_MESSAGES.get('no_new_emails', "  No hay correos nuevos en el buzón para '{user}'.").format(user=user))
            pass
        for i in range(1, count + 1):
            logging.info(LANG_MESSAGES.get('processing_email_num', "Processing email #{current}/{total}...").format(current=i, total=count) + f" for '{user}'.")
            print(LANG_MESSAGES.get('processing_email_num', "    Procesando correo #{current}/{total}...").format(current=i, total=count))
            try:
                _, header_bytes, _ = servidor_pop.top(i, 0)
                headers_raw = b'\r\n'.join(header_bytes)
                msg_headers = BytesParser(policy=policy.default).parsebytes(headers_raw)
                hash_correo = obtener_hash_encabezados(msg_headers)
                logging.debug(LANG_MESSAGES.get('calculated_headers_hash', "Calculated headers hash: {hash}...").format(hash=hash_correo[:10]))
                if hash_correo in existing_hashes:
                    logging.info(LANG_MESSAGES.get('email_already_downloaded', "Email #{num} (hash {hash}...) has already been downloaded for '{user}'. Skipping.").format(num=i, hash=hash_correo[:10], user=user))
                    print(LANG_MESSAGES.get('email_already_exists', f"      Correo #{i} ya existe en el registro. Omitiendo.").format(num=i))
                    continue # Pasa al siguiente correo sin descargarlo de nuevo.
                else:
                    logging.info(LANG_MESSAGES.get('email_is_new', "Email #{num} (hash {hash}...) is new for '{user}'. Downloading full body.").format(num=i, hash=hash_correo[:10], user=user))
                    print(LANG_MESSAGES.get('downloading_new_email', f"      Descargando correo nuevo #{i}...").format(num=i))
                    pass
                _, msg_bytes, _ = servidor_pop.retr(i)
                msg = BytesParser(policy=policy.default).parsebytes(b'\r\n'.join(msg_bytes))
                logging.debug(LANG_MESSAGES.get('email_body_downloaded', "Email body downloaded and parsed."))
                metadatos_correo = guardar_correo_y_obtener_metadata(
                    user, msg_bytes, msg, hash_correo, mail_whitelist, mail_blacklist, word_whitelist, word_blacklist)
                if metadatos_correo:
                    all_emails_metadata.append(metadatos_correo) # Añade los metadatos a la lista global.
                    existing_hashes.add(metadatos_correo["hash"]) # Añade el hash para futuras verificaciones.
                    logging.info(LANG_MESSAGES.get('email_processed_saved_metadata_obtained', "Email #{num} processed, saved, and metadata obtained successfully.").format(num=i))
                    print(LANG_MESSAGES.get('email_saved_metadata_registered', f"      Correo #{i} guardado y metadatos registrados.").format(num=i))
                else:
                    logging.error(LANG_MESSAGES.get('error_getting_or_saving_metadata', "ERROR: Could not get or save metadata for email #{num}. Hash will not be registered.").format(num=i))
                    print(LANG_MESSAGES.get('email_save_metadata_failed', f"      [ERROR] No se pudo guardar el correo #{i} o sus metadatos.").format(num=i))
                    pass
            except poplib.error_proto as e:
                logging.error(LANG_MESSAGES.get('pop3_error_processing_email', "POP3 protocol error processing email #{num}: {error}. Skipping this email.").format(num=i, error=e) + f" for '{user}'.")
                print(LANG_MESSAGES.get('pop3_error_processing_email', f"    [ERROR] Fallo de POP3 al procesar correo #{i}: {e}. Omitiendo este correo.").format(num=i, error=e))
                continue # Continúa con el siguiente correo si hay un error de protocolo.
            except Exception as e:
                logging.error(LANG_MESSAGES.get('unexpected_error_processing_email', "Unexpected error processing email #{num}: {error}. Skipping this email.").format(num=i, error=e) + f" for '{user}'.")
                print(LANG_MESSAGES.get('unexpected_error_processing_email', f"    [ERROR] Error inesperado al procesar correo #{i}: {e}. Omitiendo este correo.").format(num=i, error=e))
                continue # Continúa con el siguiente correo si hay un error general.
        
        logging.info(LANG_MESSAGES.get('finished_processing_emails', "Finished processing emails for account '{user}'. Closing connection.").format(user=user))
        if servidor_pop:
            try:
                servidor_pop.quit() # Cierra la conexión POP3.
                logging.info(LANG_MESSAGES.get('pop3_connection_closed_successfully', "POP3 connection closed successfully."))
                print(LANG_MESSAGES.get('pop3_connection_closed', "  Conexión POP3 para '{user}' cerrada.").format(user=user))
            except Exception as e:
                logging.warning(LANG_MESSAGES.get('pop3_connection_close_error', "Error closing POP3 connection for {user}.").format(user=user) + f" Details: {e}")
                print(LANG_MESSAGES.get('pop3_connection_close_error', f"  [WARNING] Error al cerrar la conexión para {user}.").format(user=user))
                pass
    except Exception as e:
        logging.critical(LANG_MESSAGES.get('critical_account_processing_error', "CRITICAL ERROR: General failure processing account {user}: {error}. Moving to next account if applicable.").format(user=user, error=e))
        print(LANG_MESSAGES.get('critical_account_processing_error', f"  [CRITICAL ERROR] Fallo general al procesar la cuenta {user}: {e}. Pasando a la siguiente cuenta (si aplica).").format(user=user, error=e))
        if servidor_pop:
            try:
                servidor_pop.quit()
            except Exception:
                pass # Ignora errores al intentar cerrar la conexión si ya hay un error crítico.

def main():
    """
    Función principal del script: inicia el ciclo de verificación de correos,
    maneja la carga de cuentas y filtros, y gestiona los ciclos de espera.
    """
    print("=====================================================")
    print(f"  {LANG_MESSAGES.get('downloader_script_started', 'EMAIL DOWNLOAD AND FILTERING SCRIPT STARTED')}")
    print("=====================================================")
    logging.info(LANG_MESSAGES.get('script_started', "Script started."))

    crear_directorios_necesarios()
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(LANG_MESSAGES.get('new_cycle_started', "\n--- INICIANDO NUEVO CICLO DE VERIFICACIÓN ({timestamp}) ---").format(timestamp=timestamp))
        logging.info(LANG_MESSAGES.get('new_cycle_started', "Starting new email verification cycle.").format(timestamp=timestamp))
        try:
            accounts = parse_accounts()
            if not accounts:
                print(LANG_MESSAGES.get('no_valid_accounts', "No se encontraron cuentas válidas. Esperando el próximo ciclo."))
                logging.warning(LANG_MESSAGES.get('no_valid_accounts', "No valid accounts found. Waiting for next cycle."))
                pass
            else:
                all_emails_metadata, existing_hashes = cargar_metadatos_existentes()
                # Se llama a load_spam_config, pero ahora retorna filtros vacíos.
                mail_whitelist, mail_blacklist, word_whitelist, word_blacklist = load_spam_config()
                
                # El mensaje de "filtros cargados" ahora reflejará que no se usa spam_config.json
                print(f"  {LANG_MESSAGES.get('filters_loaded', 'Spam filter configuration (spam_config.json) is not being used. No filters applied.')}")

                for account in accounts:
                    procesar_cuenta(account, all_emails_metadata, existing_hashes, mail_whitelist, mail_blacklist, word_whitelist, word_blacklist)
                guardar_metadatos_consolidados(all_emails_metadata)
        except Exception as e:
            print(LANG_MESSAGES.get('critical_error', "\n[ERROR CRÍTICO] Ocurrió un error inesperado en el bucle principal del script: {details}").format(details=e))
            logging.critical(LANG_MESSAGES.get('critical_error', "Critical error in main script loop: {details}").format(details=e))
            pass
        
        print(LANG_MESSAGES.get('cycle_finished_waiting', "\n--- Ciclo de verificación finalizado. Esperando {minutes} minuto(s) antes del próximo ciclo. ---").format(minutes=CHECK_INTERVAL//60))
        logging.info(LANG_MESSAGES.get('cycle_finished_waiting', "Verification cycle finished. Waiting {minutes} minute(s).").format(minutes=CHECK_INTERVAL//60))

        tiempo_esperado = 0
        while tiempo_esperado < CHECK_INTERVAL:
            time.sleep(1) # Espera 1 segundo para no consumir CPU innecesariamente.
            tiempo_esperado += 1
            if os.path.exists(TRIGGER_FILE_PATH):
                print(LANG_MESSAGES.get('trigger_file_detected', f"\n--- Archivo de trigger '{TRIGGER_FILE_PATH}' detectado. Reiniciando ciclo manualmente. ---").format(path=TRIGGER_FILE_PATH))
                logging.info(LANG_MESSAGES.get('trigger_file_detected', f"Trigger file '{TRIGGER_FILE_PATH}' detected. Restarting cycle.").format(path=TRIGGER_FILE_PATH))
                try:
                    os.remove(TRIGGER_FILE_PATH) # Elimina el archivo de trigger para que no se active de nuevo.
                    print(LANG_MESSAGES.get('trigger_file_deleted', f"Archivo de trigger '{TRIGGER_FILE_PATH}' eliminado.").format(path=TRIGGER_FILE_PATH))
                    logging.info(LANG_MESSAGES.get('trigger_file_deleted', f"Trigger file '{TRIGGER_FILE_PATH}' deleted.").format(path=TRIGGER_FILE_PATH))
                except Exception as e:
                    print(LANG_MESSAGES.get('trigger_file_delete_failed', f"  [ADVERTENCIA] No se pudo eliminar el archivo de trigger '{TRIGGER_FILE_PATH}'. Por favor, elimínelo manualmente. Error: {e}").format(path=TRIGGER_FILE_PATH, error=e))
                    logging.warning(LANG_MESSAGES.get('trigger_file_delete_failed', f"Could not delete trigger file '{TRIGGER_FILE_PATH}': {e}").format(path=TRIGGER_FILE_PATH, error=e))
                    pass
                break # Rompe el bucle de espera y reinicia el ciclo principal de inmediato.

if __name__ == "__main__":
    main()
