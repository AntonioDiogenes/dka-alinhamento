"""
Utilitário HTTP compartilhado (utils/http.py).
Fornece um wrapper de urllib.request.urlopen com fallback de SSL
para ambientes Windows/PyInstaller que não possuem bundle de certificados.
"""
import ssl
import urllib.request


def urlopen_with_ssl(req, timeout: int = 10):
    """
    Executa urlopen com validação SSL e faz fallback para contexto sem
    verificação caso ocorra CERTIFICATE_VERIFY_FAILED (comum no Windows
    com executáveis gerados pelo PyInstaller).
    """
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except Exception as exc:
        exc_str = str(exc)
        if "CERTIFICATE_VERIFY_FAILED" in exc_str or "certificate verify failed" in exc_str:
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise
