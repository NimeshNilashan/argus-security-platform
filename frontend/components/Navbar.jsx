export default function Navbar({ title = "Welcome back, Nimesh" }) {
    return (
        <div className="mb-10 flex items-center justify-between">
            <h1 className="text-xl font-semibold">{title}</h1>
            <span className="flex items-center gap-1.5 rounded border border-white/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-gray-500">
        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 motion-safe:animate-pulse" />
        system nominal
      </span>
        </div>
    );
}