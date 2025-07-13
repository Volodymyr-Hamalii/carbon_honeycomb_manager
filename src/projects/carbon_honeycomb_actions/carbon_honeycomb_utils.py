import numpy as np
# from collections import defaultdict
from scipy.spatial.distance import cdist


from src.services import Constants, DistanceMeasurer


class CarbonHoneycombUtils:

    @staticmethod
    def find_end_points(
        points_on_line: np.ndarray,
        coordinates_to_check: tuple[str, str] = ("x", "y"),
    ) -> tuple[tuple, tuple]:
        if len(points_on_line) == 0:
            raise ValueError("No points provided to CarbonHoneycombUtils.find_end_points")

        first_point: np.ndarray = points_on_line[0]

        index_0: int = Constants.math.COORDINATE_INDEX_MAP[coordinates_to_check[0]]
        index_1: int = Constants.math.COORDINATE_INDEX_MAP[coordinates_to_check[1]]

        start: np.ndarray = first_point
        end: np.ndarray = start

        for point in points_on_line[1:]:  # skip the first point
            c1, c2 = point[index_0], point[index_1]  # first and second coordinates
            s_c1, s_c2 = start[index_0], start[index_1]  # first and second coordinates of the start
            e_c1, e_c2 = end[index_0], end[index_1]  # first and second coordinates of the end

            if c1 == s_c1 and c1 == e_c1:
                if c2 < s_c2:
                    start = point
                elif c2 > e_c2:
                    end = point
            elif c1 < s_c1:
                start = point
            elif c1 > e_c1:
                end = point

        return tuple(start), tuple(end)

    @classmethod
    def find_end_points_of_honeycomb_planes_groups(
        cls, honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], np.ndarray]]
    ) -> list[tuple[tuple[np.float32, np.float32], tuple[np.float32, np.float32]]]:
        """
        Returns the coordinates of the ends of the segments
        on the xOy plane that form the channel planes.

        Keep the same index order as in honeycomb_planes_groups.
        """

        end_points_of_groups: list[tuple[tuple[np.float32, np.float32], tuple[np.float32, np.float32]]] = []

        for group in honeycomb_planes_groups:
            keys: np.ndarray = np.array(list(group.keys()))
            start, end = cls.find_end_points(points_on_line=keys)
            end_points_of_groups.append((start, end))

        # return sorted(end_points_of_groups, key=lambda p: p[0][0])
        return end_points_of_groups

    @staticmethod
    def found_polygon_node_indexes(
        extreme_points_of_groups: list[tuple[tuple, tuple]],
        num_of_nodes: int = 6,  # hexagon
    ) -> list[list[int]]:
        """ Fount the lines that form polygons and returns the list of indexes of such groups. """

        # Step 1: Extract all unique nodes (points) and map them to integer indices
        # Collect all points
        points_set = set()
        for i, (p1, p2) in enumerate(extreme_points_of_groups):
            points_set.add(p1)
            points_set.add(p2)
        points_list = list(points_set)
        point_to_index = {p: idx for idx, p in enumerate(points_list)}

        # Step 2: Build adjacency list from edges
        n = len(points_list)
        adjacency = [[] for _ in range(n)]
        for i, (p1, p2) in enumerate(extreme_points_of_groups):
            u = point_to_index[p1]
            v = point_to_index[p2]
            adjacency[u].append((v, i))  # store (node, edge_index)
            adjacency[v].append((u, i))  # undirected

        # Step 3: Find all num_of_nodes-cycles
        # A brute force backtracking approach:
        polygons = set()  # use a set to avoid duplicates, will store tuple of sorted edges

        num_of_edges: int = num_of_nodes + 1

        def backtrack(start_node, current_node, visited_nodes, visited_edges) -> None:
            # If we have a path of length num_of_nodes, check if it forms a cycle back to start_node
            if len(visited_nodes) == num_of_edges:
                # Check if last node connects to start_node
                if visited_nodes[-1] == start_node:
                    # We found a num_of_nodes-cycle
                    # visited_edges has the edge indices in the order they were visited
                    cycle_edges = tuple(sorted(visited_edges))
                    polygons.add(cycle_edges)
                return

            if len(visited_nodes) > num_of_edges:
                return  # longer than needed

            # Explore neighbors
            for (nxt, eidx) in adjacency[current_node]:
                # We must not revisit nodes to ensure a simple cycle, except possibly to close the cycle
                if nxt == start_node and len(visited_nodes) == num_of_nodes:
                    # Can we close the cycle with start_node?
                    # This adds one more edge, completing a num_of_nodes-cycle
                    new_visited_edges = visited_edges + [eidx]
                    cycle_edges = tuple(sorted(new_visited_edges))
                    polygons.add(cycle_edges)
                elif nxt not in visited_nodes:
                    # Continue path
                    # Add node and edge
                    backtrack(start_node, nxt, visited_nodes + [nxt], visited_edges + [eidx])

        # Try starting from each node and find num_of_nodes-cycles
        # To avoid recounting the same cycle multiple times starting from different nodes,
        # we can impose an order: start from a specific node and only proceed to neighbors with greater index, etc.
        # However, using the set of sorted edges as a key will eliminate duplicates anyway.
        for start in range(n):
            backtrack(start, start, [start], [])

        # Step 4: Convert the set of cycles back into lists of edges
        # Each element in polygons is a tuple of edge indices sorted.
        # If needed, we can return them as lists in sorted order.
        result: list[list[int]] = [list(cycle) for cycle in polygons]

       # Remove duplicates by converting each list to a frozenset
        unique_cycles = {frozenset(cycle) for cycle in result}

        # Convert each frozenset back to a list
        result = [list(cycle) for cycle in unique_cycles]

        return result

    @staticmethod
    def split_xy_groups_by_max_distances(
        groups_by_the_xy_lines: list[dict[tuple[np.float32, np.float32], np.ndarray]],
        max_distance_between_xy_groups: np.floating | float,
    ) -> list[dict[tuple[np.float32, np.float32], np.ndarray]]:
        """
        Takes groups_by_the_xy_lines and split the group into separate
        if there are some groups with the min distances more than max_distance_between_xy_groups.
        """
        result: list[dict[tuple[np.float32, np.float32], np.ndarray]] = []

        for line_dict in groups_by_the_xy_lines:
            # Sort keys (usually by x then y)
            keys: list[tuple[np.floating, np.floating]] = sorted(
                line_dict.keys(), key=lambda p: (float(p[0]), float(p[1])))

            clusters = []
            current_cluster: list[tuple[np.floating, np.floating]] = [keys[0]]

            # Build clusters based on max distance
            for i in range(1, len(keys)):
                dist: float = DistanceMeasurer.calculate_distance_between_2_points(keys[i - 1], keys[i])
                if dist <= max_distance_between_xy_groups:
                    # Same cluster
                    current_cluster.append(keys[i])
                else:
                    # New cluster starts here
                    clusters.append(current_cluster)
                    current_cluster = [keys[i]]

            # Append the last cluster if not empty
            if current_cluster:
                clusters.append(current_cluster)

            # Filter out clusters that have only one point
            filtered_clusters = [c for c in clusters if len(c) > 1]

            # Convert each cluster back to a dict
            for cluster in filtered_clusters:
                cluster_dict = {k: line_dict[k] for k in cluster}
                result.append(cluster_dict)

        return result

    @staticmethod
    def split_groups_by_max_distances(
        points_grouped_by_lines: list[np.ndarray],
        max_distance_between_xy_groups: np.floating | float,
    ) -> list[np.ndarray]:
        """
        Takes a list of np.ndarray (each representing a set of points that lie on a line),
        and splits each set into smaller clusters if the distance between consecutive points
        exceeds max_distance_between_xy_groups.

        Params:
        points_grouped_by_lines - A list of np.ndarrays. Each ndarray is assumed
                                  to be shape (N, D) (commonly (N,2) or (N,3)).
        max_distance_between_xy_groups - The maximum allowed distance between consecutive points in a cluster.

        Returns a list of np.ndarrays, each containing a cluster of points.
        """
        result: list[np.ndarray] = []

        for line_points in points_grouped_by_lines:
            # Ensure line_points is a NumPy array
            line_points = np.array(line_points, dtype=float)
            n = line_points.shape[0]
            if n == 0:
                continue

            # Calculate pairwise distance matrix
            dist_matrix = cdist(line_points, line_points)

            # Keep track of whether a point is already clustered
            used = np.zeros(n, dtype=bool)

            clusters = []
            for i in range(n):
                if used[i]:
                    # Point i is already assigned to a cluster
                    continue

                # Check if point i has any neighbor within the threshold
                # (excluding itself, obviously)
                close_points_idx = np.where(dist_matrix[i] <= max_distance_between_xy_groups)[0]
                # Exclude self
                close_points_idx = close_points_idx[close_points_idx != i]

                if len(close_points_idx) == 0:
                    # No neighbor within threshold => make a new cluster for i alone
                    cluster_array = line_points[[i], :]
                    used[i] = True
                    clusters.append(cluster_array)
                else:
                    # There's at least one neighbor => Start a cluster with i and its neighbors
                    # We then expand to include neighbors-of-neighbors if they are also close
                    # (depending on desired logic—here let's do a BFS/DFS approach to gather
                    # all connected points under the threshold).
                    cluster_indices = set()
                    queue = [i]
                    while queue:
                        current = queue.pop()
                        if current in cluster_indices:
                            continue
                        cluster_indices.add(current)
                        used[current] = True
                        # Check all points that are within threshold of current
                        neighbors = np.where(dist_matrix[current] <= max_distance_between_xy_groups)[0]
                        # Exclude self
                        neighbors = neighbors[neighbors != current]
                        for neigh in neighbors:
                            if not used[neigh]:
                                queue.append(neigh)

                    # Build cluster from those indices
                    cluster_array = line_points[list(cluster_indices), :]
                    clusters.append(cluster_array)

            clusters = [c for c in clusters if c.shape[0] > 1]

            result.extend(clusters)

        return result
