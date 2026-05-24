"use client";

import { useEffect, useCallback, useState } from "react";
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from "reactflow";
interface DependencyGraphProps {
  affectedServices: string[];
}

const initialNodes: Node[] = [
  {
    id: "api-gateway",
    type: "default",
    data: { label: "API Gateway" },
    position: { x: 250, y: 50 },
    style: { background: "#1e1e3f", color: "#fff", border: "1px solid #00f3ff", borderRadius: "8px", padding: "10px" },
  },
  {
    id: "auth-service",
    type: "default",
    data: { label: "Auth Service" },
    position: { x: 100, y: 200 },
    style: { background: "#1e1e3f", color: "#fff", border: "1px solid #00f3ff", borderRadius: "8px", padding: "10px" },
  },
  {
    id: "payment-service",
    type: "default",
    data: { label: "Payment Service" },
    position: { x: 400, y: 200 },
    style: { background: "#1e1e3f", color: "#fff", border: "1px solid #00f3ff", borderRadius: "8px", padding: "10px" },
  },
  {
    id: "database",
    type: "default",
    data: { label: "Database" },
    position: { x: 150, y: 350 },
    style: { background: "#1e1e3f", color: "#fff", border: "1px solid #00f3ff", borderRadius: "8px", padding: "10px" },
  },
  {
    id: "redis-cache",
    type: "default",
    data: { label: "Redis Cache" },
    position: { x: 400, y: 350 },
    style: { background: "#1e1e3f", color: "#fff", border: "1px solid #00f3ff", borderRadius: "8px", padding: "10px" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "api-gateway", target: "auth-service", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
  { id: "e1-3", source: "api-gateway", target: "payment-service", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
  { id: "e2-4", source: "auth-service", target: "database", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
  { id: "e3-4", source: "payment-service", target: "database", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
  { id: "e2-5", source: "auth-service", target: "redis-cache", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
  { id: "e3-5", source: "payment-service", target: "redis-cache", markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: "#00f3ff" } },
];

export default function DependencyGraph({ affectedServices }: DependencyGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [highlighted, setHighlighted] = useState<string[]>([]);

  // Update node styles when affectedServices changes
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        const isAffected = affectedServices.includes(node.id);
        return {
          ...node,
          style: {
            ...node.style,
            border: isAffected ? "2px solid #ff3333" : "1px solid #00f3ff",
            boxShadow: isAffected ? "0 0 15px rgba(255, 51, 51, 0.6)" : "none",
            background: isAffected ? "#3f1e1e" : "#1e1e3f",
          },
        };
      })
    );

    // Also highlight edges connected to affected nodes
    setEdges((eds) =>
      eds.map((edge) => {
        const isSourceAffected = affectedServices.includes(edge.source);
        const isTargetAffected = affectedServices.includes(edge.target);
        const shouldHighlight = isSourceAffected || isTargetAffected;
        return {
          ...edge,
          style: {
            stroke: shouldHighlight ? "#ff3333" : "#00f3ff",
            strokeWidth: shouldHighlight ? 3 : 2,
          },
          animated: shouldHighlight,
        };
      })
    );
  }, [affectedServices, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div style={{ height: "400px", width: "100%" }} className="bg-black/30 rounded-lg">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        attributionPosition="bottom-right"
      >
        <Background color="#00f3ff" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
}