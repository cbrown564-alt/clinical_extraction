"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import CustomNode from "./CustomNode";
import { useArchitectStore } from "@/lib/stores";

const nodeTypes = { custom: CustomNode };

export default function PipelineCanvas() {
  const storeNodes = useArchitectStore((s) => s.nodes);
  const storeEdges = useArchitectStore((s) => s.edges);
  const updateNode = useArchitectStore((s) => s.updateNode);
  const setEdges = useArchitectStore((s) => s.setEdges);

  const initialNodes: Node[] = useMemo(
    () =>
      storeNodes.map((n) => ({
        id: n.id,
        type: "custom",
        position: { x: n.x, y: n.y },
        data: n as unknown as Record<string, unknown>,
        draggable: true,
      })),
    [storeNodes]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      storeEdges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: "#9ca3af", strokeWidth: 2 },
      })),
    [storeEdges]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdgesState, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (connection: Connection) => {
      const newEdge = addEdge(
        {
          ...connection,
          id: `e-${connection.source}-${connection.target}`,
          animated: true,
          style: { stroke: "#9ca3af", strokeWidth: 2 },
        } as Edge,
        edges
      );
      setEdgesState(newEdge);
      setEdges([
        ...storeEdges,
        { id: connection.source + "-" + connection.target, source: connection.source!, target: connection.target! },
      ]);
    },
    [edges, setEdgesState, setEdges, storeEdges]
  );

  const onNodeDragStop = useCallback(
    (_: unknown, node: { id: string; position: { x: number; y: number } }) => {
      updateNode(node.id, { x: node.position.x, y: node.position.y });
    },
    [updateNode]
  );

  return (
    <div className="flex-1 h-full bg-surface-raised/30">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={16} size={1} color="#e5e4e2" />
        <Controls className="!bg-surface !border-border !shadow-sm" />
        <MiniMap
          className="!bg-surface !border-border !shadow-sm"
          nodeColor={(node) => {
            const family = (node.data as { family?: string })?.family;
            if (family === "rules_only") return "#2a6f6f";
            if (family === "llm_only") return "#d97706";
            if (family === "hybrid") return "#7c3aed";
            return "#9ca3af";
          }}
          maskColor="rgba(250, 249, 247, 0.7)"
        />
      </ReactFlow>
    </div>
  );
}
