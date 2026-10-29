import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Pipe Marketplace", template: "%s · Pipe Marketplace" },
  description: "Surplus pipe, valves, fittings and flanges — bids, asks, delivered-price matching and a price index.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <nav className="topnav">
          <span className="brand">Pipe Marketplace</span>
          <Link href="/">Dashboard</Link>
          <Link href="/asks">Asks</Link>
          <Link href="/bids">Bids</Link>
          <Link href="/trades">Price History</Link>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
