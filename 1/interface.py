from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, end_nodes):
        with self._driver.session() as session:
            default_output = [{'path': []}]
            
            try:
                # Convert single node to list format
                targets = [end_nodes] if isinstance(end_nodes, int) else list(end_nodes)
                
                # Validate node existence
                node_validation = session.run(
                    """
                    UNWIND $node_list AS loc_id
                    MATCH (n:Location {name: loc_id})
                    RETURN count(n) AS found_nodes
                    """, {"node_list": [start_node] + targets}
                ).single()["found_nodes"]
                
                if node_validation != len(targets) + 1:
                    return default_output
                
                # Manage graph projection
                session.run("CALL gds.graph.drop('bfs_temp_graph', false)")
                
                session.run(
                    """
                    CALL gds.graph.project(
                        'bfs_temp_graph',
                        'Location',
                        'TRIP',
                        {nodeProperties: ['name']}
                    )
                    """
                )
                
                # Get internal node IDs
                node_identifiers = session.run(
                    """
                    UNWIND $node_list AS loc
                    MATCH (n:Location {name: loc})
                    RETURN collect(id(n)) AS node_ids
                    """, {"node_list": [start_node] + targets}
                ).single()
                
                if not node_identifiers or len(node_identifiers["node_ids"]) != len(targets) + 1:
                    return default_output
                    
                origin_id = node_identifiers["node_ids"][0]
                destination_ids = node_identifiers["node_ids"][1:]
                
                # Execute BFS algorithm
                path_result = session.run(
                    """
                    CALL gds.bfs.stream(
                        'bfs_temp_graph',
                        {
                            sourceNode: $origin,
                            targetNodes: $targets,
                            maxDepth: 1000
                        }
                    )
                    YIELD path
                    RETURN [node IN nodes(path) | {name: node.name}] AS route
                    LIMIT 1
                    """, {
                        "origin": origin_id,
                        "targets": destination_ids
                    }
                )
                
                path_data = path_result.single()
                if path_data and path_data["route"]:
                    return [{'path': path_data["route"]}]
                
                return default_output
                
            except Exception as e:
                print(f"BFS Operation Failed: {str(e)}")
                return default_output
            finally:
                try:
                    session.run("CALL gds.graph.drop('bfs_temp_graph', false)")
                except Exception as cleanup_error:
                    print(f"Graph Cleanup Issue: {str(cleanup_error)}")

    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            # Create graph projection
            session.run("""
                CALL gds.graph.project(
                    'pagerank_graph',
                    'Location',
                    {
                        TRIP: {
                            type: 'TRIP',
                            orientation: 'NATURAL',
                            properties: [$weight_prop]
                        }
                    },
                    {
                        nodeProperties: ['name']
                    }
                )
                """, {"weight_prop": weight_property})
            
            try:
                # Run PageRank 
                result = session.run("""
                    CALL gds.pageRank.stream('pagerank_graph', {
                        maxIterations: $iterations,
                        dampingFactor: 0.85,
                        relationshipWeightProperty: $weight_prop
                    })
                    YIELD nodeId, score
                    RETURN gds.util.asNode(nodeId).name AS name, score
                    ORDER BY score DESC
                    """, {
                        "iterations": max_iterations,
                        "weight_prop": weight_property
                    })
                node = [{'name': record['name'], 'score': record['score']} for record in result]
                # Return formatted results
                return (node[0], node[-1])
                
            finally:
                session.run("CALL gds.graph.drop('pagerank_graph')")