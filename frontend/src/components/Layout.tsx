import { type ReactNode } from "react";

type Props = {
  children: ReactNode;
};

const Layout = ({ children }: Props) => (
  <div className="min-h-screen bg-slate-50">
    <div className="max-w-6xl mx-auto px-6 py-6">
      <header className="border-b border-slate-200 pb-5 mb-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">
            ASC Scheduler
          </h1>
          <p className="text-slate-600">
            Track satellites, TLEs, and scheduled passes.
          </p>
        </div>
      </header>
      <main className="flex flex-col gap-4">{children}</main>
    </div>
  </div>
);

export default Layout;
