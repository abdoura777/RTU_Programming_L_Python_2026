"""
Lab 2.1 – Simple Datasets and Aggregates
----------------------------------------
Practice lists, dictionaries and tuples by computing simple aggregates.

Write these functions:
- average(values)               -> float
    Average of a list of numbers. Return 0.0 if the list is empty.
- largest_city(populations)     -> tuple (name, population)
    The city with the LARGEST population.
- smallest_city(populations)    -> tuple (name, population)
    The city with the SMALLEST population.
- total_population(populations) -> int
    Sum of all populations. Return 0 if the dict is empty.

`populations` is a dictionary like {"Riga": 605000, "Daugavpils": 78000}.
For largest_city() and smallest_city():
- If two cities tie, return the one that comes FIRST in the dictionary.
- If the dictionary is empty, return ("", 0).
- Built-ins such as sum(), len(), max() and min() are allowed.
  Hint: max(populations, key=populations.get) gives the key with the
  largest value.

In the main block: create your OWN datasets (a list `temperatures` with
7 daily temperatures, and a dict `city_population` with at least 5 cities),
call the functions, and print the results. Print the average with
1 decimal place.

Example run (with your own data the numbers will differ):
    Average temperature: 4.3
    Largest city: Riga - 605000
    Smallest city: Valmiera - 23000
    Total population: 806000

Examples (these are also used to check your work):
>>> average([1, 2, 3, 4])
2.5
>>> average([])
0.0
>>> cities = {"Riga": 605000, "Daugavpils": 78000, "Liepaja": 67000}
>>> largest_city(cities)
('Riga', 605000)
>>> smallest_city(cities)
('Liepaja', 67000)
>>> total_population(cities)
750000
>>> largest_city({})
('', 0)
>>> largest_city({"A": 10, "B": 10})
('A', 10)
"""


def average(values: list[float]) -> float:
    """Return the average of values, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def largest_city(populations: dict[str, int]) -> tuple[str, int]:
    """Return (city, population) for the city with the largest population."""
    if not populations:
        return ("", 0)
    # max() avec key=populations.get sélectionne la clé avec la plus grande valeur.
    # Pour respecter l'ordre d'insertion en cas d'égalité, on peut inverser l'ordre des clés ou utiliser une astuce,
    # mais l'indice de cours suggère d'utiliser max(populations, key=populations.get).
    # Pour gérer proprement les égalités (prendre la première), on peut parcourir ou utiliser max avec une clé inversée si besoin,
    # mais max() en Python préserve déjà le premier trouvé si on fait attention, ou bien :
    largest = max(populations, key=populations.get)
    return (largest, populations[largest])


def smallest_city(populations: dict[str, int]) -> tuple[str, int]:
    """Return (city, population) for the city with the smallest population."""
    if not populations:
        return ("", 0)
    smallest = min(populations, key=populations.get)
    return (smallest, populations[smallest])


def total_population(populations: dict[str, int]) -> int:
    """Return the sum of all populations."""
    if not populations:
        return 0
    return sum(populations.values())


def total_population(populations: dict[str, int]) -> int:
    """Return the sum of all populations."""
    # TODO: implement
    raise NotImplementedError("total_population() is not implemented yet")


if __name__ == "__main__":
    # Keep all input() and print() calls inside this block, otherwise the
    # autograder cannot import your file.

    # TODO: Create your own datasets - up to you to fill in the data
    temperatures = [2.5, 3.1, 4.0, 5.2, 6.1, 4.8, 4.3]
    city_population = {
        "Riga": 605000,
        "Daugavpils": 78000,
        "Liepaja": 67000,
        "Jelgava": 55000,
        "Valmiera": 23000
    }

    # TODO: call the functions above and print the results
    avg_temp = average(temperatures)
    lg_city = largest_city(city_population)
    sm_city = smallest_city(city_population)
    tot_pop = total_population(city_population)

    print(f"Average temperature: {avg_temp:.1f}")
    print(f"Largest city: {lg_city[0]} - {lg_city[1]}")
    print(f"Smallest city: {sm_city[0]} - {sm_city[1]}")
    print(f"Total population: {tot_pop}")
