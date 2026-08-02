import { UserButton, useUser } from '@clerk/nextjs'

const NAV_ITEMS = [
    "OSINT",
    "Port Scanner",
    "File Integrity",
    "Log Analyzer",
    "AI Assistant",
    <UserButton />,
];

const STATS = [
    { label: "Findings", value: 18, accent: "border-cyan-400/40" },
    { label: "High Risk", value: 3, accent: "border-red-400" },
    { label: "Scans", value: 27, accent: "border-cyan-400/40" },
    { label: "Files", value: 8, accent: "border-cyan-400/40" },
];

const SEVERITY_STYLE = {
    HIGH: "text-red-400",
    MEDIUM: "text-amber-400",
    LOW: "text-cyan-400/70",
};

const FINDINGS = [
    { severity: "HIGH", text: "File modified", time: "2 min ago" },
    { severity: "HIGH", text: "SSH brute force", time: "10 min ago" },
    { severity: "MEDIUM", text: "Port 22 open", time: "25 min ago" },
    { severity: "LOW", text: "New subdomain", time: "1 hour ago" },
];

const ACTIVITY = [
    "OSINT scan completed",
    "Port scan completed",
    "Log analysis completed",
    "File integrity verified",
];

export default function Dashboard() {
    return (
        <div className="flex min-h-screen bg-black text-white">
            {/* Background grid texture — same as the landing page, keeps the two screens feeling like one product */}
            <div
                className="pointer-events-none fixed inset-0 opacity-5"
                style={{
                    backgroundImage:
                        "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
                    backgroundSize: "56px 56px",
                }}
            />

            {/* Sidebar */}
            <aside className="flex w-56 shrink-0 flex-col border-r border-white/10">
                <div className="border-b border-white/10 px-5 py-5">
                    <span className="font-mono text-lg font-semibold tracking-tight">ARGUS</span>

                </div>
                <nav className="flex-1 py-4">
                    {NAV_ITEMS.map((item) => {
                        const active = item === "Dashboard";
                        return (
                            <button
                                key={item}
                                className={
                                    "flex w-full items-center gap-3 border-l-2 px-5 py-2.5 text-left font-mono text-xs uppercase tracking-wide transition focus:outline-none focus-visible:bg-white/5 " +
                                    (active
                                        ? "border-cyan-400 text-white"
                                        : "border-transparent text-gray-500 hover:border-white/20 hover:text-gray-300")
                                }
                            >
                                {item}
                            </button>
                        );
                    })}
                </nav>
            </aside>

            {/* Main content */}
            <main className="flex-1 px-8 py-8">
                {/* Top bar */}
                <div className="mb-10 flex items-center justify-between">
                    <h1 className="text-xl font-semibold">Welcome back, Nimesh</h1>
                    <span className="flex items-center gap-1.5 rounded border border-white/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-gray-500">
          </span>
                </div>

                {/* Stats */}
                <section className="mb-12">
                    <h2 className="mt-2 text-lg font-semibold">Security overview</h2>

                    <div className="mt-6 grid gap-px overflow-hidden rounded border border-white/10 bg-white/10 sm:grid-cols-4">
                        {STATS.map((stat) => (
                            <div key={stat.label} className={"border-l-2 bg-black px-6 py-5 " + stat.accent}>
                                <p className="font-mono text-xs uppercase tracking-wide text-gray-500">{stat.label}</p>
                                <p className="mt-2 font-mono text-3xl font-semibold">{stat.value}</p>
                            </div>
                        ))}
                    </div>
                </section>

                <div className="grid gap-12 lg:grid-cols-[1.4fr_1fr]">
                    {/* Recent findings */}
                    <section>
                        <h2 className="mt-2 text-lg font-semibold">Recent findings</h2>

                        <div className="mt-5 divide-y divide-white/10 rounded border border-white/10">
                            {FINDINGS.map((f, i) => (
                                <div key={i} className="flex items-center justify-between px-5 py-3.5">
                                    <div className="flex items-center gap-4">
                    <span className={"w-16 shrink-0 font-mono text-xs font-semibold " + SEVERITY_STYLE[f.severity]}>
                      {f.severity}
                    </span>
                                        <span className="text-sm text-gray-200">{f.text}</span>
                                    </div>
                                    <span className="font-mono text-xs text-gray-600">{f.time}</span>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Recent activity */}
                    <section>
                        <h2 className="mt-2 text-lg font-semibold">Recent activity</h2>

                        <div className="mt-5 rounded border border-white/10">
                            {ACTIVITY.map((a, i) => (
                                <div
                                    key={i}
                                    className="flex items-center gap-3 border-b border-white/10 px-5 py-3.5 font-mono text-sm text-gray-300 last:border-b-0"
                                >
                                    <span className="text-cyan-400">✓</span>
                                    {a}
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
}