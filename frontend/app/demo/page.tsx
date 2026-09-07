import type { Metadata } from "next";
import VivaDemo from "@/components/demo/VivaDemo";

export const metadata: Metadata = { title: "Extract, then decide" };
export default function DemoPage() { return <VivaDemo />; }
