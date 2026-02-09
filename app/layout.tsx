import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Six Nations Fantasy Team - Gameweek 1",
  description: "Optimal XV Selection for Six Nations Fantasy Rugby",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
