from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ...logger import logger

if TYPE_CHECKING:
    from ..options import WriterOptions
    from io import TextIOWrapper


class FileWriter(ABC):
    """Base writer."""
    def __init__(self, file_path: str, writer_options: WriterOptions) -> None:
        self._file_path = file_path
        self._options = writer_options

    @abstractmethod
    def write(self, catalog_doc: Any) -> None:
        """Write Catalog Item API JSON document retrieved by parser."""
        pass

    def _open_file(self, file_path: str, mode='r') -> TextIOWrapper:
        return open(file_path, mode, encoding=self._options.encoding,
                    newline='', errors='replace')

    def _check_catalog_doc(self, catalog_doc: Any, verbose: bool = True):
        """Check Catalog Item API JSON document for errors."""
        try:
            assert isinstance(catalog_doc, dict)

            if 'error' in catalog_doc['meta']:  # An error is found
                if verbose:
                    error_msg = catalog_doc['meta']['error'].get('message', None)
                    if error_msg:
                        logger.error('Сервер ответил ошибкой: %s', error_msg)
                    else:
                        logger.error('Сервер ответил неизвестной ошибкой.')

                return False

            assert catalog_doc['meta']['code'] == 200
            assert 'result' in catalog_doc
            assert 'items' in catalog_doc['result']
            assert isinstance(catalog_doc['result']['items'], list)
            assert len(catalog_doc['result']['items']) > 0
            assert isinstance(catalog_doc['result']['items'][0], dict)

            if len(catalog_doc['result']['items']) > 1:
                logger.warning('Сервер вернул больше одного ответа.')

            return True
        except (KeyError, AssertionError):
            logger.error('Сервер ответил неизвестным документом.')
            return False

    def __enter__(self) -> FileWriter:
        self._file = self._open_file(self._file_path, 'w')
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self._file.close()
