import Providers from "../providers";

export default function ObservatoryLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <Providers>{children}</Providers>;
}
