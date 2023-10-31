import osmium


class MyHandler(osmium.SimpleHandler):
    def __init__(self, output_file):
        super().__init__()
        self.output_file = output_file
        self.glacier_nodes = []

    def node(self, n):
        if 'natural' in n.tags and n.tags['natural'] == 'glacier':
            self.glacier_nodes.append(n)

    def write_to_osm(self):
        writer = osmium.SimpleWriter(self.output_file)
        for node in self.glacier_nodes:
            writer.add_node(node)
        writer.close()


# Load your planet.osm.pbf file
osm_file = "../Download/planet.osm.pbf"
output_osm_file = "../Download/output_glacier.osm"

handler = MyHandler(output_osm_file)
reader = osmium.SimpleReader(osm_file)
reader.apply(handler)

# Write the glacier nodes to the output OSM file
handler.write_to_osm()
print(f"Glacier data written to {output_osm_file}")
