from sslyze.server_connectivity import ServerConnectivityInfo
from sslyze.synchronous_scanner import SynchronousScanner
from sslyze import synchronous_scanner
from ssylze.plugins.openssl_cipher_suites_plugin import Tlsv10ScanCommand
from ssylze.ssl_settings import TlsWrappedProtocolEnum

def my_handler(event, context):
    # Setup the server to scan and ensure it is online/reachable
    hostname = event['hostname']
    server_info = ServerConnectivityInfo(hostname=hostname, port=587,
                                         tls_wrapped_protocol=TlsWrappedProtocolEnum.STARTTLS_SMTP)
    server_info.test_connectivity_to_server()

    # Run one scan command synchronously to list the server's TLS 1.0 cipher suites
    print(u'\nRunning one scan command synchronously...')
    synchronous_scanner = SynchronousScanner()
    command = Tlsv10ScanCommand()
    scan_result = synchronous_scanner.run_scan_command(server_info, command)
    ciphers = [cipher.name for cipher in scan_result.accepted_cipher_list]
      
    return { 
        'message' : ciphers[0]
    }  

