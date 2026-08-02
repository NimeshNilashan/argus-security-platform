import { ClerkProvider } from '@clerk/nextjs'
import { IBM_Plex_Sans, Geist_Mono } from "next/font/google";
import "./globals.css";

const ibmPlexSans = IBM_Plex_Sans({
  variable: "--font-ibm-plex-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "ARGUS",
  description: "Security Capstone project by Nilashan",
};

export default function RootLayout({ children }) {
  return (
      <html
          lang="en"
          className={`${ibmPlexSans.variable} ${geistMono.variable} h-full antialiased`}
      >
      <body className="min-h-full flex flex-col">
      <ClerkProvider
          afterSignInUrl="/dashboard"
          afterSignUpUrl="/dashboard"

      >
          <header />
          {children}
      </ClerkProvider>
      </body>
      </html>
  );
}