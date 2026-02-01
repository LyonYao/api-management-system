package com.company.apimgmt.dto;

import org.eclipse.microprofile.openapi.annotations.media.Schema;

import java.util.List;

@Schema(description = "Topology graph data representing systems, APIs, and their relationships")
public class TopologyDTO {
    @Schema(description = "List of nodes in the topology graph (systems and APIs)")
    public List<NodeDTO> nodes;
    
    @Schema(description = "List of edges in the topology graph (call relationships)")
    public List<EdgeDTO> edges;

    public TopologyDTO() {
    }

    public TopologyDTO(List<NodeDTO> nodes, List<EdgeDTO> edges) {
        this.nodes = nodes;
        this.edges = edges;
    }
}
