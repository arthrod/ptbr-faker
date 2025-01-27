# Brazilian Name and Location Sampler (ptbr-faker)

A Python CLI tool for generating realistic Brazilian names and locations based on demographic data.

## Features

- Generate random Brazilian names based on historical frequency data
- Generate random Brazilian locations weighted by population
- Generate valid postal codes (CEP) for locations
- Multiple output formats and customization options
- Command-line interface with rich formatting

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ptbr-faker.git
cd ptbr-faker

# Install dependencies
pip install -e .
```

## Usage

Basic usage:

```bash
# Generate 5 random Brazilian names with locations
python -m src.cli.commands sample -q 5

# Generate only names
python -m src.cli.commands sample -q 3 -n

# Generate only locations with CEP
python -m src.cli.commands sample -q 3 --only-cep

# Generate names from a specific time period
python -m src.cli.commands sample -q 3 -t ate1950
```

For all available options:
```bash
python -m src.cli.commands sample --help
```

## Project Structure

```
src/
├── cli/                 # CLI-related modules
│   ├── commands.py     # CLI commands implementation
│   ├── formatting.py   # Output formatting utilities
│   └── options.py      # CLI options definitions
├── samplers/           # Core sampling functionality
│   ├── location.py     # Location sampling implementation
│   └── name.py        # Name sampling implementation
└── utils/             # Utility modules
    └── time_period.py # Time period definitions
```

## Data Sources

The project uses demographic data from:
- Brazilian census data for name frequencies
- IBGE population data for location weighting
- Official postal code (CEP) ranges

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
