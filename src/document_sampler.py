"""Brazilian document number generator using utility functions."""

from src.utils.cei import random_cei
from src.utils.cnpj import random_cnpj
from src.utils.cpf import random_cpf
from src.utils.pis import random_pis


class DocumentSampler:
    """Class for generating various Brazilian documents."""

    def __init__(self):
        """Initialize the document sampler."""

    def generate_cpf(self, formatted: bool = True) -> str:
        """Generate a valid CPF number.

        Args:
            formatted: If True, returns CPF in XXX.XXX.XXX-XX format
        """
        return random_cpf(formatted=formatted)

    def generate_pis(self, formatted: bool = True) -> str:
        """Generate a valid PIS number.

        Args:
            formatted: If True, returns PIS in XXX.XXXXX.XX-X format
        """
        return random_pis(formatted=formatted)

    def generate_cnpj(self, formatted: bool = True) -> str:
        """Generate a valid CNPJ number.

        Args:
            formatted: If True, returns CNPJ in XX.XXX.XXX/XXXX-XX format
        """
        return random_cnpj(formatted=formatted)

    def generate_cei(self, formatted: bool = True) -> str:
        """Generate a valid CEI number.

        Args:
            formatted: If True, returns CEI in XX.XXX.XXXXX/XX format
        """
        return random_cei(formatted=formatted)
