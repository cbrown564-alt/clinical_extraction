import Providers from "../providers";

export default function WorkbenchLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <Providers>{children}</Providers>;
}
