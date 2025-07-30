"""Brazilian document number generator."""
from typing import List
import secrets


class DocumentSampler:
    """Class for generating various Brazilian documents."""
    
    def __init__(self):
        """Initialize the document sampler."""
        pass

    def _calculate_verifier_digit(self, digits: List[int], weights: List[int]) -> int:
        """Calculate verifier digit using provided weights."""
        total = sum(d * w for d, w in zip(digits, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    def generate_cei(self) -> str:
        """Generate a valid CEI number."""
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(10)]
        
        # Calculate first verifier digit
        weights = [7, 4, 1, 8, 5, 2, 1, 6, 3, 7]
        total = sum(d * w for d, w in zip(base, weights))
        remainder = total % 11
        if remainder == 0:
            remainder = 11
        digit = 11 - remainder
        
        base.append(digit)
        return ''.join(map(str, base))

    def generate_cnpj(self) -> str:
        """Generate a valid CNPJ number."""
        # Generate first 12 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(12)]
        
        # Calculate first verifier digit
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit1 = self._calculate_verifier_digit(base, weights)
        base.append(digit1)
        
        # Calculate second verifier digit
        weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit2 = self._calculate_verifier_digit(base, weights)
        base.append(digit2)
        
        return ''.join(map(str, base))

    def generate_cpf(self) -> str:
        """Generate a valid CPF number."""
        # Generate first 9 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(9)]
        
        # Calculate first verifier digit
        weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        digit1 = self._calculate_verifier_digit(base, weights)
        base.append(digit1)
        
        # Calculate second verifier digit
        weights = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        digit2 = self._calculate_verifier_digit(base, weights)
        base.append(digit2)
        
        return ''.join(map(str, base))

    def generate_rg(self) -> str:
        """Generate a valid RG number."""
        # Generate 8 random digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(8)]
        
        # Calculate verifier digit
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        total = sum(d * w for d, w in zip(base, weights))
        remainder = total % 11
        digit = 'X' if remainder == 10 else str(remainder)
        
        return ''.join(map(str, base)) + digit

    def generate_pis(self) -> str:
        """Generate a valid PIS number."""
        # Generate first 10 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(10)]
        
        # Calculate verifier digit
        weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit = self._calculate_verifier_digit(base, weights)
        base.append(digit)
        
        return ''.join(map(str, base))
"""Brazilian document number generator."""
from typing import List


class DocumentSampler:
    """Class for generating various Brazilian documents."""
    
    def __init__(self):
        """Initialize the document sampler."""
        pass

    def _calculate_verifier_digit(self, digits: List[int], weights: List[int]) -> int:
        """Calculate verifier digit using provided weights."""
        total = sum(d * w for d, w in zip(digits, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    def generate_cei(self) -> str:
        """Generate a valid CEI number."""
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(10)]
        
        # Calculate first verifier digit
        weights = [7, 4, 1, 8, 5, 2, 1, 6, 3, 7]
        total = sum(d * w for d, w in zip(base, weights))
        remainder = total % 11
        if remainder == 0:
            remainder = 11
        digit = 11 - remainder
        
        base.append(digit)
        return ''.join(map(str, base))

    def generate_cnpj(self) -> str:
        """Generate a valid CNPJ number."""
        # Generate first 12 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(12)]
        
        # Calculate first verifier digit
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit1 = self._calculate_verifier_digit(base, weights)
        base.append(digit1)
        
        # Calculate second verifier digit
        weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit2 = self._calculate_verifier_digit(base, weights)
        base.append(digit2)
        
        return ''.join(map(str, base))

    def generate_cpf(self) -> str:
        """Generate a valid CPF number."""
        # Generate first 9 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(9)]
        
        # Calculate first verifier digit
        weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        digit1 = self._calculate_verifier_digit(base, weights)
        base.append(digit1)
        
        # Calculate second verifier digit
        weights = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        digit2 = self._calculate_verifier_digit(base, weights)
        base.append(digit2)
        
        return ''.join(map(str, base))

    def generate_rg(self) -> str:
        """Generate a valid RG number."""
        # Generate 8 random digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(8)]
        
        # Calculate verifier digit
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        total = sum(d * w for d, w in zip(base, weights))
        remainder = total % 11
        digit = 'X' if remainder == 10 else str(remainder)
        
        return ''.join(map(str, base)) + digit

    def generate_pis(self) -> str:
        """Generate a valid PIS number."""
        # Generate first 10 digits
        base = [secrets.SystemRandom().randint(0, 9) for _ in range(10)]
        
        # Calculate verifier digit
        weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digit = self._calculate_verifier_digit(base, weights)
        base.append(digit)
        
        return ''.join(map(str, base))
