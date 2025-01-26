import json
import random


class BrazilianPopulationSampler:
    def __init__(self, json_file_path: str):
        """
        Initialize the sampler with population data from a JSON file.

        Args:
            json_file_path (str): Path to the JSON file containing population data
        """
        with open(json_file_path, encoding='utf-8') as file:
            self.data = json.load(file)

        # Pre-calculate weights for more efficient sampling
        self._calculate_weights()

    def _calculate_weights(self) -> None:
        """
        Pre-calculate weights for states and cities based on population percentages.
        Stores the results in instance variables for reuse.
        """
        # Calculate state weights
        self.state_weights = []
        self.state_names = []

        for state_name, state_data in self.data['states'].items():
            self.state_names.append(state_name)
            self.state_weights.append(state_data['population_percentage'])

        # Normalize state weights to sum to 1
        total_weight = sum(self.state_weights)
        self.state_weights = [w / total_weight for w in self.state_weights]

        # Calculate city weights per state
        self.city_weights_by_state = {}
        self.city_names_by_state = {}

        for city_name, city_data in self.data['cities'].items():
            state = city_data['city_uf']

            if state not in self.city_weights_by_state:
                self.city_weights_by_state[state] = []
                self.city_names_by_state[state] = []

            self.city_names_by_state[state].append(city_name)
            self.city_weights_by_state[state].append(city_data['population_percentage_state'])

        # Normalize city weights within each state
        for state in self.city_weights_by_state:
            total = sum(self.city_weights_by_state[state])
            if total > 0:  # Avoid division by zero
                self.city_weights_by_state[state] = [w / total for w in self.city_weights_by_state[state]]

    def get_state(self) -> tuple[str, str]:
        """
        Get a random state weighted by population percentage.

        Returns:
            Tuple[str, str]: A tuple containing (state_name, state_abbreviation)
        """
        state_name = random.choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str = None) -> tuple[str, str]:
        """
        Get a random city weighted by population percentage.
        If state_abbr is provided, returns a city from that state.
        If state_abbr is None, first selects a random state, then a city from it.

        Args:
            state_abbr (str, optional): State abbreviation to get city from

        Returns:
            Tuple[str, str]: A tuple containing (city_name, state_abbreviation)
        """
        if state_abbr is None:
            _, state_abbr = self.get_state()

        if state_abbr not in self.city_weights_by_state:
            raise ValueError(f'No cities found for state: {state_abbr}')

        city_name = random.choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

        return city_name, state_abbr

    def get_state_and_city(self) -> tuple[str, str, str]:
        """
        Get a random state and city combination weighted by population percentage.

        Returns:
            Tuple[str, str, str]: A tuple containing (state_name, state_abbreviation, city_name)
        """
        state_name, state_abbr = self.get_state()
        city_name, _ = self.get_city(state_abbr)
        return state_name, state_abbr, city_name


def main():
    """
    Example usage of the BrazilianPopulationSampler class.
    """
    # Initialize the sampler
    sampler = BrazilianPopulationSampler('population_data_2024.json')

    # Example: Get random state
    state_name, state_abbr = sampler.get_state()
    print(f'\nRandom State: {state_name} ({state_abbr})')

    # Example: Get random city from specific state
    city_name, city_state = sampler.get_city(state_abbr)
    print(f'Random City from {state_abbr}: {city_name}')

    # Example: Get random city from random state
    city_name, city_state = sampler.get_city()
    print(f'Random City from Random State: {city_name} ({city_state})')

    # Example: Get random state and city combination
    state_name, state_abbr, city_name = sampler.get_state_and_city()
    print(f'Random State and City: {city_name}, {state_name} ({state_abbr})')


if __name__ == '__main__':
    main()
