import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ML Lab | Understand your machine learning models",
  description: "An interactive machine-learning experimentation platform.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return <html lang="en"><body>{children}</body></html>;
}
