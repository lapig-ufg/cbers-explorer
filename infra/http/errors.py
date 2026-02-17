from qgis.PyQt.QtCore import QCoreApplication


def _tr(message):
    return QCoreApplication.translate("HttpErrors", message)


def normalize_error(status_code, reply_content=""):
    messages = {
        400: _tr("Requisicao invalida. Verifique os parametros de busca."),
        401: _tr("Nao autorizado."),
        403: _tr("Acesso negado ao servidor STAC."),
        404: _tr("Recurso nao encontrado no servidor STAC."),
        408: _tr("Tempo de requisicao esgotado. Tente novamente."),
        429: _tr("Muitas requisicoes. Aguarde e tente novamente."),
        500: _tr("Erro interno do servidor STAC."),
        502: _tr("Servidor STAC indisponivel (Bad Gateway)."),
        503: _tr("Servico STAC temporariamente indisponivel."),
        504: _tr("Tempo de resposta do servidor STAC esgotado (Gateway Timeout)."),
    }

    if status_code in messages:
        return messages[status_code]

    if 400 <= status_code < 500:
        return _tr("Erro do cliente HTTP ({status_code}).").format(
            status_code=status_code
        )

    if 500 <= status_code < 600:
        return _tr("Erro do servidor STAC ({status_code}).").format(
            status_code=status_code
        )

    if status_code == 0:
        return _tr("Falha na conexao. Verifique sua rede.")

    return _tr("Erro HTTP inesperado ({status_code}).").format(
        status_code=status_code
    )
