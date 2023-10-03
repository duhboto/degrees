import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    # Check if source or target are None and return None
    if source is None or target is None:
        return None

    if source == target:
        return []

    # Check for direct connection
    direct_movies = people[source]["movies"].intersection(people[target]["movies"])
    if direct_movies:
        return [(next(iter(direct_movies)), target)]

    # Initialize the frontier with the source node
    start_node = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start_node)
    
    explored = set()
    frontier_states = {source}  # Initialize with the source state

    num_explored = 0  # Initialize the counter

    while True:
        if frontier.empty():
            logging.info(f"Nodes explored: {num_explored}")
            return None

        node = frontier.remove()
        frontier_states.remove(node.state)  # Remove state from frontier_states
        num_explored += 1

        # Mark node as explored
        explored.add(node.state)

        # Directly retrieve and iterate over neighbors using dictionaries
        current_movies = people[node.state]["movies"]
        for movie_id in current_movies:
            stars_in_movie = movies[movie_id]["stars"]
            for person_id in stars_in_movie:
                if person_id != node.state:  # Avoid adding the current person as their own neighbor

                    # Check for the target state early
                    if person_id == target:
                        path = [(movie_id, person_id)]
                        while node.parent is not None:
                            path.append((node.action, node.state))
                            node = node.parent
                        path.reverse()
                        logging.info(f"Found solution after exploring {num_explored} nodes!")
                        return path

                    # Avoid adding the node to the frontier if it's already explored or in the frontier
                    if person_id not in explored and person_id not in frontier_states:
                        child = Node(state=person_id, parent=node, action=movie_id)
                        frontier.add(child)
                        explored.add(person_id)  # Mark the state as explored
                        frontier_states.add(person_id)  # Add state to frontier_states



def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
