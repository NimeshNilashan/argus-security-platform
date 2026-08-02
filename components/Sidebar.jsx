"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
    { label: "OSINT", href: "/osint" },
    { label: "Port Scanner", href: "/port-scanner" },
    { label: "File Integrity", href: "/file-integrity" },
    { label: "Log Analyzer", href: "/log-analyzer" },
    { label: "AI Assistant", href: "/ai-assistant" },
    { label: "Profile", href: "/profile" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="flex w-56 shrink-0 flex-col border-r border-white/10">
            <div className="border-b border-white/10 px-5 py-5">
                <span className="font-mono text-lg font-semibold tracking-tight">ARGUS</span>
            </div>
            <nav className="flex-1 py-4">
                {NAV_ITEMS.map((item) => {
                    const active = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={
                                "flex w-full items-center gap-3 border-l-2 px-5 py-2.5 font-mono text-xs uppercase tracking-wide transition focus:outline-none focus-visible:bg-white/5 " +
                                (active
                                    ? "border-cyan-400 text-white"
                                    : "border-transparent text-gray-500 hover:border-white/20 hover:text-gray-300")
                            }
                        >
                            {item.label}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}